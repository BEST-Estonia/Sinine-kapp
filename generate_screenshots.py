#!/usr/bin/env python3
"""
Screenshot generator for the Smart Cupboard application
Creates screenshots of all screens for documentation
"""
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import sys
from pathlib import Path
import pygame

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from database import DatabaseManager
from hardware.mock_rfid import MockRFIDReader
from hardware.mock_qr import MockQRScanner
from hardware.mock_scales import MockScale
from hardware.mock_camera import MockCamera
from screens import *


class MockUI:
    """Mock UI manager for screenshot generation"""
    def __init__(self):
        pygame.init()
        self.width = 600
        self.height = 1024
        self.screen = pygame.display.set_mode((600, 1024))
        self.rfid = MockRFIDReader()
        self.qr = MockQRScanner()
        self.camera = MockCamera()
        self.scale_top = MockScale("top")
        self.scale_bottom = MockScale("bottom")
        self.db = DatabaseManager()


def save_screenshot(screen, filename):
    """Save a screenshot of the given screen"""
    output_dir = Path("screenshots")
    output_dir.mkdir(exist_ok=True)
    
    pygame.image.save(screen, str(output_dir / filename))
    print(f"  ✓ Saved {filename}")


def generate_screenshots():
    """Generate screenshots for all screens"""
    print("Generating screenshots...")
    print()
    
    ui = MockUI()
    
    # Get sample data
    admin_user = ui.db.get_user_by_card("1")
    regular_user = ui.db.get_user_by_card("2")
    items = ui.db.get_all_items()
    sample_basket = [
        {'qr_code': items[0]['qr_code'], 'name': items[0]['name'], 'quantity': 2},
        {'qr_code': items[1]['qr_code'], 'name': items[1]['name'], 'quantity': 1},
    ]
    
    # 1. Main Menu
    print("1. Main Menu")
    screen = MainMenuScreen(ui)
    screen.draw(ui.screen)
    save_screenshot(ui.screen, "01_main_menu.png")
    
    # 2. Card Scan (for borrowing)
    print("2. Card Scan - Borrow")
    screen = CardScanScreen(ui, "Open Doors - Scan Card", "qr_scan_borrow")
    screen.status = "Please scan your card..."
    screen.draw(ui.screen)
    save_screenshot(ui.screen, "02_card_scan_borrow.png")
    
    # 3. Card Scan (success)
    print("3. Card Scan - Success")
    screen = CardScanScreen(ui, "Open Doors - Scan Card", "qr_scan_borrow")
    screen.user_info = regular_user
    screen.status = f"Welcome, {regular_user['name']}!"
    screen.scanned = True
    screen.draw(ui.screen)
    save_screenshot(ui.screen, "03_card_scan_success.png")
    
    # 4. User Registration
    print("4. User Registration")
    screen = RegisterUserScreen(ui, "999")
    screen.input_box.set_text("John Doe")
    screen.draw(ui.screen)
    save_screenshot(ui.screen, "04_register_user.png")
    
    # 5. QR Scan (empty basket)
    print("5. QR Scan - Empty Basket")
    screen = QRScanScreen(ui, regular_user, 'borrow')
    screen.draw(ui.screen)
    save_screenshot(ui.screen, "05_qr_scan_empty.png")
    
    # 6. QR Scan (with items)
    print("6. QR Scan - With Items")
    screen = QRScanScreen(ui, regular_user, 'borrow')
    screen.basket = sample_basket.copy()
    screen.status = f"Added: {items[1]['name']}"
    screen.draw(ui.screen)
    save_screenshot(ui.screen, "06_qr_scan_items.png")
    
    # 7. Basket Confirmation
    print("7. Basket Confirmation")
    screen = BasketScreen(ui, regular_user, sample_basket.copy(), 'borrow')
    screen.draw(ui.screen)
    save_screenshot(ui.screen, "07_basket_confirm.png")
    
    # 8. Thank You (Borrow)
    print("8. Thank You - Borrow")
    screen = ThankYouScreen(ui, regular_user, sample_basket.copy(), 'borrow')
    screen.draw(ui.screen)
    save_screenshot(ui.screen, "08_thank_you_borrow.png")
    
    # 9. Thank You (Return)
    print("9. Thank You - Return")
    screen = ThankYouScreen(ui, regular_user, sample_basket.copy(), 'return')
    screen.draw(ui.screen)
    save_screenshot(ui.screen, "09_thank_you_return.png")
    
    # 10. Admin Main Panel
    print("10. Admin Main Panel")
    screen = AdminMainScreen(ui, admin_user)
    screen.draw(ui.screen)
    save_screenshot(ui.screen, "10_admin_main.png")
    
    # 11. Admin Users List
    print("11. Admin Users List")
    screen = AdminUsersScreen(ui, admin_user)
    screen.draw(ui.screen)
    save_screenshot(ui.screen, "11_admin_users.png")
    
    # 12. Admin User Details
    print("12. Admin User Details")
    # Create some sample borrows for display
    ui.db.borrow_item(regular_user['id'], items[0]['qr_code'])
    ui.db.borrow_item(regular_user['id'], items[1]['qr_code'])
    
    screen = AdminUserDetailsScreen(ui, admin_user, regular_user['id'])
    screen.draw(ui.screen)
    save_screenshot(ui.screen, "12_admin_user_details.png")
    
    # 13. Admin Inventory
    print("13. Admin Inventory Manager")
    screen = AdminInventoryScreen(ui, admin_user)
    screen.draw(ui.screen)
    save_screenshot(ui.screen, "13_admin_inventory.png")
    
    # 14. Admin Logs
    print("14. Admin System Logs")
    screen = AdminLogsScreen(ui, admin_user)
    screen.draw(ui.screen)
    save_screenshot(ui.screen, "14_admin_logs.png")
    
    # 15. Stock/Inventory (public view)
    print("15. Stock/Inventory View")
    screen = AdminInventoryScreen(ui, {'name': 'Guest', 'id': 0, 'is_admin': False})
    screen.draw(ui.screen)
    save_screenshot(ui.screen, "15_stock_inventory.png")
    
    ui.db.close()
    pygame.quit()
    
    print()
    print("=" * 60)
    print("✓ All screenshots generated in ./screenshots/")
    print("=" * 60)


if __name__ == "__main__":
    generate_screenshots()
