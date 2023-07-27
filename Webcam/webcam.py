import csv
import cv2
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from gaze_tracking import GazeTracking
from fer import FER
from datetime import datetime

detector = FER(mtcnn=True)
gaze = GazeTracking()
webcam = cv2.VideoCapture(0)

# Open the CSV files for writing
gaze_csv_file = open("gaze_data.csv", "w", newline="")
gaze_csv_writer = csv.writer(gaze_csv_file)
gaze_csv_writer.writerow(["Timestamp", "Left Pupil", "Right Pupil"])

emotion_csv_file = open("emotion_data.csv", "w", newline="")
emotion_csv_writer = csv.writer(emotion_csv_file)
emotion_csv_writer.writerow(["Timestamp", "Angry", "Disgust", "Fear", "Happy", "Sad", "Surprise", "Neutral"])

eye_centers = []
angry = []
disgust = []
fear = []
happy = []
sad = []
surprise = []
neutral = []

try:
    print("Turning webcam on!")
    
    while True:
        ret, frame = webcam.read()

        if not ret:
            print("Can't receive new frame, exiting...")
            break

        frame_1 = cv2.flip(frame, 1)
        gaze.refresh(frame)
        left_pupil = gaze.pupil_left_coords()
        right_pupil = gaze.pupil_right_coords()

        if left_pupil is not None and right_pupil is not None:
            eye_center = ((left_pupil[0] + right_pupil[0]) // 2, (left_pupil[1] + right_pupil[1]) // 2)
            eye_centers.append(eye_center)

        # Get current timestamp
        edt_timestamp = datetime.now()
        timestamp = edt_timestamp.strftime('%H:%M:%S.%f')
        # Write gaze data to the CSV file
        gaze_csv_writer.writerow([timestamp, left_pupil, right_pupil])

        # Write emotion data to the CSV file
        emotions = detector.detect_emotions(frame_1)
        if emotions:
            angry.append(emotions[0]['emotions']['angry'])
            disgust.append(emotions[0]['emotions']['disgust'])
            fear.append(emotions[0]['emotions']['fear'])
            happy.append(emotions[0]['emotions']['happy'])
            sad.append(emotions[0]['emotions']['sad'])
            surprise.append(emotions[0]['emotions']['surprise'])
            neutral.append(emotions[0]['emotions']['neutral'])
            
        else:
            angry.append(0)
            disgust.append(0)
            fear.append(0)
            happy.append(0)
            sad.append(0)
            surprise.append(0)
            neutral.append(0)
        emotion_csv_writer.writerow([timestamp, *angry[-1:], *disgust[-1:], *fear[-1:], *happy[-1:], *sad[-1:], *surprise[-1:], *neutral[-1:]])

        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == 27: #ord('esc'):
            break

finally:
    print("Turning webcam off!")
    webcam.release()
    cv2.destroyAllWindows()
    gaze_csv_file.close()
    emotion_csv_file.close()

# Perform clustering on eye centers
X = np.array(eye_centers)
if len(X) > 0:
    kmeans = KMeans(n_clusters=10)
    kmeans.fit(X)
    labels = kmeans.labels_
    centers = kmeans.cluster_centers_

    # Calculate the range of eye concentration data
    x_min, x_max = np.min(X[:, 0]), np.max(X[:, 0])
    y_min, y_max = np.min(X[:, 1]), np.max(X[:, 1])

    # CS:GO captured graph resolution
    graph_width = 1920
    graph_height = 1080

    # Calculate the scaling factors
    x_scale = graph_width / (x_max - x_min)
    y_scale = graph_height / (y_max - y_min)

    # Load the CS:GO captured graph
    csgo_graph = cv2.imread("csgo.png")  # Replace "csgo.png" with the path to your CS:GO graph image
    csgo_graph = cv2.resize(csgo_graph, (graph_width, graph_height))

    # Overlay eye concentration markers on the CS:GO captured graph
    scaled_eye_centers = np.column_stack(((X[:, 0] - x_min) * x_scale, (X[:, 1] - y_min) * y_scale))

    for i in range(len(scaled_eye_centers)):
        x, y = scaled_eye_centers[i]
        cv2.circle(csgo_graph, (int(x), int(y)), 5, (0, 0, 255), -1)  # Red circle as eye concentration marker

    # Display the CS:GO captured graph with eye concentration markers
    cv2.imwrite("csgo_with_eye_concentration.png", csgo_graph)

# Plot emotional data
x = np.linspace(0, len(happy), num=len(happy))
plt.plot(x, angry, label="Angry", color='red')
plt.plot(x, disgust, label="Disgust", color='yellow')
plt.plot(x, fear, label="Fear", color='black')
plt.plot(x, happy, label="Happy", color='green')
plt.plot(x, sad, label="Sad", color='blue')
plt.plot(x, surprise, label="Surprise", color='magenta')
plt.plot(x, neutral, label="Neutral", color='gray')
plt.legend(loc='upper right')
plt.show()
