import time
import threading
from PIL import Image, ImageDraw, ImageFont

# Try to import hardware-specific libraries
try:
    import board
    import digitalio
    from adafruit_rgb_display.st7789 import ST7789
    HARDWARE_AVAILABLE = True
except ImportError:
    print("LCD hardware libraries not available - using mock LCD")
    HARDWARE_AVAILABLE = False
    board = None
    digitalio = None
    ST7789 = None

class LCD:
    def __init__(self):
        # --- Config ---
        self.TIMEOUT_SECONDS = 30
        self.last_activity = time.time()
        self.running = True
        self.is_on = True
        self.mock_mode = not HARDWARE_AVAILABLE

        if self.mock_mode:
            print("LCD: Running in mock mode (no physical display)")
            # Don't initialize hardware
            self.disp = None
            self.height = 170
            self.width = 320
            self.image = None
            self.draw = None
            self.font = None
        else:
            # --- Pinout (Fixed for Pi 5 & NFC Compatibility) ---
            # CS=Pin 18 (GPIO 24), DC=Pin 13 (GPIO 27), RST=Pin 15 (GPIO 22)
            cs_pin = digitalio.DigitalInOut(board.D24)
            dc_pin = digitalio.DigitalInOut(board.D27)
            reset_pin = digitalio.DigitalInOut(board.D22)
            spi = board.SPI()

            # --- Display Init ---
            self.disp = ST7789(
                spi,
                cs=cs_pin, dc=dc_pin, rst=reset_pin,
                baudrate=60000000,
                width=170, height=320,
                x_offset=35, y_offset=0
            )

            # --- Drawing Context ---
            self.height = self.disp.width   # 170
            self.width = self.disp.height   # 320
            self.image = Image.new("RGB", (self.width, self.height))
            self.draw = ImageDraw.Draw(self.image)
            
            # Load Font
            try:
                self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            except IOError:
                self.font = ImageFont.load_default()

        # --- Start Background Timer ---
        self.thread = threading.Thread(target=self._auto_off_worker, daemon=True)
        self.thread.start()

    def show_message(self, text):
        """
        Displays text on the screen and resets the 30s timer.
        """
        self.last_activity = time.time() # Reset timer
        self.is_on = True

        if self.mock_mode:
            print(f"[LCD Mock] Display: {text}")
            return

        # Clear background (Black)
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
        
        # Draw Text (Centered approximately)
        self.draw.text((10, 60), str(text), font=self.font, fill=(255, 255, 255))
        
        # Push to display
        self.disp.image(self.image, rotation=90)

    def clear(self):
        """
        Manually clears the screen immediately.
        """
        if self.mock_mode:
            print("[LCD Mock] Screen cleared")
            self.is_on = False
            return
            
        # Draw a black rectangle over the whole screen
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
        self.disp.image(self.image, rotation=90)
        self.is_on = False

    def _auto_off_worker(self):
        """Background thread that turns screen black after 30s idle."""
        while self.running:
            time.sleep(1)
            # Check if 30s have passed since last activity
            if self.is_on and (time.time() - self.last_activity > self.TIMEOUT_SECONDS):
                self.clear() # Re-use the clear function
    
    def cleanup(self):
        self.running = False