"""
See fail tegeleb riistvara suhtlusega.
get_nfc() loeb nfc lugejat ja returnib saadud vastuse
Mai viitsi rohkem edasi kirjutada

"""
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import time
import sys
import subprocess
import threading
import numpy as np
import cv2
from pyzbar.pyzbar import decode
try:
    import msvcrt
except ImportError:
    msvcrt = None


# --- Configuration ---
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
FRAME_LEN = int(FRAME_WIDTH * FRAME_HEIGHT * 1.5) # YUV420 buffer size

class CameraStream:
    """
    Background service to keep the camera buffer clean and ready.
    Runs silently.
    """
    def __init__(self):
        self.cmd = [
            'rpicam-vid', '-t', '0', '--inline',
            '--width', str(FRAME_WIDTH), '--height', str(FRAME_HEIGHT),
            '--codec', 'yuv420', '--nopreview', '-o', '-'
        ]
        self.process = None
        self.thread = None
        self.running = False
        self.latest_frame = None

    def start(self):
        if self.running:
            return
        
        try:
            self.process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, bufsize=10**8)
            self.running = True
            self.thread = threading.Thread(target=self._update, daemon=True)
            self.thread.start()
        except:
            # If camera fails, ensure running is False so we don't hang
            self.running = False

    def _update(self):
        while self.running:
            try:
                raw_bytes = self.process.stdout.read(FRAME_LEN)
                if len(raw_bytes) != FRAME_LEN:
                    continue

                yuv = np.frombuffer(raw_bytes, dtype=np.uint8).reshape((int(FRAME_HEIGHT * 1.5), FRAME_WIDTH))
                self.latest_frame = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_I420)
            except:
                break

    def read(self):
        return self.latest_frame

    def stop(self):
        self.running = False
        if self.process:
            try:
                self.process.terminate()
            except:
                pass

# Create a single global instance of the camera
camera_service = CameraStream()

def get_barcode(timeout=10):
    """
    Scans for a barcode for up to 'timeout' seconds.
    
    Returns:
        str: The barcode data if found.
        int: 0 if timed out.
    """
    
    # 1. Auto-start camera if it's not running
    if not camera_service.running:
        camera_service.start()
        # Give it 1.5s to warm up and fill the buffer if we just started it
        time.sleep(1.5)

    start_time = time.time()

    # 2. Loop until timeout
    while (time.time() - start_time) < timeout:
        frame = camera_service.read()
        
        if frame is None:
            time.sleep(0.01)
            continue

        # Convert to grayscale for faster processing
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Decode
        barcodes = decode(gray)
        
        if barcodes:
            # Return the first barcode found immediately
            return barcodes[0].data.decode("utf-8")
        
        # Slight pause to prevent 100% CPU usage loop
        time.sleep(0.05)

    # 3. If we exit the loop, time is up
    return 0

def cleanup_camera():
    """Call this when your program is shutting down completely."""
    camera_service.stop()

#küsib nfc tagi
def get_nfc():
    """
    Waits until a card is tapped, then returns the UID as a number.
    """
    reader = SimpleMFRC522()
    try:
        # reader.read() blocks (pauses) execution until a card is detected
        id, text = reader.read()
        return id
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


#Sebib barcodei
def get_barcode_scan():
   
    barcode = input("DEBUG SISesta klaviatuuril barcode---")
    print() # Newline on timeout
    return barcode



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
