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
1. To create an `.exe` file, run `src\setup.py`.
2. Make sure the **Arduino Nano driver** is installed.
3. Edit the `monitor_config.ini` file to configure monitor parameters.
4. Place the executable or a shortcut into the startup folder: `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`
