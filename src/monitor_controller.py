import os
import sys
import time
import configparser

class MonitorController:
    UPDATE_DELAY = 1.1
    
    def __init__(self, monitor, config_path=None):
        self.monitor = monitor
        self.last_command_time = 0
        self.update_delay = MonitorController.UPDATE_DELAY

        if config_path is None:
            base_path = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
            config_path = os.path.join(base_path, 'monitor_config.ini')

        self.config_path = config_path
        self._load_config()
        
        try:
            with self.monitor:
                self.current_brightness = self.monitor.get_luminance()
                self.model = self.monitor.get_vcp_capabilities().get('model', 'DEFAULT')
                print(f"Monitor {self.model} brightness: {self.current_brightness}%")
        except Exception as e:
            print(f"Could not read monitor info: {e}")
            self.current_brightness = 50
            self.model = 'DEFAULT'

        self._apply_model_settings()

    def _load_config(self):
        self.config = configparser.ConfigParser()
        self.config['DEFAULT'] = {
            'LUX_MIN': '0',
            'LUX_MAX': '1000',
            'BRIGHTNESS_MIN': '0',
            'BRIGHTNESS_MAX': '100',
            'BRIGHTNESS_STEP': '1'
        }

        if os.path.exists(self.config_path):
            self.config.read(self.config_path)
        else:
            print(f"Config file '{self.config_path}' not found. Using defaults.")

    def _apply_model_settings(self):
        cfg = self.config
        model_section = self.model if self.model in cfg else 'DEFAULT'

        self.lux_min = int(self.config[model_section].get('LUX_MIN', self.config['DEFAULT']['LUX_MIN']))
        self.lux_max = int(self.config[model_section].get('LUX_MAX', self.config['DEFAULT']['LUX_MAX']))
        self.brightness_min = int(self.config[model_section].get('BRIGHTNESS_MIN', self.config['DEFAULT']['BRIGHTNESS_MIN']))
        self.brightness_max = int(self.config[model_section].get('BRIGHTNESS_MAX', self.config['DEFAULT']['BRIGHTNESS_MAX']))
        self.brightness_step = int(self.config[model_section].get('BRIGHTNESS_STEP', self.config['DEFAULT']['BRIGHTNESS_STEP']))

    def set_brightness_if_changed(self, brightness):
        if self.current_brightness == brightness:
            print(f"Brightness unchanged ({brightness}%), skipping update")
            return False

        now = time.time()
        #if now - self.last_command_time < self.update_delay:
        #    print("Command skipped: too soon after previous")
        #    return False

        try:
            with self.monitor:
                self.monitor.set_luminance(brightness)
                self.current_brightness = brightness
                self.last_command_time = now
                print(f"Successfully set brightness to {brightness}%")
                return True
        except Exception as e:
            print(f"Failed to set brightness: {e}")
            return False

    def calculate_brightness(self, lux_value, delta = 0):
        # Limit lux value
        lux_value = self.constrain(lux_value, self.lux_min, self.lux_max)

        # Normalize lux → 0–100
        brightness = int((lux_value - self.lux_min) / (self.lux_max - self.lux_min) * 100)

        # Limit brightness
        brightness = self.constrain(brightness + delta, self.brightness_min, self.brightness_max)
        
        print(f"Measured lux: {lux_value:.2f} lux")
        print(f"Target brightness: {brightness}% (correction {delta:+d}%)")
        
        brightness = self.constrain(
            brightness,
            self.current_brightness - self.brightness_step - abs(delta),
            self.current_brightness + self.brightness_step + abs(delta))

        return brightness
    
    def constrain(self, x, a, b):
        return max(a, min(x, b))
