# src/app/ui_pygame.py
import pygame
import sys
from pathlib import Path
from .screens import (
    MainScreen, CardScanScreen, OpenDoorsScreen, 
    ReturnDrinkScreen, AdminScreen, StockInventoryScreen
)
from database import UserDatabase

SCREEN_W, SCREEN_H = 800, 480  # typical 7" touchscreen resolution
FPS = 30


class TouchUI:
    """Main UI manager that coordinates all screens"""
    
    def __init__(self, rfid, qr, camera, scale_top, scale_bottom):
        pygame.init()
        pygame.font.init()
        
        self.width = SCREEN_W
        self.height = SCREEN_H
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Smart Cupboard")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.font = pygame.font.SysFont(None, 36)
        self.large_font = pygame.font.SysFont(None, 48)
        
        # Hardware references
        self.rfid = rfid
        self.qr = qr
        self.camera = camera
        self.scale_top = scale_top
        self.scale_bottom = scale_bottom
        
        # Database
        self.db = UserDatabase()
        
        # Screen management
        self.current_screen = None
        self.screen_name = "main"
        self._load_screen("main")
    
    def _load_screen(self, screen_name, **kwargs):
        """Load a new screen by name"""
        self.screen_name = screen_name
        
        if screen_name == "main":
            self.current_screen = MainScreen(self)
        elif screen_name == "open_doors":
            # First show card scan screen
            self.current_screen = CardScanScreen(
                self, 
                "Open Doors - Scan Card",
                "open_doors_unlocked"
            )
        elif screen_name == "open_doors_unlocked":
            # After successful scan, show the unlocked door screen
            user_info = kwargs.get("user_info")
            if user_info:
                self.current_screen = OpenDoorsScreen(self, user_info)
            else:
                self.current_screen = MainScreen(self)
        elif screen_name == "return_drink":
            self.current_screen = CardScanScreen(
                self,
                "Return Drink - Scan Card",
                "return_drink_confirmed"
            )
        elif screen_name == "return_drink_confirmed":
            user_info = kwargs.get("user_info")
            if user_info:
                self.current_screen = ReturnDrinkScreen(self, user_info)
            else:
                self.current_screen = MainScreen(self)
        elif screen_name == "admin":
            self.current_screen = CardScanScreen(
                self,
                "Admin Panel - Scan Card",
                "admin_panel"
            )
        elif screen_name == "admin_panel":
            user_info = kwargs.get("user_info")
            if user_info:
                self.current_screen = AdminScreen(self, user_info)
            else:
                self.current_screen = MainScreen(self)
        elif screen_name == "stock_inventory":
            # Stock/Inventory doesn't require card scan
            self.current_screen = StockInventoryScreen(self)
        else:
            self.current_screen = MainScreen(self)
    
    def run(self):
        """Main game loop"""
        while True:
            self.clock.tick(FPS)
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.db.close()
                    pygame.quit()
                    sys.exit()
                
                # Let current screen handle the event
                result = self.current_screen.handle_event(event)
                if result:
                    self._handle_screen_result(result)
            
            # Update screen state
            result = self.current_screen.update()
            if result:
                self._handle_screen_result(result)
            
            # Draw
            self.current_screen.draw(self.screen)
            pygame.display.flip()
    
    def _handle_screen_result(self, result):
        """Handle screen transitions and actions"""
        if isinstance(result, str):
            # Screen transition
            if result == "main":
                self._load_screen("main")
            elif result == "open_doors_unlocked":
                # Get user info from the card scan screen
                if hasattr(self.current_screen, 'user_info') and self.current_screen.user_info:
                    self._load_screen("open_doors_unlocked", user_info=self.current_screen.user_info)
                else:
                    self._load_screen("main")
            elif result == "return_drink_confirmed":
                if hasattr(self.current_screen, 'user_info') and self.current_screen.user_info:
                    self._load_screen("return_drink_confirmed", user_info=self.current_screen.user_info)
                else:
                    self._load_screen("main")
            elif result == "admin_panel":
                if hasattr(self.current_screen, 'user_info') and self.current_screen.user_info:
                    self._load_screen("admin_panel", user_info=self.current_screen.user_info)
                else:
                    self._load_screen("main")
            else:
                self._load_screen(result)
