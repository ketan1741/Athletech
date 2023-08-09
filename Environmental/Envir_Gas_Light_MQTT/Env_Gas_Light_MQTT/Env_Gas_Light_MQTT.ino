#include <ArduinoMqttClient.h>
#include <WiFiNINA.h>
#include <Wire.h>
#include <SPI.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include "arduino_secret.h"
#include "MHZ19.h"
#include <Arduino.h>
#include <BH1750.h>

#define BME_SCK 13
#define BME_MISO 12
#define BME_MOSI 11
#define BME_CS 10

#define RX_PIN 3
#define TX_PIN 2
#define BAUDRATE 9600                                      // Native to the sensor (do not change)

#define SEALEVELPRESSURE_HPA (1013.25)

Adafruit_BME280 bme; // I2C
BH1750 lightMeter;

unsigned long delayTime;

///////please enter your sensitive data in the Secret tab/arduino_secrets.h
char ssid[] = SECRET_SSID;        // your network SSID (name)
char pass[] = SECRET_PASS;    // your network password (use for WPA, or use as key for WEP)

WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);

const char* mqtt_username = "aws_server";
const char* mqtt_password = "esports_data";

const char broker[] = "ec2-3-145-8-89.us-east-2.compute.amazonaws.com";
int        port     = 8883;
const char topic[]  = "Environment";

//set interval for sending messages (milliseconds)
const long interval = 250;
unsigned long previousMillis = 0;

int count = 0;

//below is MH-Z19B Code
MHZ19 myMHZ19;
#if defined(ESP32)
HardwareSerial mySerial(2);                                // On ESP32 we do not require the SoftwareSerial library, since we have 2 USARTS available
#else
#include <SoftwareSerial.h>                                //  Remove if using HardwareSerial or non-uno compatible device
SoftwareSerial mySerial(RX_PIN, TX_PIN);                   // (Uno example) create device to MH-Z19 serial
#endif

void setup() {
  //Initialize serial and wait for port to open:
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }

  // attempt to connect to Wifi network:
  Serial.print("Attempting to connect to WPA SSID: ");
  Serial.println(ssid);
  while (WiFi.begin(ssid, pass) != WL_CONNECTED) {
    // failed, retry
    Serial.print(".");
    delay(5000);
  }

  Serial.println("You're connected to the network");
  Serial.println();

  Serial.print("Attempting to connect to the MQTT broker: ");
  Serial.println(broker);

  mqttClient.setUsernamePassword(mqtt_username, mqtt_password);

  if (!mqttClient.connect(broker, port)) {
    Serial.print("MQTT connection failed! Error code = ");
    Serial.println(mqttClient.connectError());

    while (1);
  }

  Serial.println("You're connected to the MQTT broker!");
  Serial.println();

  //下面是BME280部分
  Serial.println(F("BME280 test"));

  bool status;
  
  // default settings
  // (you can also pass in a Wire library object like &Wire2)
  status = bme.begin();  
  if (!status) {
    Serial.println("Could not find a valid BME280 sensor, check wiring!");
    while (1);
  }
  
  Serial.println("-- Default Test --");
  delayTime = 1000;

  Serial.println();

  mySerial.begin(BAUDRATE);                                // Uno example: Begin Stream with MHZ19 baudrate
  myMHZ19.begin(mySerial);                                 // *Important, Pass your Stream reference

  //下面是Light sensor部分
   // Initialize the I2C bus (BH1750 library doesn't do this automatically)
  Wire.begin();
  // On esp8266 you can select SCL and SDA pins using Wire.begin(D4, D3);
  // For Wemos / Lolin D1 Mini Pro and the Ambient Light shield use Wire.begin(D2, D1);

  lightMeter.begin();

  Serial.println(F("BH1750 Test begin"));
}

void loop() {
  // call poll() regularly to allow the library to send MQTT keep alive which
  // avoids being disconnected by the broker
  mqttClient.poll();

  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    // save the last time a message was sent
    previousMillis = currentMillis;

    //record random value from A0, A1 and A2
    float Rvalue = bme.readTemperature();
    float Rvalue2 = bme.readPressure() / 100.0F;
    float Rvalue3 = bme.readAltitude(SEALEVELPRESSURE_HPA);
    float Rvalue4 = bme.readHumidity();
    float Rvalue5 = lightMeter.readLightLevel()
    double adjustedCO2 = myMHZ19.getCO2Raw();
    adjustedCO2 = 6.60435861e+15 * exp(-8.78661228e-04 * adjustedCO2);
    float Rvalue6 = adjustedCO2;

    Serial.print(Rvalue);
    Serial.print(",");
    Serial.print(Rvalue2);
    Serial.print(",");
    Serial.print(Rvalue3);
    Serial.print(",");
    Serial.print(Rvalue4);
    Serial.print(",");
    Serial.print(Rvalue5);
    Serial.print(",");
    Serial.print(Rvalue6);
    // Serial.print("Sending message to topic: ");
    // Serial.println(topic);
    // Serial.println(Rvalue);

    // Serial.print("Sending message to topic: ");
    // Serial.println(topic2);
    // Serial.println(Rvalue2);

    // Serial.print("Sending message to topic: ");
    // Serial.println(topic3);
    // Serial.println(Rvalue3);

    // Serial.print("Sending message to topic: ");
    // Serial.println(topic4);
    // Serial.println(Rvalue4);

    // Serial.print("Sending message to topic: ");
    // Serial.println(topic5);
    // Serial.println(Rvalue5);

    // Serial.print("Sending message to topic: ");
    // Serial.println(topic6);
    // Serial.println(Rvalue6);

    // send message, the Print interface can be used to set the message contents
    mqttClient.beginMessage(topic);
    mqttClient.print(Rvalue);
    mqttClient.print(",");
    mqttClient.print(Rvalue2);
    mqttClient.print(",");
    mqttClient.print(Rvalue3);
    mqttClient.print(",");
    mqttClient.print(Rvalue4);
    mqttClient.print(",");
    mqttClient.print(Rvalue5);
    mqttClient.print(",");
    mqttClient.print(Rvalue6);
    mqttClient.println();
    mqttClient.endMessage();

    Serial.println();
  }
}