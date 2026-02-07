import hardware_handler
import time

print("Starting barcode test...")
print("Scan a barcode. The program will wait for 10 seconds for each scan.")
print("To exit, press Ctrl+C.")

try:
    while True:
        print("\nWaiting for barcode...")
        # Wait for a barcode for 10 seconds
        barcode = hardware_handler.get_barcode(timeout=10)

        if barcode != 0:
            print(f"--> Scanned barcode: {barcode}")
        else:
            print("--> Timeout: No barcode scanned in the last 10 seconds.")
        
        # Adding a small delay to make the output more readable
        time.sleep(1)

except KeyboardInterrupt:
    print("\nExiting barcode test.")

