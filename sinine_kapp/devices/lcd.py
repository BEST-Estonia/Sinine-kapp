"""Small ST7789 LCD display used for operational feedback."""

import time
import threading
import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display.st7789 import ST7789


class LCD:
    """Thin drawing wrapper around the ST7789 display."""

    def __init__(self):
        # Runtime state for the auto-off worker.
        self.TIMEOUT_SECONDS = 30
        self.last_activity = time.time()
        self.running = True
        self.is_on = True
        self._cleaned_up = False

        # --- Pinout (Fixed for Pi 5 & NFC Compatibility) ---
        # CS=Pin 18 (GPIO 24), DC=Pin 13 (GPIO 27), RST=Pin 15 (GPIO 22)
        self.cs_pin = digitalio.DigitalInOut(board.D24)
        self.dc_pin = digitalio.DigitalInOut(board.D27)
        self.reset_pin = digitalio.DigitalInOut(board.D22)
        self.spi = board.SPI()
        
        # Backlight control on GPIO 26
        self.backlight = digitalio.DigitalInOut(board.D26)
        self.backlight.direction = digitalio.Direction.OUTPUT
        self.backlight.value = False # Start with backlight OFF

        self.disp = ST7789(
            self.spi,
            cs=self.cs_pin, dc=self.dc_pin, rst=self.reset_pin,
            baudrate=60000000,
            width=170, height=320,
            x_offset=35, y_offset=0
        )

        # PIL image buffer that gets pushed to the physical LCD.
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

    def set_backlight(self, state):
        """Turn the LCD backlight on or off."""
        self.backlight.value = state

    def show_message(self, text):
        """
        Displays text on the screen and resets the 30s timer.
        """
        self.last_activity = time.time() # Reset timer
        self.is_on = True

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
        """Stop the background worker and release display GPIO/SPI resources."""
        if self._cleaned_up:
            return

        self.running = False
        try:
            self.thread.join(timeout=2)
        except Exception:
            pass

        try:
            self.clear()
        except Exception:
            pass

        try:
            self.backlight.value = False
        except Exception:
            pass

        for resource_name in ("backlight", "reset_pin", "dc_pin", "cs_pin", "spi"):
            resource = getattr(self, resource_name, None)
            if resource is None:
                continue

            deinit = getattr(resource, "deinit", None)
            if callable(deinit):
                try:
                    deinit()
                except Exception:
                    pass

        self._cleaned_up = True
