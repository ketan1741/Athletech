import obswebsocket
from obswebsocket import obsws, requests, events, exceptions
import time


time.sleep(2)

# Replace these with your actual OBS WebSocket server settings
websocket_host = "localhost"
websocket_port = 4444
websocket_password = ""  # Set to empty string if you didn't set a password

# Connect to the OBS Studio WebSocket server
ws = obswebsocket.obsws(websocket_host, websocket_port, websocket_password)

try:
    ws.connect()  # Connect to OBS Studio

    # Start the OBS Studio recording (You can change this to other actions, e.g., "StartStreaming")
    response = ws.call(requests.StartRecording())

    if response.status:
        print("Recording started successfully.")
    else:
        print("Failed to start recording:", response.error)
except exceptions.ConnectionFailure:
    print("Failed to connect to OBS Studio WebSocket server.")
finally:
    ws.disconnect()  # Disconnect from OBS Studio