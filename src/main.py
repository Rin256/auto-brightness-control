import time

from light_manager import LightManager
import serial.tools.list_ports
import serial

# Constants
BAUD_RATE = 115200
RECONNECT_DELAY = 3  # Delay before reconnection attempt (seconds)

def find_arduino_port():
    """Searches for Arduino by VID/PID among available ports."""
    ARDUINO_IDS = [
        (0x2341, 0x0043),  # Arduino Uno
        (0x2341, 0x0010),  # Arduino Nano
        (0x1A86, 0x7523),  # CH340 (Chinese clones)
    ]
    
    for port in serial.tools.list_ports.comports():
        if (port.vid, port.pid) in ARDUINO_IDS:
            return port.device
            
    return None

def main():
    """Main loop with automatic reconnection on errors."""
    while True:
        try:
            # Searching for Arduino
            arduino_port = find_arduino_port()
            if not arduino_port:
                print("Arduino not found. Retrying...")
                time.sleep(RECONNECT_DELAY)
                continue

            # Connection and startup
            print(f"Connected to Arduino on port: {arduino_port}")
            controller = LightManager(
                serial_port=arduino_port,
                baud_rate=BAUD_RATE
            )
            controller.run()  # Will run until an error occurs

        except serial.SerialException as e:
            print(f"Communication error: {e}. Reconnecting...")
            time.sleep(RECONNECT_DELAY)

        except KeyboardInterrupt:
            print("\nProgram stopped by user.")
            break

        except Exception as e:
            print(f"Unknown error: {e}. Restarting...")
            time.sleep(RECONNECT_DELAY)

if __name__ == "__main__":
    main()