"""Standalone door sensor diagnostic."""

from pathlib import Path
import sys
import time


# Let this script run from tools/ without installing the package.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import RPi.GPIO as GPIO

from sinine_kapp.devices.door import DOOR_SENSOR_PIN


def format_state(raw_value):
    """Map the raw GPIO value to the app's door state labels."""
    if raw_value == GPIO.LOW:
        return "CLOSED"
    return "OPEN"


def main():
    """Print door sensor state whenever it changes."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(DOOR_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    print(f"Testing door sensor on BCM GPIO {DOOR_SENSOR_PIN}.")
    print("Current app mapping:")
    print("  GPIO LOW  / connected to GND    -> CLOSED")
    print("  GPIO HIGH / disconnected/floating -> OPEN")
    print("Press Ctrl+C to exit.\n")

    last_raw_value = None

    try:
        while True:
            raw_value = GPIO.input(DOOR_SENSOR_PIN)
            if raw_value != last_raw_value:
                print(f"raw={raw_value} state={format_state(raw_value)}")
                last_raw_value = raw_value
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nExiting door sensor test.")
    finally:
        GPIO.cleanup(DOOR_SENSOR_PIN)


if __name__ == "__main__":
    main()
