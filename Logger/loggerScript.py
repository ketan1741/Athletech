import pyautogui
from pynput import mouse, keyboard
import csv
import datetime
import time

print("Start this process")

# Specify the filename for the CSV file
csv_filename = "activity_log.csv"

# Initialize the list to store the activity data
activity_data = []

# Global flag
exit_flag = False

# Function to handle keyboard input
def on_key_press(key):
    global exit_flag

    # If 'Esc' key is pressed stop listener
    if key == keyboard.Key.esc:
        exit_flag = True
        return False

    try:
        # Get the current timestamp
        # timestamp = datetime.datetime.now()

        timestamp = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S.%f")[:23]

        # Get the current mouse position
        mouse_position = pyautogui.position()

        # Get the current key input
        key_input = str(key)

        # Append the activity data to the list
        activity_data.append([timestamp, mouse_position, key_input, "Key Press"])

    except AttributeError:
        pass

# Function to handle mouse click
def on_click(x, y, button, pressed):
    # Get the current timestamp
    #timestamp = datetime.datetime.now()

    timestamp = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S.%f")[:23]

    # Get the current mouse position
    mouse_position = pyautogui.position()

    # Get the current mouse click
    mouse_click = str(button)

    # Append the activity data to the list
    activity_data.append([timestamp, mouse_position, mouse_click, "Mouse Click"])


# Create a keyboard listener
keyboard_listener = keyboard.Listener(on_press=on_key_press)

# Create a mouse listener
mouse_listener = mouse.Listener(on_click=on_click)

# Start the listeners
keyboard_listener.start()
mouse_listener.start()

# Record the activities until 'Esc' key is pressed
while True:
    time.sleep(1)
    # Check if 'Esc' key is pressed
    if exit_flag:
        break

# Stop the listeners
keyboard_listener.stop()
mouse_listener.stop()

# Export the activity data to a CSV file
try:
    with open(csv_filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Mouse Position", "Input", "Type"])
        writer.writerows(activity_data)
    print("Data exported successfully to", csv_filename)
except Exception as e:
    print("An error occurred while exporting the data:", str(e))

