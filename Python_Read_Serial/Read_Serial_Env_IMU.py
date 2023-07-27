import keyboard
import serial
import datetime

ESC_Pressed = False

def on_esc_pressed(event):
    global ESC_Pressed
    ESC_Pressed = True

# Register the 'ESC' key press event and call the on_esc_pressed() function
keyboard.on_press_key("esc", on_esc_pressed)

current_time = str(datetime.datetime.now())
# Define the serial port and baud rate (make sure to match the one in your Arduino sketch)
ser = serial.Serial('COM6', 9600)
ser2 = serial.Serial('COM9', 57600)
# Open a text file for writing the data
file_path = 'env_data.txt'
file_path2 = 'imu_data.txt'

try:
    with open(file_path, 'w') as file:
        with open(file_path2, 'w') as file2:
            print("Current time:", current_time)
            file.write(current_time + '\n')
            file2.write(current_time + '\n')
            while True:
                data = ser.readline().decode().strip()  
                data2 = ser2.readline().decode().strip()  
                print(data2)  # Print the received data
                file.write(data + '\n')
                file2.write(data2 + '\n')
                if ESC_Pressed:
                    break
except KeyboardInterrupt:
    # Clean up and exit gracefully when 'CTRL + C' is pressed
    pass
