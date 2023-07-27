import serial

arduino_port = "/dev/cu.usbmodem11302"
baud = 57600

ser = serial.Serial(arduino_port, baud)
# Open a text file for writing the data
file_path = 'IMUdata.txt'

try:
    with open(file_path, 'w') as file:
        while True:
            data = ser.readline().decode().strip()  # Read a line of data from the serial port and decode it
            print(data)  # Print the received data
            file.write(data + '\n')  # Write the data to the text file
except KeyboardInterrupt:
    ser.close()  # Close the serial port on Ctrl+C