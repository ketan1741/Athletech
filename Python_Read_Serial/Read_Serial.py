import serial
import datetime

current_time = str(datetime.datetime.now())
# Define the serial port and baud rate (make sure to match the one in your Arduino sketch)
ser = serial.Serial('COM6', 9600)  # Replace 'COMx' with the appropriate serial port (e.g., 'COM3' on Windows, '/dev/ttyUSB0' on Linux)

# Open a text file for writing the data
file_path = 'data.txt'

try:
    with open(file_path, 'w') as file:
        print("Current time:", current_time)
        file.write(current_time + '\n')
        while True:
            data = ser.readline().decode().strip()  # Read a line of data from the serial port and decode it
            print(data)  # Print the received data
            file.write(data + '\n')  # Write the data to the text file
except KeyboardInterrupt:
    ser.close()  # Close the serial port on Ctrl+C
