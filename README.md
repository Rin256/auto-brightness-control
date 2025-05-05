# Auto Brightness Control for Monitor
Adjusts monitor brightness based on ambient light using Arduino Nano and BH1750FVI sensor.

## Components
- **Arduino Nano** — powered and connected via USB
- **Rotary Encoder with Button**
  - S1 → D2
  - S2 → D3
  - KEY → D4
- **LED with resistor** → D13
- **BH1750FVI Sensor**
  - SCL → A5
  - SDA → A4

## Usage
Edit `monitor_config.ini` with monitor parameters.
File must be in the same directory as the executable.
