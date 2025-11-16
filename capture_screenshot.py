#!/usr/bin/env python3
"""
Simple script to capture screenshots of the main menu screen
"""
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import sys
import pygame
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

import config
from hardware.mock_rfid import MockRFIDReader
from hardware.mock_scales import MockScale
from hardware.mock_qr import MockQRScanner
from hardware.mock_camera import MockCamera
from database import DatabaseManager
from screen_manager import ScreenManager
from screens import MainMenuScreen
from assets import get_asset_manager

def capture_main_menu():
    """Capture a screenshot of the main menu"""
    pygame.init()
    pygame.font.init()
    
    # Initialize asset manager
    assets = get_asset_manager()
    assets.preload_assets()
    
    # Create display
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    
    # Create mock hardware
    rfid = MockRFIDReader()
    qr = MockQRScanner()
    cam = MockCamera()
    scale_top = MockScale(level="top")
    scale_bottom = MockScale(level="bottom")
    
    # Create UI manager mock
    class UIManager:
        def __init__(self):
            self.width = config.SCREEN_WIDTH
            self.height = config.SCREEN_HEIGHT
            self.rfid = rfid
            self.qr = qr
            self.camera = cam
            self.scale_top = scale_top
            self.scale_bottom = scale_bottom
            self.db = DatabaseManager()
    
    ui = UIManager()
    screen_manager = ScreenManager()
    
    # Create main menu screen
    main_screen = MainMenuScreen(ui, screen_manager)
    screen_manager.go_to(main_screen)
    
    # Render the screen
    main_screen.draw(screen)
    
    # Save screenshot
    output_path = Path(__file__).parent / "screenshot_main_menu.png"
    pygame.image.save(screen, str(output_path))
    print(f"✓ Screenshot saved to {output_path}")
    
    pygame.quit()
    ui.db.close()

if __name__ == "__main__":
    capture_main_menu()
