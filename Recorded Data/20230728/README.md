# Data Acquisition Process:
1. Open the EEG, turn on streaming, then wait for it to connect, and then visualize it.
   - Make sure no hair is blocking the sensors, they should have direct contact with skin.
3. Put the 6 IMUs on the player.
   - L1: Left Wrist, L2: Left Forearm, L3: Left Shoulder. Same for the right side.
4. Run the `button.py` file.
5. Click the "start logger", "start posture", "start camera" buttons.
6. Start a match of CSGO, wait for the match to begin.
7. Click "start OCR", wait 3 seconds, then in OBS, click "Start Streaming".
8. Start recording the EEG data, and also start recording the Arduino data (IMU/Environmental) by running `Arduino_Serial_Logger.py` on separate laptops.
9. Wait for the terminal to print "process ends". This indicates the OCR is finished.
   - **Do not use Ctrl+C in the terminal to end this before it prints "process ends" or the OCR data will not save!**
10. Press `Ctrl+C` in the terminal running EEG data collection to stop it.
11. Press `esc` in the terminal running Arduino data collection to stop it.
12. Press `esc` on main PC to close webcam recording, this will also end keyboard and mouse logging.
13. Close the button GUI.
