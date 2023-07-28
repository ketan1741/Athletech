#include <Wire.h>
#include <SPI.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <BH1750.h>
#include "MHZ19.h"
#include <Arduino.h>

#define BME_SCK 13
#define BME_MISO 12
#define BME_MOSI 11
#define BME_CS 10

#define SEALEVELPRESSURE_HPA (1013.25)

#define RX_PIN 3
#define TX_PIN 2
#define BAUDRATE 9600

Adafruit_BME280 bme; // I2C

BH1750 lightMeter;

MHZ19 myMHZ19;
#if defined(ESP32)
HardwareSerial mySerial(2);
#else
#include <SoftwareSerial.h>
SoftwareSerial mySerial(RX_PIN, TX_PIN);
#endif

unsigned long delayTime;

void setup() {
  // BME280 Environmental sensor part
  Serial.begin(9600);

  bool status;
  
  status = bme.begin();  
  if (!status) {
    Serial.println("Could not find a valid BME280 sensor, check wiring!");
    while (1);
  }
  
  delayTime = 200;

  //Below is BH1750 light sensor part
  Wire.begin();

  lightMeter.begin();

  //Below is MH-Z19B Gas Sensor part
  mySerial.begin(BAUDRATE);
  myMHZ19.begin(mySerial);
}


void loop() { 
  //Temperature in degree
  Serial.print(bme.readTemperature());
  Serial.print(",");
  
  //Pressure in hPa
  Serial.print(bme.readPressure() / 100.0F);
  Serial.print(",");
  
  //Altitude in meter
  Serial.print(bme.readAltitude(SEALEVELPRESSURE_HPA));
  Serial.print(",");
  
  //Humidity in %
  Serial.print(bme.readHumidity());
  Serial.print(",");

  //light in lux
  float lux = lightMeter.readLightLevel();
  Serial.print(lux);
  Serial.print(",");

  //CO2 Concentration in ppm
  double adjustedCO2 = myMHZ19.getCO2Raw();
  adjustedCO2 = 6.60435861e+15 * exp(-8.78661228e-04 * adjustedCO2);
  Serial.print(adjustedCO2);
  
  Serial.println();
  delay(delayTime);
}
