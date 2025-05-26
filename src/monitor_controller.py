import os
import sys
import configparser
import time
from collections import deque

from utils import constrain, round_down

class MonitorController:  
    def __init__(self, monitor, config_path=None):
        self.monitor = monitor
        self.target_brightness_buffer = deque(maxlen=5)
        self.total_delta = 0
        self.manual_mode = False

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

    def process_delta(self, delta):
        if delta != 0:
            self.total_delta = constrain(self.total_delta + delta, self.current_brightness, 100 - self.current_brightness)
            temporary_brightness = constrain(self.current_brightness + self.total_delta, 0, 100)
            self.set_temporary_brightness(temporary_brightness)

        print(f"Current brightness {self.current_brightness + self.total_delta}% with delta {self.total_delta}%")

    def process_manual_mode(self, manual_mode):
        if self.manual_mode != manual_mode:
            self.manual_mode = manual_mode
            self.set_brightness(self.current_brightness)

    def process_lux(self, lux_value):
        if self.manual_mode:
            return
            
        target_brightness = self.calculate_brightness(lux_value)
        self.target_brightness_buffer.append(target_brightness)
        self.fade_brightness_if_needed()    

    def fade_brightness_if_needed(self):
        print(f"Target brightness buffer: {', '.join(f'{x}%' for x in self.target_brightness_buffer)}")
        if not all(x == self.target_brightness_buffer[0] for x in self.target_brightness_buffer):
            return False
            
        target_brightness = self.target_brightness_buffer[0]
        if (abs(target_brightness - self.current_brightness) < self.brightness_step * 2
            and target_brightness != 0 and target_brightness != 100):
            return False
        
        print(f"Target brightness: {target_brightness}%")
        self.fade_brightness(target_brightness)
    
    def fade_brightness(self, brightness, step_delay = 0):
        current_brightness = self.current_brightness
        step = 1 if current_brightness < brightness else -1
        while current_brightness != brightness:
            current_brightness = current_brightness + step
            self.set_brightness(current_brightness)
            time.sleep(step_delay)    
    
    def set_brightness(self, brightness):
        try:
            with self.monitor:
                self.monitor.set_luminance(brightness)
                self.current_brightness = brightness
                self.total_delta = 0
                return True
        except Exception as e:
            print(f"Failed to set brightness: {e}")
            return False
        
    def set_temporary_brightness(self, brightness):
        try:
            with self.monitor:
                self.monitor.set_luminance(brightness)
                return True
        except Exception as e:
            print(f"Failed to set brightness: {e}")
            return False
    
    def calculate_brightness(self, lux_value):
        # Limit lux value
        lux_value = constrain(lux_value, self.lux_min, self.lux_max)

        # Normalize lux → 0–100
        brightness = int((lux_value - self.lux_min) / (self.lux_max - self.lux_min) * 100)

        # Limit brightness
        brightness = constrain(brightness, self.brightness_min, self.brightness_max)
        brightness = round_down(brightness, self.brightness_step)
        
        return brightness
