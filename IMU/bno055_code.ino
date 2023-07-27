#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>
#include <EEPROM.h>
#include <SPI.h>
#include <WiFiNINA.h>
#include <ArduinoMqttClient.h>

/* Network variables */
#include "arduino_secrets.h"
char ssid[] = SECRET_SSID;
char pass[] = SECRET_PASS;

WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);

const char broker[] = MQTT_BROKER;
int port = 8883;
const char topic1[] = "left_wrist (l1)";
const char topic2[] = "right_wrist (r1)";
const char topic3[] = "left_forearm (l2)";
const char topic4[] = "right_forearm (r2)";
const char topic5[] = "left_shoulder (l3)";
const char topic6[] = "right_shoulder (r3)";

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

/* Set up I2C multiplexer */
#define TCAADDR 0x70

// Check I2C device address and correct line below (by default address is 0x29 or 0x28)
//                                      id, address
// Since we are using multiplexer, can just set them all to same address
Adafruit_BNO055 bno_r1 = Adafruit_BNO055(1, 0x28, &Wire);
Adafruit_BNO055 bno_r2 = Adafruit_BNO055(2, 0x28, &Wire);
Adafruit_BNO055 bno_r3 = Adafruit_BNO055(3, 0x28, &Wire);

Adafruit_BNO055 bno_l1 = Adafruit_BNO055(4, 0x28, &Wire);
Adafruit_BNO055 bno_l2 = Adafruit_BNO055(5, 0x28, &Wire);
Adafruit_BNO055 bno_l3 = Adafruit_BNO055(6, 0x28, &Wire);

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

/*
 * Function to select which device on multiplexer
 */
void tcaselect(uint8_t i) {
  if (i > 7) return;
 
  Wire.beginTransmission(TCAADDR);
  Wire.write(1 << i);
  Wire.endTransmission();  
}

void printWifiData() {
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);
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
  Serial.begin(57600);

  while (!Serial) delay(10);  // wait for serial port to open!

  // Serial.println();
  // if (WiFi.status() == WL_NO_MODULE) {
  //   Serial.println("No Wifi!");
  //   while(true);
  // }

  // String fv = WiFi.firmwareVersion();

  // if (fv < WIFI_FIRMWARE_LATEST_VERSION) {
  //   Serial.println("Old firmware, update!");
  // }

  // Serial.print("Attempting to connect to WPA SSID: ");
  // Serial.println(ssid);
  // while (WiFi.begin(ssid, pass) != WL_CONNECTED) {
  //   Serial.print(".");
  //   delay(5000);
  // }
  // Serial.println("You're connected to the network ");
  // printCurrentNet();
  // printWifiData();
  
  // Serial.println("Attempting to connect to MQTT broker: ");
  // Serial.println(broker);

  // mqttClient.setUsernamePassword("aws_server", "esports_data");

  // if(!mqttClient.connect(broker, port)) {
  //   Serial.print("MQTT connection failed! Error code: ");
  //   Serial.println(mqttClient.connectError());
  //   while(1);
  // }

  // Serial.println("Connected to MQTT broker!");

  // Serial.println();
  // Serial.println("Wearable IMU System");
  // Serial.println();

  Wire.begin();

  /* Initialise the 1st left sensor */
  //Select the 1st left sensor
  tcaselect(2);
  //Set it into IMUPLUS mode, since we only need Accelerometer and Gyroscope
  if(!bno_l1.begin(OPERATION_MODE_IMUPLUS))
  {
    /* There was a problem detecting the BNO055 ... check your connections */
    Serial.println("No l1!");
    while(1);
  }

  /* Initialise the 1st right sensor */
  //Select the 1st right sensor
  tcaselect(3);
  //Set it into IMUPLUS mode, since we only need Accelerometer and Gyroscope
  if(!bno_r1.begin(OPERATION_MODE_IMUPLUS))
  {
    /* There was a problem detecting the BNO055 ... check your connections */
    Serial.println("No r1!");
    while(1);
  }

  /* Initialise the 2nd left sensor */
  //Select the 2nd left sensor
  tcaselect(4);
  //Set it into IMUPLUS mode, since we only need Accelerometer and Gyroscope
  if(!bno_l2.begin(OPERATION_MODE_IMUPLUS))
  {
    /* There was a problem detecting the BNO055 ... check your connections */
    Serial.println("No l2!");
    while(1);
  }

  /* Initialise the 2nd right sensor */
  //Select the 2nd right sensor
  tcaselect(5);
  //Set it into IMUPLUS mode, since we only need Accelerometer and Gyroscope
  if(!bno_r2.begin(OPERATION_MODE_IMUPLUS))
  {
    /* There was a problem detecting the BNO055 ... check your connections */
    Serial.print("No r2!");
    while(1);
  }
  
  /* Initialise the 3rd left sensor */
  //Select the 3rd left sensor
  tcaselect(6);
  //Set it into IMUPLUS mode, since we only need Accelerometer and Gyroscope
  if(!bno_l3.begin(OPERATION_MODE_IMUPLUS))
  {
    /* There was a problem detecting the BNO055 ... check your connections */
    Serial.println("No l3!");
    while(1);
  }

  /* Initialise the 3rd right sensor */
  //Select the 3rd right sensor
  tcaselect(7);
  //Set it into IMUPLUS mode, since we only need Accelerometer and Gyroscope
  if(!bno_r3.begin(OPERATION_MODE_IMUPLUS))
  {
    /* There was a problem detecting the BNO055 ... check your connections */
    Serial.print("No r3!");
    while(1);
  }

  /* Try to use EEPROM to load and store IMU calibration data */
  sensor_t s_r1;
  sensor_t s_r2;
  sensor_t s_r3;
  sensor_t s_l1;
  sensor_t s_l2;
  sensor_t s_l3;
  long bno_ID_r1;
  long bno_ID_r2;
  long bno_ID_r3;
  long bno_ID_l1;
  long bno_ID_l2;
  long bno_ID_l3;
  bool is_calib_r1 = false;
  bool is_calib_r2 = false;
  bool is_calib_r3 = false;
  bool is_calib_l1 = false;
  bool is_calib_l2 = false;
  bool is_calib_l3 = false;
  bool new_calib_r1 = false;
  bool new_calib_r2 = false;
  bool new_calib_r3 = false;
  bool new_calib_l1 = false;
  bool new_calib_l2 = false;
  bool new_calib_l3 = false;

  EEPROM.get(0, bno_ID_r1);
  EEPROM.get(sizeof(long) + sizeof(adafruit_bno055_offsets_t), bno_ID_r2);
  EEPROM.get(2*(sizeof(long) + sizeof(adafruit_bno055_offsets_t)), bno_ID_r3);
  EEPROM.get(3*(sizeof(long) + sizeof(adafruit_bno055_offsets_t)), bno_ID_l1);
  EEPROM.get(4*(sizeof(long) + sizeof(adafruit_bno055_offsets_t)), bno_ID_l2);
  EEPROM.get(5*(sizeof(long) + sizeof(adafruit_bno055_offsets_t)), bno_ID_l3);

  /*
   * Look in EEPROM for sensor IDs
   */
  tcaselect(2);
  bno_l1.getSensor(&s_l1);

  if (bno_ID_l1 != s_l1.sensor_id)
  {
    Serial.println("No l1 data!");
    delay(500);
  }
  else {
    // Serial.println("l1 data found!");

    //Offset from start of EEPROM to find sensor l1 calibration
    adafruit_bno055_offsets_t cal_data_l1;
    EEPROM.get(3*(sizeof(long) + sizeof(adafruit_bno055_offsets_t)) + sizeof(long), cal_data_l1);

    //Display stored value
    // displaySensorOffsets(cal_data_l1);

    //Set calibration data to sensor
    // Serial.println("Setting l1...");
    bno_l1.setSensorOffsets(cal_data_l1);
    is_calib_l1 = true;
  }

  delay(250);
  bno_l1.setExtCrystalUse(true);

  tcaselect(3);
  bno_r1.getSensor(&s_r1);

  if (bno_ID_r1 != s_r1.sensor_id)
  {
    Serial.println("No r1 data!");
    delay(500);
  }
  else {
    // Serial.println("r1 data found!");

    //Offset from start of EEPROM to find sensor r1 calibration
    adafruit_bno055_offsets_t cal_data_r1;
    EEPROM.get(sizeof(long), cal_data_r1);

    //Display stored value
    // displaySensorOffsets(cal_data_r1);

    //Set calibration data to sensor
    // Serial.println("Setting r1...");
    bno_r1.setSensorOffsets(cal_data_r1);
    is_calib_r1 = true;
  }

  delay(250);
  bno_r1.setExtCrystalUse(true);

  tcaselect(4);
  bno_l2.getSensor(&s_l2);

  if (bno_ID_l2 != s_l2.sensor_id)
  {
    Serial.println("No l2 data!");
    delay(500);
  }
  else {
    // Serial.println("l2 data found!");

    //Offset from start of EEPROM to find sensor l2 calibration
    adafruit_bno055_offsets_t cal_data_l2;
    EEPROM.get(4*(sizeof(long) + sizeof(adafruit_bno055_offsets_t)) + sizeof(long), cal_data_l2);

    //Display stored value
    // displaySensorOffsets(cal_data_l2);

    //Set calibration data to sensor
    // Serial.println("Setting l2...");
    bno_l2.setSensorOffsets(cal_data_l2);
    is_calib_l2 = true;
  }

  delay(250);
  bno_l2.setExtCrystalUse(true);

  tcaselect(5);
  bno_r2.getSensor(&s_r2);

  if (bno_ID_r2 != s_r2.sensor_id)
  {
    Serial.println("No r2 data!");
    delay(500);
  }
  else {
    // Serial.println("r2 data found!");

    //Offset from start of EEPROM to find sensor r2 calibration
    adafruit_bno055_offsets_t cal_data_r2;
    EEPROM.get(2*sizeof(long) + sizeof(adafruit_bno055_offsets_t), cal_data_r2);

    //Display stored value
    // displaySensorOffsets(cal_data_r2);

    //Set calibration data to sensor
    // Serial.println("Setting r2...");
    bno_r2.setSensorOffsets(cal_data_r2);
    is_calib_r2 = true;
  }

  delay(250);
  bno_r2.setExtCrystalUse(true);

  tcaselect(6);
  bno_l1.getSensor(&s_l3);

  if (bno_ID_l3 != s_l3.sensor_id)
  {
    Serial.println("No l3 data!");
    delay(500);
  }
  else {
    // Serial.println("l3 data found!");

    //Offset from start of EEPROM to find sensor l3 calibration
    adafruit_bno055_offsets_t cal_data_l3;
    EEPROM.get(5*(sizeof(long) + sizeof(adafruit_bno055_offsets_t)) + sizeof(long), cal_data_l3);

    //Display stored value
    // displaySensorOffsets(cal_data_l3);

    //Set calibration data to sensor
    // Serial.println("Setting l3...");
    bno_l3.setSensorOffsets(cal_data_l3);
    is_calib_l3 = true;
  }

  delay(250);
  bno_l3.setExtCrystalUse(true);

  tcaselect(7);
  bno_r3.getSensor(&s_r3);

  if (bno_ID_r3 != s_r3.sensor_id)
  {
    Serial.println("No r3 data!");
    delay(500);
  }
  else {
    // Serial.println("r3 data found!");

    //Offset from start of EEPROM to find sensor r3 calibration
    adafruit_bno055_offsets_t cal_data_r3;
    EEPROM.get(2*(sizeof(long) + sizeof(adafruit_bno055_offsets_t)) + sizeof(long), cal_data_r3);

    //Display stored value
    // displaySensorOffsets(cal_data_r3);

    //Set calibration data to sensor
    // Serial.println("Setting r3...");
    bno_r3.setSensorOffsets(cal_data_r3);
    is_calib_r3 = true;
  }

  delay(250);
  bno_r3.setExtCrystalUse(true);

  //Calibrate the sensors if calibration data isn't found
  if (!is_calib_l1){
    tcaselect(2);
    new_calib_l1 = true;
    Serial.println("Calibrating l1...");
    delay(5000);
    uint8_t system, gyro, accel, mag = 0;
    while (!bno_l1.isFullyCalibrated()) {
      /* Display calibration status for each sensor. */
      bno_l1.getCalibration(&system, &gyro, &accel, &mag);
      Serial.print("CALIBRATION: Gyro=");
      Serial.print(gyro, DEC);
      Serial.print(" Accel=");
      Serial.println(accel, DEC);

      delay(BNO055_SAMPLERATE_DELAY_MS);
    }

    Serial.println();
    Serial.println("l1 calibrated!");
    Serial.println();
    delay(500);
  }

  if (!is_calib_r1){
    tcaselect(3);
    new_calib_r1 = true;
    Serial.println("Calibrating r1...");
    delay(5000);
    uint8_t system, gyro, accel, mag = 0;
    while (!bno_r1.isFullyCalibrated()) {
      /* Display calibration status for each sensor. */
      bno_r1.getCalibration(&system, &gyro, &accel, &mag);
      Serial.print("CALIBRATION: Gyro=");
      Serial.print(gyro, DEC);
      Serial.print(" Accel=");
      Serial.println(accel, DEC);

      delay(BNO055_SAMPLERATE_DELAY_MS);
    }

    Serial.println();
    Serial.println("r1 calibrated!");
    Serial.println();
    delay(500);
  }

  if (!is_calib_l2){
    tcaselect(4);
    new_calib_l2 = true;
    Serial.println("Calibrating l2...");
    delay(5000);
    uint8_t system, gyro, accel, mag = 0;
    while (!bno_l2.isFullyCalibrated()) {
      /* Display calibration status for each sensor. */
      bno_l2.getCalibration(&system, &gyro, &accel, &mag);
      Serial.print("CALIBRATION: Gyro=");
      Serial.print(gyro, DEC);
      Serial.print(" Accel=");
      Serial.println(accel, DEC);

      delay(BNO055_SAMPLERATE_DELAY_MS);
    }

    Serial.println();
    Serial.println("l2 calibrated!");
    Serial.println();
    delay(500);
  }

  if (!is_calib_r2){
    tcaselect(5);
    new_calib_r2 = true;
    Serial.println("Calibrating r2...");
    delay(5000);
    uint8_t system, gyro, accel, mag = 0;
    while (!bno_r2.isFullyCalibrated()) {
      /* Display calibration status for each sensor. */
      bno_r2.getCalibration(&system, &gyro, &accel, &mag);
      Serial.print("CALIBRATION: Gyro=");
      Serial.print(gyro, DEC);
      Serial.print(" Accel=");
      Serial.println(accel, DEC);

      delay(BNO055_SAMPLERATE_DELAY_MS);
    }

    Serial.println();
    Serial.println("r2 calibrated!");
    Serial.println();
    delay(500);
  }

  if (!is_calib_l3){
    tcaselect(6);
    new_calib_l3 = true;
    Serial.println("Calibrating l3...");
    delay(5000);
    uint8_t system, gyro, accel, mag = 0;
    while (!bno_l3.isFullyCalibrated()) {
      /* Display calibration status for each sensor. */
      bno_l3.getCalibration(&system, &gyro, &accel, &mag);
      Serial.print("CALIBRATION: Gyro=");
      Serial.print(gyro, DEC);
      Serial.print(" Accel=");
      Serial.println(accel, DEC);

      delay(BNO055_SAMPLERATE_DELAY_MS);
    }

    Serial.println();
    Serial.println("l3 calibrated!");
    Serial.println();
    delay(500);
  }

  if (!is_calib_r3){
    tcaselect(7);
    new_calib_r3 = true;
    Serial.println("Calibrating r3...");
    delay(5000);
    uint8_t system, gyro, accel, mag = 0;
    while (!bno_r3.isFullyCalibrated()) {
      /* Display calibration status for each sensor. */
      bno_r3.getCalibration(&system, &gyro, &accel, &mag);
      Serial.print("CALIBRATION: Gyro=");
      Serial.print(gyro, DEC);
      Serial.print(" Accel=");
      Serial.println(accel, DEC);

      delay(BNO055_SAMPLERATE_DELAY_MS);
    }

    Serial.println();
    Serial.println("r3 calibrated!");
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
  if (new_calib_l1) {
    tcaselect(2);
    Serial.println("Storing l1...");

    //Store sensor ID after r3
    EEPROM.put(3*(sizeof(long) + sizeof(adafruit_bno055_offsets_t)), s_l1.sensor_id);

    //Store calibration data at offset from start of EEPROM
    adafruit_bno055_offsets_t new_cal_data_l1;
    bno_l1.getSensorOffsets(new_cal_data_l1);
    EEPROM.put(3*(sizeof(long) + sizeof(adafruit_bno055_offsets_t)) + sizeof(long), new_cal_data_l1);

    Serial.println();
    Serial.println("l1 stored!");
    Serial.println();
  }

  if (new_calib_r1) {
    tcaselect(3);
    Serial.println("Storing r1...");

    //Store sensor ID at start of EEPROM
    EEPROM.put(0, s_r1.sensor_id);

    //Store calibration data at offset from start of EEPROM
    adafruit_bno055_offsets_t new_cal_data_r1;
    bno_r1.getSensorOffsets(new_cal_data_r1);
    EEPROM.put(sizeof(long), new_cal_data_r1);

    Serial.println();
    Serial.println("r1 stored!");
    Serial.println();
  }

  if (new_calib_l2) {
    tcaselect(4);
    Serial.println("Storing l2...");

    //Store sensor ID after l1
    EEPROM.put(4*(sizeof(long) + sizeof(adafruit_bno055_offsets_t)), s_l2.sensor_id);

    //Store calibration data at offset from start of EEPROM
    adafruit_bno055_offsets_t new_cal_data_l2;
    bno_l2.getSensorOffsets(new_cal_data_l2);
    EEPROM.put(4*(sizeof(long) + sizeof(adafruit_bno055_offsets_t)) + sizeof(long), new_cal_data_l2);

    Serial.println();
    Serial.println("l2 stored!");
    Serial.println();
  }

  if (new_calib_r2) {
    tcaselect(5);
    Serial.println("Storing r2...");

    //Store sensor ID after r1
    EEPROM.put(sizeof(long) + sizeof(adafruit_bno055_offsets_t), s_r2.sensor_id);

    //Store calibration data at offset from start of EEPROM
    adafruit_bno055_offsets_t new_cal_data_r2;
    bno_r2.getSensorOffsets(new_cal_data_r2);
    EEPROM.put(2*sizeof(long) + sizeof(adafruit_bno055_offsets_t), new_cal_data_r2);

    Serial.println();
    Serial.println("r2 stored!");
    Serial.println();
  }

  if (new_calib_l3) {
    tcaselect(2);
    Serial.println("Storing l3...");

    //Store sensor ID after l2
    EEPROM.put(5*(sizeof(long) + sizeof(adafruit_bno055_offsets_t)), s_l3.sensor_id);

    //Store calibration data at offset from start of EEPROM
    adafruit_bno055_offsets_t new_cal_data_l3;
    bno_l3.getSensorOffsets(new_cal_data_l3);
    EEPROM.put(5*(sizeof(long) + sizeof(adafruit_bno055_offsets_t)) + sizeof(long), new_cal_data_l3);

    Serial.println();
    Serial.println("l3 stored!");
    Serial.println();
  }

  if (new_calib_r3) {
    tcaselect(7);
    Serial.println("Storing r3...");

    //Store sensor ID after r2
    EEPROM.put(2*(sizeof(long) + sizeof(adafruit_bno055_offsets_t)), s_r3.sensor_id);

    //Store calibration data at offset from start of EEPROM
    adafruit_bno055_offsets_t new_cal_data_r3;
    bno_r3.getSensorOffsets(new_cal_data_r3);
    EEPROM.put(2*(sizeof(long) + sizeof(adafruit_bno055_offsets_t)) + sizeof(long), new_cal_data_r3);

    Serial.println();
    Serial.println("r3 stored!");
    Serial.println();
  }
  
  delay(500);
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
  tcaselect(2);
  imu::Vector<3> gyro_l1 = bno_l1.getVector(Adafruit_BNO055::VECTOR_GYROSCOPE);
  imu::Vector<3> accel_l1 = bno_l1.getVector(Adafruit_BNO055::VECTOR_LINEARACCEL);
  tcaselect(3);
  imu::Vector<3> gyro_r1 = bno_r1.getVector(Adafruit_BNO055::VECTOR_GYROSCOPE);
  imu::Vector<3> accel_r1 = bno_r1.getVector(Adafruit_BNO055::VECTOR_LINEARACCEL);
  tcaselect(4);
  imu::Vector<3> gyro_l2 = bno_l2.getVector(Adafruit_BNO055::VECTOR_GYROSCOPE);
  imu::Vector<3> accel_l2 = bno_l2.getVector(Adafruit_BNO055::VECTOR_LINEARACCEL);
  tcaselect(5);
  imu::Vector<3> gyro_r2 = bno_r2.getVector(Adafruit_BNO055::VECTOR_GYROSCOPE);
  imu::Vector<3> accel_r2 = bno_r2.getVector(Adafruit_BNO055::VECTOR_LINEARACCEL);
  tcaselect(6);
  imu::Vector<3> gyro_l3 = bno_l3.getVector(Adafruit_BNO055::VECTOR_GYROSCOPE);
  imu::Vector<3> accel_l3 = bno_l3.getVector(Adafruit_BNO055::VECTOR_LINEARACCEL);
  tcaselect(7);
  imu::Vector<3> gyro_r3 = bno_r3.getVector(Adafruit_BNO055::VECTOR_GYROSCOPE);
  imu::Vector<3> accel_r3 = bno_r3.getVector(Adafruit_BNO055::VECTOR_LINEARACCEL);

  //Prepare data to send to server
  String data_l1 = String(gyro_l1.x()) + "," + String(gyro_l1.y()) + "," + String(gyro_l1.z()) + "," + String(accel_l1.x()) + "," + String(accel_l1.y()) + "," + String(accel_l1.z());
  String data_r1 = String(gyro_r1.x()) + "," + String(gyro_r1.y()) + "," + String(gyro_r1.z()) + "," + String(accel_r1.x()) + "," + String(accel_r1.y()) + "," + String(accel_r1.z());
  String data_l2 = String(gyro_l2.x()) + "," + String(gyro_l2.y()) + "," + String(gyro_l2.z()) + "," + String(accel_l2.x()) + "," + String(accel_l2.y()) + "," + String(accel_l2.z());
  String data_r2 = String(gyro_r2.x()) + "," + String(gyro_r2.y()) + "," + String(gyro_r2.z()) + "," + String(accel_r2.x()) + "," + String(accel_r2.y()) + "," + String(accel_r2.z());
  String data_l3 = String(gyro_l3.x()) + "," + String(gyro_l3.y()) + "," + String(gyro_l3.z()) + "," + String(accel_l3.x()) + "," + String(accel_l3.y()) + "," + String(accel_l3.z());
  String data_r3 = String(gyro_r3.x()) + "," + String(gyro_r3.y()) + "," + String(gyro_r3.z()) + "," + String(accel_r3.x()) + "," + String(accel_r3.y()) + "," + String(accel_r3.z());

  Serial.print(data_l1);
  Serial.print(",");
  Serial.print(data_r1);
  Serial.print(",");
  Serial.print(data_l2);
  Serial.print(",");
  Serial.print(data_r2);
  Serial.print(",");
  Serial.print(data_l3);
  Serial.print(",");
  Serial.println(data_r3);

  // mqttClient.poll();

  // unsigned long currentMillis = millis();

  // if (currentMillis - previousMillis >= interval) {
  //   previousMillis = currentMillis;
  //   Serial.print("Sending message to topic: ");
  //   Serial.println(topic1);
  //   Serial.println(data_l1);

  //   Serial.print("Sending message to topic: ");
  //   Serial.println(topic2);
  //   Serial.println(data_r1);

  //   Serial.print("Sending message to topic: ");
  //   Serial.println(topic3);
  //   Serial.println(data_l2);

  //   Serial.print("Sending message to topic: ");
  //   Serial.println(topic4);
  //   Serial.println(data_r2);

  //   Serial.print("Sending message to topic: ");
  //   Serial.println(topic5);
  //   Serial.println(data_l3);

  //   Serial.print("Sending message to topic: ");
  //   Serial.println(topic6);
  //   Serial.println(data_r3);

  //   mqttClient.beginMessage(topic1);
  //   mqttClient.print(data_l1);
  //   mqttClient.endMessage();

  //   mqttClient.beginMessage(topic2);
  //   mqttClient.print(data_r1);
  //   mqttClient.endMessage();

  //   mqttClient.beginMessage(topic3);
  //   mqttClient.print(data_l2);
  //   mqttClient.endMessage();

  //   mqttClient.beginMessage(topic4);
  //   mqttClient.print(data_r2);
  //   mqttClient.endMessage();

  //   mqttClient.beginMessage(topic5);
  //   mqttClient.print(data_l3);
  //   mqttClient.endMessage();

  //   mqttClient.beginMessage(topic6);
  //   mqttClient.print(data_r3);
  //   mqttClient.endMessage();

  //   Serial.println();

  // /* Display the gyroscope data in radians per second */
  // Serial.println("Left");
  // Serial.print("X: ");
  // Serial.print(gyro_l1.x());
  // Serial.print(" Y: ");
  // Serial.print(gyro_l1.y());
  // Serial.print(" Z: ");
  // Serial.print(gyro_l1.z());
  // Serial.print("\t\t");

  // /* Display the accelerometer data in m/s^2 */
  // Serial.print("X: ");
  // Serial.print(accel_l1.x());
  // Serial.print(" Y: ");
  // Serial.print(accel_l1.y());
  // Serial.print(" Z: ");
  // Serial.println(accel_l1.z());
  
  // /* Display the gyroscope data in radians per second */
  // Serial.print("X: ");
  // Serial.print(gyro_l2.x());
  // Serial.print(" Y: ");
  // Serial.print(gyro_l2.y());
  // Serial.print(" Z: ");
  // Serial.print(gyro_l2.z());
  // Serial.print("\t\t");

  // /* Display the accelerometer data in m/s^2 */
  // Serial.print("X: ");
  // Serial.print(accel_l2.x());
  // Serial.print(" Y: ");
  // Serial.print(accel_l2.y());
  // Serial.print(" Z: ");
  // Serial.println(accel_l2.z());

  // /* Display the gyroscope data in radians per second */
  // Serial.print("X: ");
  // Serial.print(gyro_l3.x());
  // Serial.print(" Y: ");
  // Serial.print(gyro_l3.y());
  // Serial.print(" Z: ");
  // Serial.print(gyro_l3.z());
  // Serial.print("\t\t");

  // /* Display the accelerometer data in m/s^2 */
  // Serial.print("X: ");
  // Serial.print(accel_l3.x());
  // Serial.print(" Y: ");
  // Serial.print(accel_l3.y());
  // Serial.print(" Z: ");
  // Serial.println(accel_l3.z());

  // /* Display the gyroscope data in radians per second */
  // Serial.println("Right");
  // Serial.print("X: ");
  // Serial.print(gyro_r1.x());
  // Serial.print(" Y: ");
  // Serial.print(gyro_r1.y());
  // Serial.print(" Z: ");
  // Serial.print(gyro_r1.z());
  // Serial.print("\t\t");

  // /* Display the accelerometer data in m/s^2 */
  // Serial.print("X: ");
  // Serial.print(accel_r1.x());
  // Serial.print(" Y: ");
  // Serial.print(accel_r1.y());
  // Serial.print(" Z: ");
  // Serial.println(accel_r1.z());
  
  // /* Display the gyroscope data in radians per second */
  // Serial.print("X: ");
  // Serial.print(gyro_r2.x());
  // Serial.print(" Y: ");
  // Serial.print(gyro_r2.y());
  // Serial.print(" Z: ");
  // Serial.print(gyro_r2.z());
  // Serial.print("\t\t");

  // /* Display the accelerometer data in m/s^2 */
  // Serial.print("X: ");
  // Serial.print(accel_r2.x());
  // Serial.print(" Y: ");
  // Serial.print(accel_r2.y());
  // Serial.print(" Z: ");
  // Serial.println(accel_r2.z());

  // /* Display the gyroscope data in radians per second */
  // Serial.print("X: ");
  // Serial.print(gyro_r3.x());
  // Serial.print(" Y: ");
  // Serial.print(gyro_r3.y());
  // Serial.print(" Z: ");
  // Serial.print(gyro_r3.z());
  // Serial.print("\t\t");

  // /* Display the accelerometer data in m/s^2 */
  // Serial.print("X: ");
  // Serial.print(accel_r3.x());
  // Serial.print(" Y: ");
  // Serial.print(accel_r3.y());
  // Serial.print(" Z: ");
  // Serial.println(accel_r3.z());
  // Serial.println();
  // Serial.println();

  // delay(BNO055_SAMPLERATE_DELAY_MS);
  delay(250);
}
