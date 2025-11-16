#!/usr/bin/env python3
"""
Generate screenshots of all main screens
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import pygame
from screens import (
    MainMenuScreen,
    CardScanScreen,
    RegisterPromptScreen,
    QRScanScreen,
    FinalizeScreen,
    ThankYouScreen,
    InventoryViewScreen,
    AdminMainScreen,
)
from screen_manager import ScreenManager
from database import DatabaseManager
from hardware.mock_rfid import MockRFIDReader
from hardware.mock_qr import MockQRScanner
from hardware.mock_scales import MockScale
from hardware.mock_camera import MockCamera


class MockUI:
    """Mock UI for screenshots"""
    def __init__(self):
        pygame.init()
        self.width = 600
        self.height = 1024
        self.screen = pygame.display.set_mode((600, 1024))
        self.db = DatabaseManager()
        self.rfid = MockRFIDReader()
        self.qr = MockQRScanner()
        self.camera = MockCamera()
        self.scale_top = MockScale(level="top")
        self.scale_bottom = MockScale(level="bottom")


def save_screenshot(screen, filename):
    """Save a screenshot of the screen"""
    surface = pygame.Surface((600, 1024))
    screen.draw(surface)
    
    # Create screenshots directory
    screenshots_dir = Path(__file__).parent / "screenshots"
    screenshots_dir.mkdir(exist_ok=True)
    
    filepath = screenshots_dir / filename
    pygame.image.save(surface, str(filepath))
    print(f"  ✓ Saved {filename}")


def main():
    """Generate screenshots"""
    print("Generating screenshots...")
    
    ui = MockUI()
    sm = ScreenManager()
    
    # Get sample user
    user = ui.db.get_user_by_card("1")
    
    # 1. Main Menu Screen
    main = MainMenuScreen(ui, sm)
    save_screenshot(main, "01_main_menu.png")
    
    # 2. Card Scan Screen
    card_scan = CardScanScreen(ui, sm, "Open Doors - Scan Card", "borrow")
    save_screenshot(card_scan, "02_card_scan.png")
    
    # 3. Registration Prompt
    reg_prompt = RegisterPromptScreen(ui, sm, "999", "borrow")
    save_screenshot(reg_prompt, "03_registration_prompt.png")
    
    # 4. QR Scan Screen with items
    qr_scan = QRScanScreen(ui, sm, user, "borrow")
    qr_scan.basket = [
        {'qr_code': 'DRINK001', 'name': 'Coca Cola', 'quantity': 2},
        {'qr_code': 'DRINK002', 'name': 'Sprite', 'quantity': 1},
        {'qr_code': 'DRINK003', 'name': 'Orange Juice', 'quantity': 1},
    ]
    qr_scan._build_item_buttons()
    save_screenshot(qr_scan, "04_qr_scan_with_basket.png")
    
    # 5. Finalize Screen
    finalize = FinalizeScreen(ui, sm, user, qr_scan.basket, "borrow")
    save_screenshot(finalize, "05_finalize.png")
    
    # 6. Thank You Screen
    thank_you = ThankYouScreen(ui, sm, user, qr_scan.basket, "borrow")
    save_screenshot(thank_you, "06_thank_you.png")
    
    # 7. Inventory View
    inv_view = InventoryViewScreen(ui, sm)
    save_screenshot(inv_view, "07_inventory_view.png")
    
    # 8. Admin Main
    admin_main = AdminMainScreen(ui, sm, user)
    save_screenshot(admin_main, "08_admin_main.png")
    
    print("\n✓ All screenshots generated successfully!")
    print(f"Screenshots saved to: {Path(__file__).parent / 'screenshots'}")
    
    pygame.quit()


if __name__ == "__main__":
    main()
