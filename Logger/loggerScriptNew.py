import pyautogui
from pynput import mouse, keyboard
import csv
import datetime
import threading

print("Start this process")

# Specify the filename for the CSV file
csv_filename = "activity_log.csv"

# Initialize the list to store the activity data
activity_data = []

# Global flag
exit_flag = False

# Lock for synchronization
write_lock = threading.Lock()

try:
    with write_lock:
        with open(csv_filename, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Mouse Position", "Input", "Type"])
        print("Data exported successfully to", csv_filename)
except Exception as e:
    print("An error occurred while exporting the data:", str(e))


# Function to write the data to the CSV file
def write_to_csv(data):
    try:
        with write_lock:
            with open(csv_filename, 'a', newline='') as file:
                writer = csv.writer(file)
                # writer.writerow(["Timestamp", "Mouse Position", "Input", "Type"])
                writer.writerows(data)
            print("Data exported successfully to", csv_filename)
    except Exception as e:
        print("An error occurred while exporting the data:", str(e))


# Function to handle keyboard input
def on_key_press(key):
    global exit_flag

    # If 'Esc' key is pressed stop listener
    if key == keyboard.Key.esc:
        exit_flag = True
        # Write the activity_data to CSV before breaking
        write_to_csv(activity_data)
        return False

    try:
        # Get the current timestamp
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S.%f")[:23]

        # Get the current mouse position
        mouse_position = pyautogui.position()

        # Get the current key input
        key_input = str(key)

        # Append the activity data to the list
        activity_data.append([timestamp, mouse_position, key_input, "Key Press"])

        # Write the activity_data to CSV after each key press
        write_to_csv(activity_data)

        # Clear activity_data to avoid duplicates in CSV
        activity_data.clear()

    except AttributeError:
        pass


# Function to handle mouse click
def on_click(x, y, button, pressed):
    try:
        # Get the current timestamp
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S.%f")[:23]

        # Get the current mouse position
        mouse_position = pyautogui.position()

        # Get the current mouse click
        mouse_click = str(button)

        # Append the activity data to the list
        activity_data.append([timestamp, mouse_position, mouse_click, "Mouse Click"])

        # Write the activity_data to CSV after each mouse click
        write_to_csv(activity_data)

        # Clear activity_data to avoid duplicates in CSV
        activity_data.clear()

    except AttributeError:
        pass


# Create a keyboard listener
keyboard_listener = keyboard.Listener(on_press=on_key_press)

# Create a mouse listener
mouse_listener = mouse.Listener(on_click=on_click)

# Start the listeners
keyboard_listener.start()
mouse_listener.start()

# Record the activities until 'Esc' key is pressed
try:
    while not exit_flag:
        pass
except KeyboardInterrupt:
    pass

# Stop the listeners
keyboard_listener.stop()
mouse_listener.stop()
