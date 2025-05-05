#include <BH1750.h>
#include <Wire.h>
#include <EncButton.h>
#include <EEPROM.h>

// Pins and parameters
#define LED_PIN 13
#define BAUD_RATE 115200
#define UPDATE_DELAY 1100
#define EEPROM_ADDR_MODE 0
#define CENTER_LIGHT_TIMEOUT 200  // ms

// Encoder counter parameters (counter_limit * multiplier = 100)
#define COUNTER_LIMIT 20
#define COUNTER_MULTIPLIER 5

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

  // Center position indication in automatic mode
  if (!isManualMode && eb.turn() && eb.counter == 0) {
    centerLightUntil = millis() + CENTER_LIGHT_TIMEOUT;
  }

  // LED control
  if (isManualMode) {
    digitalWrite(LED_PIN, HIGH);
  } else {
    digitalWrite(LED_PIN, millis() < centerLightUntil ? HIGH : LOW);
  }

  // Send data with interval
  if (millis() - lastSendTime >= UPDATE_DELAY) {
    eb.counter = constrain(eb.counter, -COUNTER_LIMIT, COUNTER_LIMIT);
    
    Serial.print(lux);
    Serial.print(",");
    Serial.print(isManualMode);
    Serial.print(",");
    Serial.println(eb.counter * COUNTER_MULTIPLIER);

    lastSendTime = millis();
    if (isManualMode) {
      eb.counter = 0;
    }
  }
}
