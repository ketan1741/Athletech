import cv2
import mediapipe as mp
import matplotlib.pyplot as plt
import csv
import time
from datetime import datetime

# Create a MediaPipe Pose object
mp_pose = mp.solutions.pose

video_capture = cv2.VideoCapture(1)
frame_rate = video_capture.get(cv2.CAP_PROP_FPS)
print(f"Frame rate: {frame_rate} fps")

# Initialize previous landmark positions
prev_landmarks = None

# Create lists to store the differences in landmark positions
diff_x_list = []
diff_y_list = []

# Threshold to filter out erroneous differences
threshold = 0.0005  # Adjust this value as needed

# Create a CSV file to store the data
csv_file = "posture_changes.csv"
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "X Coordinate Difference", "Y Coordinate Difference"])

    with mp_pose.Pose() as pose:
        while True:
            ret, frame = video_capture.read()
            if not ret:
                print("Error reading frame from video stream")
                break

            # Convert the frame to RGB format
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process the frame with MediaPipe Pose
            results = pose.process(frame_rgb)

            # Extract landmarks from the current frame
            landmarks = []
            if results.pose_landmarks:
                for landmark in results.pose_landmarks.landmark:
                    landmarks.append((landmark.x, landmark.y, landmark.z))

            # Compare with previous frame
            if prev_landmarks and landmarks:
                if len(landmarks) >= 2:
                    diff_x = landmarks[0][0] - prev_landmarks[0][0]
                    diff_y = landmarks[1][1] - prev_landmarks[1][1]
                    if abs(diff_x) > threshold and abs(diff_y) > threshold:
                        diff_x_list.append(diff_x)
                        diff_y_list.append(diff_y)

                        # Get current timestamp in UTC timezone
                        edt_timestamp = datetime.now()

                        # Format the EDT timestamp as a string with the desired format
                        edt_timestamp_str = edt_timestamp.strftime('%H:%M:%S.%f')

                        # Store the data in the CSV file
                        writer.writerow([edt_timestamp_str, diff_x, diff_y])

            # Update the previous landmarks
            prev_landmarks = landmarks

            # Visualize the pose landmarks on the frame
            if results.pose_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(
                    frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS
                )

            cv2.imshow('Video', frame)

            if cv2.waitKey(1) & 0xFF == 27: #ord('esc'):
                break

video_capture.release()
cv2.destroyAllWindows()

# Plot the changes in the posture
frame_count = len(diff_x_list)
x = range(frame_count)
duration_seconds = frame_count / frame_rate
print(f"Duration: {duration_seconds} seconds")

fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)

ax1.plot(x, diff_x_list, label='X Coordinate Difference')
ax1.set_ylabel('X Coordinate Difference')

ax2.plot(x, diff_y_list, label='Y Coordinate Difference')
ax2.set_ylabel('Y Coordinate Difference')
ax2.set_xlabel('Frame')

plt.suptitle('Changes in Posture over Frames')
plt.show()
