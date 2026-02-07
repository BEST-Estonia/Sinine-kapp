import RPi.GPIO as GPIO
import time

# Set up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        button_state = GPIO.input(21)
        
        if button_state == GPIO.LOW:
            print("door closed")
        else:
            print("door open")
        
        time.sleep(1)  # Check every 500ms to avoid excessive output

except KeyboardInterrupt:
    print("\nTest stopped")

finally:
    GPIO.cleanup()
