# src/main.py
"""
Main entry point for the Smart Cupboard application
Complete Pygame touchscreen app with stack-based screen management
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

# Import screen manager
from screen_manager import ScreenManager

# Import screens
from screens import (
    MainMenuScreen,
    CardScanScreen,
    RegisterPromptScreen,
    RegisterUserScreen,
    QRScanScreen,
    BasketScreen,
    FinalizeScreen,
    ThankYouScreen,
    InventoryViewScreen,
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
        
        # Screen management with stack-based ScreenManager
        self.screen_manager = ScreenManager()
        
        # Create and load main menu as root screen
        main_screen = MainMenuScreen(self, self.screen_manager)
        self.screen_manager.go_to(main_screen)
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds
            
            # Handle events - delegate to screen manager
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                
                # Let screen manager delegate to current screen
                self.screen_manager.handle_event(event)
            
            # Update current screen through screen manager
            self.screen_manager.update(dt)
            
            # Render current screen through screen manager
            self.screen_manager.render(self.screen)
            
            pygame.display.flip()
        
        # Cleanup
        self.db.close()
        pygame.quit()
        sys.exit()


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
