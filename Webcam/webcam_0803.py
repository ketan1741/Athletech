import csv
import cv2
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from gaze_tracking import GazeTracking
from datetime import datetime
import time
from fer import FER

# Initialize gaze tracking and emotion analysis objects
gaze = GazeTracking()
detector = FER(mtcnn=True)

webcam = cv2.VideoCapture(0)

# Open the CSV files for writing
gaze_csv_file = open("gaze_analysis/gaze_data.csv", "w", newline="")
gaze_csv_writer = csv.writer(gaze_csv_file)
gaze_csv_writer.writerow(["Timestamp", "Left Pupil", "Right Pupil"])

emotion_csv_file = open("emotion_analysis/emotion_data.csv", "w", newline="")
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
        # Start timing for gaze tracking and emotion analysis
        start_time = time.time()

        ret, frame = webcam.read()

        if not ret:
            print("Can't receive new frame, exiting...")
            break

        # Perform gaze tracking
        gaze.refresh(frame)
        left_pupil = gaze.pupil_left_coords()
        right_pupil = gaze.pupil_right_coords()

        # Perform emotion analysis
        frame = cv2.flip(frame, 1)
        emotions = detector.detect_emotions(frame)

        # Get current timestamp
        timestamp = datetime.now()
        timestamp = timestamp.timestamp()
        #timestamp = edt_timestamp.strftime('%H:%M:%S.%f')

        if left_pupil is not None and right_pupil is not None:
            eye_center = ((left_pupil[0] + right_pupil[0]) / 2, (left_pupil[1] + right_pupil[1]) / 2)
            eye_centers.append(eye_center)


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

        # Write gaze data and emotion data to the CSV files
        gaze_csv_writer.writerow([timestamp, left_pupil, right_pupil])
        emotion_csv_writer.writerow([timestamp, *angry[-1:], *disgust[-1:], *fear[-1:], *happy[-1:], *sad[-1:], *surprise[-1:], *neutral[-1:]])

        # Calculate the elapsed time
        elapsed_time = time.time() - start_time

        # Add a time delay to achieve approximately 0.0015 seconds (adjust the value as needed)
        time.sleep(max(0, 0.0015 - elapsed_time))

        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == 27:
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
    kmeans = KMeans(n_clusters=9)
    kmeans.fit(X)
    labels = kmeans.labels_
    centers = kmeans.cluster_centers_

    plt.scatter(X[:, 0], X[:, 1], c=labels, cmap='viridis', alpha=0.5)
    plt.scatter(centers[:, 0], centers[:, 1], c='red', marker='X', s=200)
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title('Eye Center Clustering')
    plt.savefig('Eye_centers_clutering.png')
    plt.close()

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

y = np.linspace(0, len(happy), num=len(happy))
plt.plot(y, angry, label="Angry", color='red')
plt.plot(y, disgust, label="Disgust", color='yellow')
plt.plot(y, fear, label="Fear", color='black')
plt.plot(y, happy, label="Happy", color='green')
plt.plot(y, sad, label="Sad", color='blue')
plt.plot(y, surprise, label="Surprise", color='magenta')
plt.plot(y, neutral, label="Neutral", color='gray')
plt.legend(loc='upper right')
plt.show()
