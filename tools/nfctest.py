"""Standalone NFC reader diagnostic."""

from pathlib import Path
import sys
import time


# Let this script run from tools/ without installing the package.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sinine_kapp.devices import nfc_reader


def main():
    """Print one NFC tag UID/text at a time."""
    print("Starting NFC reader test...")
    print("Tap a card to print its UID and stored text.")
    print("To exit, press Ctrl+C.\n")

    try:
        while True:
            print("Waiting for NFC tag...")
            tag_id, tag_text = nfc_reader.read_tag_details()
            print(f"--> NFC UID: {tag_id}")
            print(f"--> NFC Text: {tag_text!r}\n")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting NFC test.")


if __name__ == "__main__":
    main()
