#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>
#include <SPI.h>
#include <WiFiNINA.h>
#include <ArduinoMqttClient.h>
#include <FlashStorage_SAMD.h>
#include <ArduinoBLE.h>
#include <Arduino_APDS9960.h>

/* Flash Memory variables */
FlashStorage(seat_id, long)
FlashStorage(back_id, long)
FlashStorage(seat_calib, adafruit_bno055_offsets_t)
FlashStorage(back_calib, adafruit_bno055_offsets_t)

/* Network variables */
#include "arduino_secrets.h"
char ssid[] = SECRET_SSID;
char pass[] = SECRET_PASS;

WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);

const char broker[] = MQTT_BROKER;
int port = 1883;
const char topic1[] = "seat";
const char topic2[] = "back";

//How often to send a message
const long interval = 1000;
unsigned long previousMillis = 0;

int count = 0;

/* This driver reads raw data from the BNO055

   Connections
   ===========
   Connect SCL to analog 5
   Connect SDA to analog 4
   Connect VDD to 3.3V DC
   Connect GROUND to common ground
   Connect ADDR to 3.3V DC

   History
   =======
   2015/MAR/03  - First release (KTOWN)
*/

/* Set the delay between fresh samples */
#define BNO055_SAMPLERATE_DELAY_MS (100)

// Check I2C device address and correct line below (by default address is 0x29 or 0x28)
//                                      id, address
// Since we are using multiplexer, can just set them all to same address
Adafruit_BNO055 seat = Adafruit_BNO055(1, 0x29, &Wire);
Adafruit_BNO055 back = Adafruit_BNO055(2, 0x28, &Wire);

/*
 * Display sensor offset data for Accelerometer and Gyroscope
 */
void displaySensorOffsets(const adafruit_bno055_offsets_t &calibData)
{
    Serial.print("Accel: ");
    Serial.print(calibData.accel_offset_x); Serial.print(" ");
    Serial.print(calibData.accel_offset_y); Serial.print(" ");
    Serial.print(calibData.accel_offset_z); Serial.print(" ");

    Serial.print("\nGyro: ");
    Serial.print(calibData.gyro_offset_x); Serial.print(" ");
    Serial.print(calibData.gyro_offset_y); Serial.print(" ");
    Serial.print(calibData.gyro_offset_z); Serial.print(" ");

    Serial.print("\nAccel Radius: ");
    Serial.println(calibData.accel_radius);
}

void printWifiData() {
  IPAddress ip = WiFi.localIP();
  byte mac[6];
  Serial.print("IP Address: ");
  Serial.println(ip);

  WiFi.macAddress(mac);
  Serial.print("MAC: ");
  Serial.print(mac[5],HEX);
  Serial.print(":");
  Serial.print(mac[4],HEX);
  Serial.print(":");
  Serial.print(mac[3],HEX);
  Serial.print(":");
  Serial.print(mac[2],HEX);
  Serial.print(":");
  Serial.print(mac[1],HEX);
  Serial.print(":");
  Serial.println(mac[0],HEX);
}

void printCurrentNet() {
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());
  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.println(rssi);
  byte encryption = WiFi.encryptionType();
  Serial.print("Encryption Type:");
  Serial.println(encryption, HEX);
  Serial.println();
}

/**************************************************************************/
/*
    Arduino setup function (automatically called at startup)
*/
/**************************************************************************/
void setup(void)
{
  Serial.begin(9600);

  while (!Serial) delay(10);  // wait for serial port to open!

  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("No Wifi!");
    while(true);
  }

  String fv = WiFi.firmwareVersion();

  if (fv < WIFI_FIRMWARE_LATEST_VERSION) {
    Serial.println("Old firmware, update!");
  }

  Serial.print("Attempting to connect to WPA SSID: ");
  Serial.println(ssid);
  while (WiFi.begin(ssid, pass) != WL_CONNECTED) {
    Serial.print(".");
    delay(5000);
  }
  Serial.println("You're connected to the network ");
  printCurrentNet();
  printWifiData();
  
  Serial.println("Attempting to connect to MQTT broker: ");
  Serial.println(broker);

  mqttClient.setUsernamePassword("aws_server", "esports_data");

  if(!mqttClient.connect(broker, port)) {
    Serial.print("MQTT connection failed! Error code: ");
    Serial.println(mqttClient.connectError());
    while(1);
  }

  Serial.println("Connected to MQTT broker!");

  Wire.begin();

  /* Initialise the 1st left sensor */
  //Set it into IMUPLUS mode, since we only need Accelerometer and Gyroscope
  if(!seat.begin(OPERATION_MODE_IMUPLUS))
  {
    /* There was a problem detecting the BNO055 ... check your connections */
    Serial.println("No seat!");
    while(1);
  }

  /* Initialise the 1st right sensor */
  //Set it into IMUPLUS mode, since we only need Accelerometer and Gyroscope
  if(!back.begin(OPERATION_MODE_IMUPLUS))
  {
    /* There was a problem detecting the BNO055 ... check your connections */
    Serial.println("No back!");
    while(1);
  }

  /* Try to use Flash to load and store IMU calibration data */
  sensor_t s_seat;
  sensor_t s_back;
  long bno_ID_s;
  long bno_ID_b;
  bool is_calib_s = false;
  bool is_calib_b = false;
  bool new_calib_s = false;
  bool new_calib_b = false;

  seat_id.read(bno_ID_s);
  back_id.read(bno_ID_b);

  /*
   * Look in Flash for sensor IDs
   */
  seat.getSensor(&s_seat);

  if (bno_ID_s != s_seat.sensor_id)
  {
    Serial.println("No seat data!");
    delay(500);
  }
  else {
    //Offset from start of EEPROM to find sensor l1 calibration
    adafruit_bno055_offsets_t cal_data_s;
    seat_calib.read(cal_data_s);
    seat.setSensorOffsets(cal_data_s);
    is_calib_s = true;
  }

  delay(50);
  seat.setExtCrystalUse(true);

  back.getSensor(&s_back);

  if (bno_ID_b != s_back.sensor_id)
  {
    Serial.println("No back data!");
    delay(500);
  }
  else {
    //Offset from start of EEPROM to find sensor r1 calibration
    adafruit_bno055_offsets_t cal_data_b;
    back_calib.read(cal_data_b);
    back.setSensorOffsets(cal_data_b);
    is_calib_b = true;
  }

  delay(50);
  back.setExtCrystalUse(true);

  //Calibrate the sensors if calibration data isn't found
  if (!is_calib_s){
    new_calib_s = true;
    Serial.println("Calibrating seat...");
    delay(5000);
    uint8_t system, gyro, accel, mag = 0;
    while (!seat.isFullyCalibrated()) {
      /* Display calibration status for each sensor. */
      seat.getCalibration(&system, &gyro, &accel, &mag);
      Serial.print("CALIBRATION: Gyro=");
      Serial.print(gyro, DEC);
      Serial.print(" Accel=");
      Serial.println(accel, DEC);

      delay(BNO055_SAMPLERATE_DELAY_MS);
    }

    Serial.println();
    Serial.println("seat calibrated!");
    Serial.println();
    delay(500);
  }

  if (!is_calib_b){
    new_calib_b = true;
    Serial.println("Calibrating back...");
    delay(5000);
    uint8_t system, gyro, accel, mag = 0;
    while (!back.isFullyCalibrated()) {
      /* Display calibration status for each sensor. */
      back.getCalibration(&system, &gyro, &accel, &mag);
      Serial.print("CALIBRATION: Gyro=");
      Serial.print(gyro, DEC);
      Serial.print(" Accel=");
      Serial.println(accel, DEC);

      delay(BNO055_SAMPLERATE_DELAY_MS);
    }

    Serial.println();
    Serial.println("back calibrated!");
    Serial.println();
    delay(500);
  }

  // Serial.println();
  // Serial.println("All calibrated!");
  // Serial.println();

  /*
   * If new calibration was made, store into EEPROM
   * If no new calibration, then skip to reduce writing to EEPROM
   */
  if (new_calib_s) {
    Serial.println("Storing seat...");

    //Store sensor ID after r3
    seat_id.write(s_seat.sensor_id);

    //Store calibration data at offset from start of EEPROM
    adafruit_bno055_offsets_t new_cal_data_s;
    seat.getSensorOffsets(new_cal_data_s);
    seat_calib.write(new_cal_data_s);

    Serial.println();
    Serial.println("seat stored!");
    Serial.println();
  }

  if (new_calib_b) {
    Serial.println("Storing back...");

    //Store sensor ID after r3
    back_id.write(s_back.sensor_id);

    //Store calibration data at offset from start of EEPROM
    adafruit_bno055_offsets_t new_cal_data_b;
    back.getSensorOffsets(new_cal_data_b);
    back_calib.write(new_cal_data_b);

    Serial.println();
    Serial.println("back stored!");
    Serial.println();
  }

  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH);
}

/**************************************************************************/
/*
    Arduino loop function, called once 'setup' is complete (your own code
    should go here)
*/
/**************************************************************************/
void loop(void)
{


  // // Possible vector values can be:
  // // - VECTOR_ACCELEROMETER - m/s^2
  // // - VECTOR_MAGNETOMETER  - uT
  // // - VECTOR_GYROSCOPE     - rad/s
  // // - VECTOR_EULER         - degrees
  // // - VECTOR_LINEARACCEL   - m/s^2
  // // - VECTOR_GRAVITY       - m/s^2
  imu::Vector<3> gyro_s = seat.getVector(Adafruit_BNO055::VECTOR_GYROSCOPE);
  imu::Vector<3> accel_s = seat.getVector(Adafruit_BNO055::VECTOR_LINEARACCEL);

  imu::Vector<3> gyro_b = back.getVector(Adafruit_BNO055::VECTOR_GYROSCOPE);
  imu::Vector<3> accel_b = back.getVector(Adafruit_BNO055::VECTOR_LINEARACCEL);

  //Prepare data to send to server
  String data_s = String(gyro_s.x()) + "," + String(gyro_s.y()) + "," + String(gyro_s.z()) + "," + String(accel_s.x()) + "," + String(accel_s.y()) + "," + String(accel_s.z());
  String data_b = String(gyro_b.x()) + "," + String(gyro_b.y()) + "," + String(gyro_b.z()) + "," + String(accel_b.x()) + "," + String(accel_b.y()) + "," + String(accel_b.z());

  mqttClient.poll();

  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    Serial.print("Sending message to topic: ");
    Serial.println(topic1);
    Serial.println(data_s);

    mqttClient.beginMessage(topic1);
    mqttClient.print(data_s);
    mqttClient.endMessage();

    Serial.print("Sending message to topic: ");
    Serial.println(topic2);
    Serial.println(data_b);

    mqttClient.beginMessage(topic2);
    mqttClient.print(data_b);
    mqttClient.endMessage();
  }
  delay(200);
}
