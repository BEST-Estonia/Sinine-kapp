import arduino_handler
import time

print("--- Main Program Started ---")

def GUI_default():
    return 1

# Connect to Arduino
if not arduino_handler.connect():
    print("Failed to connect to Arduino. Exiting...")
    exit()

print("Waiting for NFC card...")

while True:
    GUI_default()
    card_id = arduino_handler.get_nfc()

    if card_id and not card_id.startswith("ERROR"):
        print("\n--- CARD DETECTED ---")
        print("NFC ID:", card_id)
        break

    print("No card detected. Waiting...")
    time.sleep(1)

arduino_handler.disconnect()
