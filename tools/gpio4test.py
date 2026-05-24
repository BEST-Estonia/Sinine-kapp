from pathlib import Path
import sys
import time

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sinine_kapp.devices import door


try:
    door.init_sensor()
    while True:
        if door.is_open():
            print("door open")
        else:
            print("door closed")

        time.sleep(1)  # Check every 500ms to avoid excessive output

except KeyboardInterrupt:
    print("\nTest stopped")

finally:
    door.cleanup()
