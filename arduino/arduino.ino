#include <BH1750.h>
#include <Wire.h>
#include <EncButton.h>
#include <EEPROM.h>

// Pins and parameters
#define LED_PIN 13
#define BAUD_RATE 115200
#define UPDATE_DELAY 1100
#define EEPROM_ADDR_MODE 0
#define ENCODER_SENSITIVITY 5

// Objects
EncButton eb(2, 3, 4);
BH1750 lightMeter;

// States
bool isManualMode = false;
uint32_t lastSendTime = 0;
uint32_t centerLightUntil = 0;

void setup() {
  Serial.begin(BAUD_RATE);
  Wire.begin();
  lightMeter.begin();
  pinMode(LED_PIN, OUTPUT);

  // Read saved mode from EEPROM
  isManualMode = EEPROM.read(EEPROM_ADDR_MODE);
  digitalWrite(LED_PIN, isManualMode ? HIGH : LOW);
  
  eb.counter = 0;
}

void loop() {
  eb.tick();

  // Read and round light level to nearest ten
  uint16_t lux = lightMeter.readLightLevel();
  lux = (lux / 10) * 10;

  // Toggle manual mode on button click
  if (eb.click()) {
    isManualMode = !isManualMode;
    digitalWrite(LED_PIN, isManualMode ? HIGH : LOW);
    EEPROM.write(EEPROM_ADDR_MODE, isManualMode);
    eb.counter = 0;
  }

  // LED control
  if (isManualMode) {
    digitalWrite(LED_PIN, HIGH);
  }

  // Send data with interval
  if (millis() - lastSendTime >= UPDATE_DELAY) {
    Serial.print(lux);
    Serial.print(",");
    Serial.print(isManualMode);
    Serial.print(",");
    Serial.println(eb.counter * ENCODER_SENSITIVITY);

    eb.counter = 0;
    lastSendTime = millis();
  }
}
