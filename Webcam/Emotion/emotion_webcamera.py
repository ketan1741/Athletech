import cv2
import time
from fer import FER
import matplotlib.pyplot as plt
import numpy as np

# Function to capture image from webcam and perform emotion detection
def detect_emotion_from_webcam():
    # Create an emotion detector object
    emotion_detector = FER()

    # Access the webcam
    webcam = cv2.VideoCapture(0)  # 0 represents the default camera (you can change it to other camera indices if needed)
    angry = []
    disgust = []
    fear = []
    happy = []
    sad = []
    surprise = []
    neutral = []
    try:
        print("Turning on webcam!")
    # Loop to capture images and detect emotions every one second
        while True:
            # Capture a frame from the webcam
            ret, frame = webcam.read()

            # Check if the frame was captured successfully
            if not ret:
                print("Failed to capture frame from webcam")
                break

            # Perform emotion detection on the captured frame
            emotions = emotion_detector.detect_emotions(frame)

            if emotions:
                # Output emotions for the current frame
                print(emotions[0]["emotions"])
                angry.append(emotions[0]["emotions"]["angry"])
                disgust.append(emotions[0]["emotions"]["disgust"])
                fear.append(emotions[0]["emotions"]["fear"])
                happy.append(emotions[0]["emotions"]["happy"])
                sad.append(emotions[0]["emotions"]["sad"])
                surprise.append(emotions[0]["emotions"]["surprise"])
                neutral.append(emotions[0]["emotions"]["neutral"])
            else:
                angry.append(0)
                disgust.append(0)
                fear.append(0)
                happy.append(0)
                sad.append(0)
                surprise.append(0)
                neutral.append(0)

            # Wait for one second before capturing the next frame
            time.sleep(1)
    except KeyboardInterrupt:
        print("Turning off webcam!")
        # Release the webcam
        webcam.release()

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

if __name__ == "__main__":
    detect_emotion_from_webcam()
