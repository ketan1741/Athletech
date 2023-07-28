import serial
from datetime import datetime
from pynput import keyboard

def on_esc_pressed(key):
    if key == keyboard.Key.esc:
        return False

# Define the serial port and baud rate (make sure to match the one in your Arduino sketch)
ser_env = serial.Serial('/dev/cu.usbmodem11302', 9600)
ser_imu = serial.Serial('/dev/cu.usbmodem11202', 57600)
# Open a text file for writing the data
file_path_env = 'env_data.txt'
file_path_imu = 'imu_data.txt'

try_read = False
read = False
try:
    with keyboard.Listener(on_press = on_esc_pressed) as listener:
        with open(file_path_env, 'w') as f_env:
            with open(file_path_imu, 'w') as f_imu:
                print("Logging Data!")
                while True:
                    if not try_read:
                        print("Trying to Read Serial Env...")
                        try_read = True
                    data_e = ser_env.readline().decode().strip()  
                    if not read:
                        print("Serial Read!")
                        read = True
                    data_i = ser_imu.readline().decode().strip()  
                    # print(data_i)  # Print the received data
                    f_env.write(datetime.now().strftime("%H:%M:%S.%f") + ',')
                    f_imu.write(datetime.now().strftime("%H:%M:%S.%f") + ',')
                    f_env.write(data_e + '\n')
                    f_imu.write(data_i + '\n')
                    if not listener.running:
                        break
except KeyboardInterrupt:
    # Clean up and exit gracefully when 'CTRL + C' is pressed
    pass
