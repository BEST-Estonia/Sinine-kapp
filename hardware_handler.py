"""
See fail tegeleb riistvara suhtlusega.
get_nfc() loeb nfc lugejat ja returnib saadud vastuse
Mai viitsi rohkem edasi kirjutada

"""
import RPi.GPIO as GPIO
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
        GPIO.cleanup()

#Küsib kaalu näitu
def get_wheight():
    time.sleep(1)
    kaal = 40.6
    return kaal


#avab ukse
def Ukse_avaja():
    return 0



#muutujad simuleerimaks kaua uks lahti on
_door_timer_start = None
_DOOR_DURATION = 15

def is_door_open():
    """
    Simuleerib ust. Esimesel käivitamisel "avab" ukse 10 sekundiks.
    Järgnevatel kordadel kontrollib, kas aeg on täis.
    """
    global _door_timer_start
    
    # 1. Kui taimer ei jookse (on None), siis see on esimene kontroll.
    #    Käivita taimer.
    if _door_timer_start is None:
    
        _door_timer_start = time.time() # Salvesta algusaeg
        return True # Ütleme tsüklile, et uks on lahti

    # 2. Taimer juba jookseb. Kontrollime, kas aeg on täis.
    elapsed_time = time.time() - _door_timer_start
    
    if elapsed_time < _DOOR_DURATION:
        # 3. Aeg POLE veel täis. Uks on endiselt lahti.
      
        return True
    else:
        # 4. Aeg ON täis. "Sulgeme" ukse.
      
        _door_timer_start = None # Nullime taimeri järgmiseks korraks
        return False