# Instructions
## How to pass in secret SSID, password, and MQTT Broker in Arduino Code
1. In the same folder as the arduino code, create a new .h file, e.g. "arduino_secrets.h".
2. Within the .h file, define the following three variables:
   - `#define SECRET_SSID "your_ssid"`
   - `#define SECRET_PASS "ssid_pass"`
   - `#define MQTT_BROKER "mqtt_broker"`
## Change port of Arduino to Log Data
Make sure in Python files, change `arduino_port` to the ports that the Arduinos are plugged into.
