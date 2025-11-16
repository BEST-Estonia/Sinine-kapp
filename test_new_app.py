#!/usr/bin/env python3
"""
Test script for the new modular Smart Cupboard application
Tests imports, database, and screen instantiation
"""
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'  # Use dummy video driver for testing

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_imports():
    """Test all imports"""
    print("Testing imports...")
    
    from database import DatabaseManager
    print("  ✓ DatabaseManager")
    
    from ui import Button, InputBox, OnScreenKeyboard
    print("  ✓ UI components")
    
    from screens import (
        BaseScreen, MainMenuScreen, CardScanScreen, RegisterUserScreen,
        QRScanScreen, BasketScreen, ThankYouScreen,
        AdminMainScreen, AdminUsersScreen, AdminUserDetailsScreen,
        AdminInventoryScreen, AdminLogsScreen
    )
    print("  ✓ All screen classes")
    
    from hardware.mock_rfid import MockRFIDReader
    from hardware.mock_qr import MockQRScanner
    from hardware.mock_scales import MockScale
    from hardware.mock_camera import MockCamera
    print("  ✓ Hardware mocks")
    
    return True


def test_database():
    """Test database operations"""
    print("\nTesting database...")
    
    from database import DatabaseManager
    db = DatabaseManager()
    
    # Test users
    users = db.get_all_users()
    print(f"  ✓ Found {len(users)} users")
    assert len(users) >= 3, "Should have at least 3 sample users"
    
    # Test items
    items = db.get_all_items()
    print(f"  ✓ Found {len(items)} items")
    assert len(items) >= 7, "Should have at least 7 sample items"
    
    # Test admin user
    admin = db.get_user_by_card("1")
    assert admin is not None, "Admin user should exist"
    assert admin.get('is_admin') == 1, "User 1 should be admin"
    print(f"  ✓ Admin user: {admin['name']}")
    
    # Test due date calculation
    due_date = db.calculate_due_date()
    print(f"  ✓ Due date calculation: {due_date}")
    
    # Test borrow/return
    user_id = admin['id']
    item = items[0]
    
    original_stock = db.get_stock(item['qr_code'])
    borrow_id = db.borrow_item(user_id, item['qr_code'])
    new_stock = db.get_stock(item['qr_code'])
    assert new_stock == original_stock - 1, "Stock should decrease on borrow"
    print(f"  ✓ Borrow transaction created (ID: {borrow_id})")
    
    db.return_item(user_id, item['qr_code'])
    returned_stock = db.get_stock(item['qr_code'])
    assert returned_stock == original_stock, "Stock should return to original"
    print(f"  ✓ Return transaction processed")
    
    db.close()
    return True


def test_screens():
    """Test screen instantiation"""
    print("\nTesting screen instantiation...")
    
    import pygame
    from database import DatabaseManager
    from hardware.mock_rfid import MockRFIDReader
    from hardware.mock_qr import MockQRScanner
    from hardware.mock_scales import MockScale
    from hardware.mock_camera import MockCamera
    
    # Mock UI manager
    class MockUI:
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
    
    ui = MockUI()
    
    # Test main menu
    from screens import MainMenuScreen
    screen = MainMenuScreen(ui)
    assert len(screen.buttons) == 4, "Main menu should have 4 buttons"
    print("  ✓ MainMenuScreen")
    
    # Test card scan
    from screens import CardScanScreen
    screen = CardScanScreen(ui, "Test", "main")
    assert len(screen.buttons) == 1, "Card scan should have 1 button"
    print("  ✓ CardScanScreen")
    
    # Test register user
    from screens import RegisterUserScreen
    screen = RegisterUserScreen(ui, "999")
    assert screen.input_box is not None, "Should have input box"
    assert screen.keyboard is not None, "Should have keyboard"
    print("  ✓ RegisterUserScreen")
    
    # Test QR scan
    from screens import QRScanScreen
    user_info = ui.db.get_user_by_card("1")
    screen = QRScanScreen(ui, user_info, 'borrow')
    assert len(screen.buttons) == 3, "QR scan should have 3 buttons"
    print("  ✓ QRScanScreen")
    
    # Test basket
    from screens import BasketScreen
    basket = [{'qr_code': 'TEST', 'name': 'Test Item', 'quantity': 1}]
    screen = BasketScreen(ui, user_info, basket, 'borrow')
    assert len(screen.basket) == 1, "Basket should have 1 item"
    print("  ✓ BasketScreen")
    
    # Test thank you
    from screens import ThankYouScreen
    screen = ThankYouScreen(ui, user_info, basket, 'borrow')
    print("  ✓ ThankYouScreen")
    
    # Test admin screens
    from screens import AdminMainScreen, AdminUsersScreen, AdminInventoryScreen, AdminLogsScreen
    screen = AdminMainScreen(ui, user_info)
    print("  ✓ AdminMainScreen")
    
    screen = AdminUsersScreen(ui, user_info)
    print("  ✓ AdminUsersScreen")
    
    screen = AdminInventoryScreen(ui, user_info)
    print("  ✓ AdminInventoryScreen")
    
    screen = AdminLogsScreen(ui, user_info)
    print("  ✓ AdminLogsScreen")
    
    ui.db.close()
    pygame.quit()
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("Smart Cupboard - New Architecture Test Suite")
    print("=" * 60)
    
    try:
        test_imports()
        test_database()
        test_screens()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
