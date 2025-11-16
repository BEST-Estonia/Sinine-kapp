# src/main_new.py
"""
Main entry point for the Smart Cupboard application
Complete Pygame touchscreen app with modular architecture
"""
import pygame
import sys
from pathlib import Path

# Import hardware
from hardware.mock_rfid import MockRFIDReader
from hardware.mock_scales import MockScale
from hardware.mock_qr import MockQRScanner
from hardware.mock_camera import MockCamera

# Import database
from database import DatabaseManager

# Import screens
from screens import (
    MainMenuScreen,
    CardScanScreen,
    RegisterUserScreen,
    QRScanScreen,
    BasketScreen,
    ThankYouScreen,
    AdminMainScreen,
    AdminUsersScreen,
    AdminUserDetailsScreen,
    AdminInventoryScreen,
    AdminLogsScreen,
)

# Configuration
SCREEN_W, SCREEN_H = 600, 1024  # Portrait orientation
FPS = 30


class SmartCupboardUI:
    """Main UI manager for the Smart Cupboard application"""
    
    def __init__(self, rfid, qr, camera, scale_top, scale_bottom):
        pygame.init()
        pygame.font.init()
        
        self.width = SCREEN_W
        self.height = SCREEN_H
        
        # Fullscreen, no borders
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.NOFRAME)
        pygame.display.set_caption("Smart Cupboard")
        self.clock = pygame.time.Clock()
        
        # Hardware references
        self.rfid = rfid
        self.qr = qr
        self.camera = camera
        self.scale_top = scale_top
        self.scale_bottom = scale_bottom
        
        # Database
        self.db = DatabaseManager()
        
        # Screen management
        self.current_screen = None
        self.screen_name = "main"
        self.screen_data = {}
        
        # Load main menu
        self._load_screen("main")
    
    def _load_screen(self, screen_name, **kwargs):
        """Load a screen by name with parameters"""
        self.screen_name = screen_name
        self.screen_data = kwargs
        
        # Map screen names to classes
        if screen_name == "main":
            self.current_screen = MainMenuScreen(self)
        
        elif screen_name == "card_scan_borrow":
            self.current_screen = CardScanScreen(self, "Open Doors - Scan Card", "qr_scan_borrow")
        
        elif screen_name == "card_scan_return":
            self.current_screen = CardScanScreen(self, "Return Drink - Scan Card", "qr_scan_return")
        
        elif screen_name == "card_scan_admin":
            self.current_screen = CardScanScreen(self, "Admin Panel - Scan Card", "admin_main")
        
        elif screen_name == "register_user":
            card_id = kwargs.get('card_id')
            self.current_screen = RegisterUserScreen(self, card_id)
        
        elif screen_name == "qr_scan_borrow":
            user_info = kwargs.get('user_info')
            self.current_screen = QRScanScreen(self, user_info, action='borrow')
        
        elif screen_name == "qr_scan_return":
            user_info = kwargs.get('user_info')
            self.current_screen = QRScanScreen(self, user_info, action='return')
        
        elif screen_name == "basket":
            user_info = kwargs.get('user_info')
            basket = kwargs.get('basket', [])
            action = kwargs.get('action', 'borrow')
            self.current_screen = BasketScreen(self, user_info, basket, action)
        
        elif screen_name == "thank_you":
            user_info = kwargs.get('user_info')
            basket = kwargs.get('basket', [])
            action = kwargs.get('action', 'borrow')
            self.current_screen = ThankYouScreen(self, user_info, basket, action)
        
        elif screen_name == "stock_inventory":
            # Show inventory (same as admin inventory but read-only)
            # For now, redirect to admin inventory
            # In production, you'd create a separate read-only inventory screen
            user_info = kwargs.get('user_info', {'name': 'Guest', 'id': 0, 'is_admin': False})
            self.current_screen = AdminInventoryScreen(self, user_info)
        
        elif screen_name == "admin_main":
            user_info = kwargs.get('user_info')
            self.current_screen = AdminMainScreen(self, user_info)
        
        elif screen_name == "admin_users":
            user_info = kwargs.get('user_info')
            self.current_screen = AdminUsersScreen(self, user_info)
        
        elif screen_name == "admin_user_details":
            admin_info = kwargs.get('admin_info')
            user_id = kwargs.get('user_id')
            self.current_screen = AdminUserDetailsScreen(self, admin_info, user_id)
        
        elif screen_name == "admin_inventory":
            user_info = kwargs.get('user_info')
            self.current_screen = AdminInventoryScreen(self, user_info)
        
        elif screen_name == "admin_logs":
            user_info = kwargs.get('user_info')
            self.current_screen = AdminLogsScreen(self, user_info)
        
        elif screen_name == "qr_scan":
            # Generic QR scan - determine action from kwargs
            user_info = kwargs.get('user_info')
            action = kwargs.get('action', 'borrow')
            self.current_screen = QRScanScreen(self, user_info, action)
        
        else:
            # Unknown screen, go to main
            self.current_screen = MainMenuScreen(self)
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            self.clock.tick(FPS)
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                
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
        
        # Cleanup
        self.db.close()
        pygame.quit()
        sys.exit()
    
    def _handle_screen_result(self, result):
        """Handle screen transitions"""
        if isinstance(result, str):
            # Simple screen transition
            self._load_screen(result)
        elif isinstance(result, tuple) and len(result) == 2:
            # Screen transition with data
            screen_name, kwargs = result
            self._load_screen(screen_name, **kwargs)


def main():
    """Main entry point"""
    # Instantiate mock hardware
    rfid = MockRFIDReader()
    qr = MockQRScanner()
    cam = MockCamera()
    scale_top = MockScale(level="top")
    scale_bottom = MockScale(level="bottom")
    
    # Create and run UI
    ui = SmartCupboardUI(
        rfid=rfid,
        qr=qr,
        camera=cam,
        scale_top=scale_top,
        scale_bottom=scale_bottom
    )
    ui.run()


if __name__ == "__main__":
    main()
