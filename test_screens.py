#!/usr/bin/env python3
"""
Test script to verify screen navigation and basic functionality
"""
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'  # Use dummy video driver for testing

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import pygame
from screens import (
    MainMenuScreen,
    CardScanScreen,
    RegisterPromptScreen,
    RegisterUserScreen,
    QRScanScreen,
    FinalizeScreen,
    ThankYouScreen,
    InventoryViewScreen,
    AdminMainScreen,
)
from screen_manager import ScreenManager
from database import DatabaseManager
from hardware.mock_rfid import MockRFIDReader


class MockUI:
    """Mock UI for testing"""
    def __init__(self):
        pygame.init()
        self.width = 600
        self.height = 1024
        self.screen = pygame.display.set_mode((600, 1024))
        self.db = DatabaseManager()
        self.rfid = MockRFIDReader()


def test_screen_creation():
    """Test that all screens can be created"""
    print("Testing screen creation...")
    
    ui = MockUI()
    sm = ScreenManager()
    
    # Test main menu
    main = MainMenuScreen(ui, sm)
    assert main is not None
    print("  ✓ MainMenuScreen created")
    
    # Test card scan
    card_scan = CardScanScreen(ui, sm, "Test", "borrow")
    assert card_scan is not None
    print("  ✓ CardScanScreen created")
    
    # Test register prompt
    reg_prompt = RegisterPromptScreen(ui, sm, "test_card", "borrow")
    assert reg_prompt is not None
    print("  ✓ RegisterPromptScreen created")
    
    # Test register user
    reg_user = RegisterUserScreen(ui, sm, "test_card")
    assert reg_user is not None
    print("  ✓ RegisterUserScreen created")
    
    # Test QR scan
    user = ui.db.get_user_by_card("1")
    qr_scan = QRScanScreen(ui, sm, user, "borrow")
    assert qr_scan is not None
    print("  ✓ QRScanScreen created")
    
    # Test finalize
    basket = [{'qr_code': 'DRINK001', 'name': 'Test Item', 'quantity': 1}]
    finalize = FinalizeScreen(ui, sm, user, basket, "borrow")
    assert finalize is not None
    print("  ✓ FinalizeScreen created")
    
    # Test thank you
    thank_you = ThankYouScreen(ui, sm, user, basket, "borrow")
    assert thank_you is not None
    print("  ✓ ThankYouScreen created")
    
    # Test inventory view
    inv_view = InventoryViewScreen(ui, sm)
    assert inv_view is not None
    print("  ✓ InventoryViewScreen created")
    
    # Test admin main
    admin_main = AdminMainScreen(ui, sm, user)
    assert admin_main is not None
    print("  ✓ AdminMainScreen created")
    
    print("All screens created successfully!")


def test_screen_manager():
    """Test screen manager navigation"""
    print("\nTesting screen manager navigation...")
    
    ui = MockUI()
    sm = ScreenManager()
    
    # Test push/pop
    main = MainMenuScreen(ui, sm)
    sm.go_to(main)
    assert sm.current() == main
    print("  ✓ go_to works")
    
    card = CardScanScreen(ui, sm, "Test", "borrow")
    sm.push(card)
    assert sm.current() == card
    print("  ✓ push works")
    
    sm.pop()
    assert sm.current() == main
    print("  ✓ pop works")
    
    print("Screen manager navigation works!")


def test_database():
    """Test database operations"""
    print("\nTesting database...")
    
    db = DatabaseManager()
    
    # Test get admin user
    admin = db.get_user_by_card("1")
    assert admin is not None
    assert admin['is_admin'] == 1
    print("  ✓ Admin user found")
    
    # Test get regular user
    user = db.get_user_by_card("2")
    assert user is not None
    assert user['is_admin'] == 0
    print("  ✓ Regular user found")
    
    # Test get items
    items = db.get_all_items()
    assert len(items) > 0
    print(f"  ✓ Found {len(items)} items")
    
    db.close()
    print("Database tests passed!")


if __name__ == "__main__":
    try:
        test_screen_creation()
        test_screen_manager()
        test_database()
        print("\n✓ All tests passed!")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
