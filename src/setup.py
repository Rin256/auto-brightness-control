from cx_Freeze import setup, Executable
import os

config_path = "monitor_config.ini"
# Check if the configuration file exists
if not os.path.exists(config_path):
    raise FileNotFoundError(f"Configuration file not found: {config_path}")

# Build options
build_options = {
    "packages": ["monitorcontrol", "serial"],
    "excludes": [],
    "include_files": [(config_path, config_path)],  # Copy monitor_config.ini next to the exe
}

# Base settings (None = console app, "Win32GUI" = no console window)
base = "Win32GUI"

executables = [
    Executable(
        "main.py",
        base=base,
        target_name="AutoBrightnessControl.exe",
    )
]

setup(
    name="AutoBrightnessControl",
    version="1.0",
    description="Auto brightness control",
    options={"build_exe": build_options},
    executables=executables,
)
