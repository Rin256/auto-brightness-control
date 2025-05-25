import time
import serial
from concurrent.futures import ThreadPoolExecutor

from monitorcontrol import get_monitors

from monitor_controller import MonitorController

class LightManager:
    def __init__(self, serial_port, baud_rate):
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.monitors = self._initialize_monitors()
        self.executor = ThreadPoolExecutor(max_workers=len(self.monitors) if self.monitors else 1)

    def _initialize_monitors(self):
        monitors = [MonitorController(m) for m in get_monitors()]
        if not monitors:
            print("Warning: No DDC/CI compatible monitors found!")
        return monitors

    def run(self):
        try:
            with serial.Serial(self.serial_port, self.baud_rate, timeout=1) as ser:
                print(f"Listening on {self.serial_port}...")
                while True:
                    if ser.in_waiting:
                        data = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                        lines = data.strip().splitlines()
                        if lines:
                            self._process_line(lines[-1].strip())
                    else:
                        time.sleep(0.01)
        except serial.SerialException as e:
            print(f"Serial port error: {e}")
        except KeyboardInterrupt:
            print("\nProgram terminated by user")
        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            self.executor.shutdown()

    def _process_line(self, line):
        try:
            print("=" * 50)
            lux_str, manual_str, delta_str = line.split(',')
            lux = float(lux_str)
            manual_mode = bool(int(manual_str))
            delta = int(delta_str)
            self._handle_input(lux, manual_mode, delta)
        except Exception as e:
            print(f"Invalid data: '{line}' ({e})")

    def _handle_input(self, lux, manual_mode, delta):
        futures = []
        for monitor in self.monitors:
            future = self.executor.submit(self._process_monitor, monitor, lux, manual_mode, delta)
            futures.append(future)
        
        for future in futures:
            future.result()

    def _process_monitor(self, monitor, lux, manual_mode, delta):
        monitor.process_delta(delta)
        monitor.process_manual_mode(manual_mode)
        monitor.process_lux(lux)
