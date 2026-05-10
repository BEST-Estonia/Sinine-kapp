"""
See fail tegeleb riistvara suhtlusega.
get_nfc() loeb nfc lugejat ja returnib saadud vastuse
Mai viitsi rohkem edasi kirjutada

"""
try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError:
    from fake_rpi.RPi import GPIO
from mfrc522 import SimpleMFRC522
import time
import logging

def get_barcode(timeout=10):
    """
    This function is deprecated. Barcode reading is now handled
    in the main event loop (drawer.py) to avoid input conflicts.
    This function remains for compatibility but will always time out.
    """
    logging.warning("hardware_handler.get_barcode() is deprecated and should not be used.")
    return 0

#küsib nfc tagi
def get_nfc(cancel_check_callback=None):
    """
    Waits until a card is tapped, then returns the UID as a number.
    If cancel_check_callback is provided, it is called periodically.
    If callback returns True, function returns None.
    """
    reader = SimpleMFRC522()
    try:
        while True:
            id, text = reader.read_no_block()
            if id:
                return id
            if cancel_check_callback and cancel_check_callback():
                return None
            time.sleep(0.1)
    finally:
        # Good practice to clean up pins, though strict cleanup
        # depends on if you have other sensors running.
        pass

#Küsib kaalu näitu
def get_wheight():
    time.sleep(1)
    kaal = 40.6
    return kaal


#avab ukse
def Ukse_avaja():
    return 0



# --- DOOR STATE DETECTION ---
# GPIO pin for door sensor using RPi.GPIO
DOOR_SENSOR_PIN = 21

# Flag to track GPIO setup
_gpio_initialized = False

def init_door_sensor():
    """
    Initialize the door sensor on GPIO21 using RPi.GPIO with built-in pull-up.

    Circuit:
    [GPIO 21]----[Pull-Up to 3.3V (built-in)]
         |
    [Push Button/Sensor]
         |
       [GND]

    When sensor connected to GND: GPIO reads LOW (GPIO.LOW = 0) → door is CLOSED
    When sensor floating (pulled up to 3.3V): GPIO reads HIGH (GPIO.HIGH = 1) → door is OPEN
    """
    global _gpio_initialized
    try:
        if not _gpio_initialized:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(DOOR_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            _gpio_initialized = True
        logging.info(f"Door sensor initialized successfully on GPIO {DOOR_SENSOR_PIN}")
    except Exception as e:
        logging.error(f"CRITICAL: Failed to initialize door sensor on GPIO {DOOR_SENSOR_PIN}: {e}")
        _gpio_initialized = False

def is_door_open():
    """
    Reads the door sensor state using RPi.GPIO.

    With pull_up=True (GPIO.PUD_UP):
    - Sensor connected to GND → GPIO reads LOW (0) → door is CLOSED → return False
    - Sensor floating (pulled up to 3.3V) → GPIO reads HIGH (1) → door is OPEN → return True
    """
    if not _gpio_initialized:
        logging.error("CRITICAL: Door sensor not initialized - returning False (door closed)")
        return False

    try:
        door_state = GPIO.input(DOOR_SENSOR_PIN)
        
        if door_state == GPIO.LOW:
            # Door is CLOSED (connected to ground)
            is_open = False
        else:
            # Door is OPEN (floating/pulled up)
            is_open = True
        
        logging.debug(f"Door sensor: GPIO state={door_state}, is_open={is_open}")
        
        return is_open

    except Exception as e:
        logging.error(f"Error reading door sensor: {e}")
        return False
