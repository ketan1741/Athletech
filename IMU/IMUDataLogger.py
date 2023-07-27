import serial
from datetime import datetime
from pynput import keyboard

arduino_port = "/dev/cu.usbmodem11302"
baud = 57600

ser = serial.Serial(arduino_port, baud)
# Open a text file for writing the data
file_path = 'IMUdata.txt'

def stop(key):
    if key == keyboard.Key.esc:
        return False

with keyboard.Listener(on_press = stop) as listener:
    with open(file_path, 'w') as file:
        file.write(datetime.now().strftime("%H:%M:%S.%f") + '\n')
        while True:
            data = ser.readline().decode().strip()  # Read a line of data from the serial port and decode it
            print(data)  # Print the received data
            file.write(data + '\n')  # Write the data to the text file
            if not listener.running:
                break

ser.close()  # Close the serial port on Ctrl+C
