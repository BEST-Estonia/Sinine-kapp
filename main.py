# main.py
import pygame
import pygame_gui
import sys
import os

# Import your custom modules (the "drawer")
import modules.gui_manager as gui
import modules.hardware as hardware
import modules.database_manager as db

# Set the working directory to the script's location
# This is crucial so it can find the theme.json file
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class SmartCabinetApp:
    def __init__(self):
        pygame.init()
        
        # --- Config ---
        self.screen_width = 800  # Set to your 7" screen size
        self.screen_height = 480
        
        # --- Setup Pygame ---
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.clock = pygame.time.Clock()
        self.is_running = True
        
        # --- Setup GUI ---
        # We pass 'self' so the GUI can call this app's functions
        self.gui = gui.GUIManager(self.screen_width, self.screen_height, self)

        # --- Setup Hardware & DB ---
        self.db = db.DatabaseManager("cabinet.db")
        self.hardware = hardware.HardwareManager()
        
        # --- Initial State ---
        print("Smart Cabinet Initialized.")
        self.gui.show_screen("welcome") # Show the "Scan Card" screen

    def run(self):
        """The main application loop"""
        while self.is_running:
            time_delta = self.clock.tick(60) / 1000.0
            
            # --- Event Handling ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                
                # Let the GUI handle its own events
                self.gui.process_event(event)

            # --- Update ---
            self.gui.update(time_delta)
            
            # --- Draw ---
            self.screen.fill(pygame.Color('#f0f0f0')) # Background
            self.gui.draw_ui(self.screen)
            pygame.display.update()

    # --- CALLBACK FUNCTIONS ---
    # These functions are called *by your GUI* or *by your hardware*
    
    def on_rfid_scan(self, card_id):
        """Called by the hardware module when a card is scanned."""
        print(f"Main App: Card scanned: {card_id}")
        if self.db.check_user_auth(card_id):
            print("User authorized.")
            self.hardware.unlock_door()
            self.gui.show_screen("scan_item")
        else:
            print("User NOT authorized.")
            self.gui.show_screen("access_denied")

    def on_qr_scan(self, qr_code):
        """Called by the GUI when a QR code is 'entered'."""
        print(f"Main App: QR code scanned: {qr_code}")
        # 1. Log in database
        # 2. Update GUI
        self.gui.show_screen("thank_you")
        
    def on_door_close(self):
        """Called by the hardware module when the switch is closed."""
        print("Main App: Door closed.")
        self.gui.show_screen("welcome")

if __name__ == "__main__":
    app = SmartCabinetApp()
    app.run()
