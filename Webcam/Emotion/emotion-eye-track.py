import csv
import cv2
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from gaze_tracking import GazeTracking
from fer import FER

detector = FER(mtcnn=True)
gaze = GazeTracking()
webcam = cv2.VideoCapture(0)

# Open the CSV file for writing
csv_file = open("gaze_data.csv", "w", newline="")
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["Frame", "Gaze Direction", "Left Pupil", "Right Pupil"])

eye_centers = []

# CS:GO captured graph resolution
graph_width = 1920
graph_height = 1080
angry = []
disgust = []
fear = []
happy = []
sad = []
surprise = []
neutral = []
try:
    print("Turning webcam on!")
    # while True:
    #     ret, frame = webcam.read()
    #     gaze.refresh(frame)
    #     left_pupil = gaze.pupil_left_coords()
    #     right_pupil = gaze.pupil_right_coords()

    #     if left_pupil is not None and right_pupil is not None:
    #         eye_center = ((left_pupil[0] + right_pupil[0]) // 2, (left_pupil[1] + right_pupil[1]) // 2)
    #         eye_centers.append(eye_center)
    #         cv2.putText(frame, "Left pupil:  " + str(left_pupil) , (90, 130), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
    #         cv2.putText(frame, "Right pupil: " + str(right_pupil) , (90, 165), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
    #         cv2.putText(frame, "o " , (320, 240), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
    #         cv2.imshow("Demo", frame)
    #     if cv2.waitKey(1) == ord('q'):
    #         break
    while True:
        # We get a new frame from the webcam
        ret, frame = webcam.read()

        if not ret:
            print("Can't receive new frame, exiting...")
            break
        # We send this frame to GazeTracking to analyze it
        gaze.refresh(frame)
        frame_1 = cv2.flip(frame, 1)
        # annotated_frame = gaze.annotated_frame()
        # text = ""

        # if gaze.is_right():
        #     text = "Looking right"
        # elif gaze.is_left():
        #     text = "Looking left"
        # elif gaze.is_center():
        #     text = "Looking center"

        left_pupil = gaze.pupil_left_coords()
        right_pupil = gaze.pupil_right_coords()

        if left_pupil is not None and right_pupil is not None:
            eye_center = ((left_pupil[0] + right_pupil[0]) // 2, (left_pupil[1] + right_pupil[1]) // 2)
            eye_centers.append(eye_center)

            # cv2.putText(annotated_frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)
            # cv2.putText(annotated_frame, "Left pupil:  " + str(left_pupil), (90, 130), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
            # cv2.putText(annotated_frame, "Right pupil: " + str(right_pupil), (90, 165), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)

        #cv2.imshow("Demo", annotated_frame)

        # Write gaze data to the CSV file
        csv_writer.writerow([len(eye_centers), left_pupil, right_pupil])

        #if cv2.waitKey(1) == ord('q'):
        #    break
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
except:
    print("Turning webcam off!")
    webcam.release()
    pass
x = np.linspace(0, len(happy), num=len(happy))
plt.plot(x, angry, label = "Angry", color='red')
plt.plot(x, disgust, label = "Disgust", color='yellow')
plt.plot(x, fear, label = "Fear", color='black')
plt.plot(x, happy, label = "Happy", color='green')
plt.plot(x, sad, label = "Sad", color='blue')
plt.plot(x, surprise, label = "Surprise", color='magenta')
plt.plot(x, neutral, label = "Neutral", color='gray')
plt.legend(loc='upper right')
plt.show()
# Release the resources
# webcam.release()
# cv2.destroyAllWindows()

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

    # Calculate the scaling factors
    x_scale = graph_width / (x_max - x_min)
    y_scale = graph_height / (y_max - y_min)

    # Load the CS:GO captured graph
    csgo_graph = cv2.imread("csgo.png")  # Replace "csgo.png" with the path to your CS:GO graph image
    csgo_graph = cv2.resize(csgo_graph, (graph_width, graph_height))

    # Overlay eye concentration markers on the CS:GO captured graph
    # scaled_eye_centers = ((X[:, 0] - x_min) * x_scale, (X[:, 1] - y_min) * y_scale)
    scaled_eye_centers = np.column_stack(((X[:, 0] - x_min) * x_scale, (X[:, 1] - y_min) * y_scale))

    for i in range(len(scaled_eye_centers)):
        x, y = scaled_eye_centers[i]
        cv2.circle(csgo_graph, (int(x), int(y)), 5, (0, 0, 255), -1)  # Red circle as eye concentration marker

    # Display the CS:GO captured graph with eye concentration markers
    cv2.imwrite("csgo_with_eye_concentration.png", csgo_graph)

# Close the CSV file
csv_file.close()
