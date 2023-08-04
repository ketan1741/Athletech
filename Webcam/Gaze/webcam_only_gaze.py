import csv
import cv2
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from gaze_tracking import GazeTracking
from datetime import datetime

gaze = GazeTracking()
webcam = cv2.VideoCapture(0)
# Print out actual FPS
actual_fps = webcam.get(cv2.CAP_PROP_FPS)
print("Actual FPS of the camera:", actual_fps)
# Open the CSV files for writing
gaze_csv_file = open("gaze_analysis/gaze_data.csv", "w", newline="")
gaze_csv_writer = csv.writer(gaze_csv_file)
gaze_csv_writer.writerow(["Timestamp", "Left Pupil", "Right Pupil"])

eye_centers = []
eye_center_window_size = 1  # Adjust the window size as needed for smoothing
try:
    print("Turning webcam on!")
    
    while True:
        ret, frame = webcam.read()

        if not ret:
            print("Can't receive new frame, exiting...")
            break

        # frame_1 = cv2.flip(frame, 1)
        gaze.refresh(frame)
        left_pupil = gaze.pupil_left_coords()
        right_pupil = gaze.pupil_right_coords()

        if left_pupil is not None and right_pupil is not None:
            eye_center = ((left_pupil[0] + right_pupil[0]) // 2, (left_pupil[1] + right_pupil[1]) // 2)
            eye_centers.append(eye_center)

            # Apply moving average to eye_center data
            if len(eye_centers) > eye_center_window_size:
                smoothed_eye_center = np.mean(eye_centers[-eye_center_window_size:], axis=0)
            else:
                smoothed_eye_center = eye_center

        # Get current timestamp
        edt_timestamp = datetime.now()
        timestamp = edt_timestamp.strftime('%H:%M:%S.%f')
        # Write gaze data to the CSV file
        gaze_csv_writer.writerow([timestamp, left_pupil, right_pupil])

        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == 27: # ord('esc'):
            break

finally:
    print("Turning webcam off!")
    webcam.release()
    cv2.destroyAllWindows()
    gaze_csv_file.close()

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
