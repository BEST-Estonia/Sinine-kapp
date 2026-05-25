"""Standalone barcode scanner diagnostic.

This bypasses the pygame UI and reads directly from the Linux keyboard input
device, which is useful when scanner input is not reaching the main app.
"""

from pathlib import Path
import sys
import time


# Let this script run from tools/ without installing the package.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sinine_kapp.devices import barcode_scanner


def main():
    """Find a scanner-like keyboard device and print scanned codes."""
    device = barcode_scanner.find_barcode_device()
    devices = barcode_scanner.list_keyboard_devices()

    print("Starting barcode scanner test...")
    print("Detected keyboard input devices:")
    for path in devices:
        print(f"  - {path}")

    if device is None:
        print("\nNo barcode-like keyboard device was found.")
        return

    print(f"\nUsing scanner device: {device}")
    print("Scan a barcode. Most scanners finish with Enter automatically.")
    print("To exit, press Ctrl+C.\n")

    try:
        while True:
            print("Waiting for barcode...")
            barcode = barcode_scanner.read_barcode(timeout=10, device_path=str(device))

            if barcode:
                print(f"--> Scanned barcode: {barcode}\n")
            else:
                print("--> Timeout: No barcode scanned in the last 10 seconds.\n")

            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nExiting barcode test.")


if __name__ == "__main__":
    main()
