#!/usr/bin/env python3
"""
Integration test for the Pygame UI
Tests the complete workflow without requiring user interaction
"""
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'  # Use dummy video driver for testing

import sys
import pygame
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from app.ui_pygame import TouchUI
from app.screens import (
    MainScreen, CardScanScreen, OpenDoorsScreen, 
    ReturnDrinkScreen, AdminScreen, StockInventoryScreen
)
from database import UserDatabase
from hardware.mock_rfid import MockRFIDReader
from hardware.mock_scales import MockScale
from hardware.mock_qr import MockQRScanner
from hardware.mock_camera import MockCamera


def test_database():
    """Test database operations"""
    print("Testing database...")
    db = UserDatabase()
    
    # Test getting users
    users = db.get_all_users()
    assert len(users) == 3, f"Expected 3 users, got {len(users)}"
    print(f"  ✓ Found {len(users)} users")
    
    # Test getting specific user
    user = db.get_user_by_rfid("1")
    assert user is not None, "User 1 should exist"
    assert user['name'] == "Alice Johnson", f"Expected Alice Johnson, got {user['name']}"
    print(f"  ✓ User 1: {user['name']}")
    
    # Test non-existent user
    user = db.get_user_by_rfid("999")
    assert user is None, "User 999 should not exist"
    print("  ✓ Non-existent user returns None")
    
    # Test adding user
    result = db.add_user("999", "Test User")
    assert result is True, "Should be able to add new user"
    print("  ✓ Added new user")
    
    # Verify user was added
    user = db.get_user_by_rfid("999")
    assert user is not None, "User 999 should now exist"
    assert user['name'] == "Test User"
    print("  ✓ Verified new user")
    
    # Clean up
    db.delete_user("999")
    db.close()
    print("✓ Database tests passed\n")


def test_ui_initialization():
    """Test UI initialization"""
    print("Testing UI initialization...")
    
    # Initialize hardware
    rfid = MockRFIDReader()
    qr = MockQRScanner()
    cam = MockCamera()
    scale_top = MockScale(level="top")
    scale_bottom = MockScale(level="bottom")
    
    # Create UI
    ui = TouchUI(rfid=rfid, qr=qr, camera=cam, scale_top=scale_top, scale_bottom=scale_bottom)
    
    # Verify UI properties
    assert ui.width == 800, "Width should be 800"
    assert ui.height == 480, "Height should be 480"
    assert ui.screen is not None, "Screen should be initialized"
    assert ui.db is not None, "Database should be initialized"
    print("  ✓ UI initialized with correct dimensions")
    
    # Verify initial screen
    assert isinstance(ui.current_screen, MainScreen), "Initial screen should be MainScreen"
    print("  ✓ Main screen loaded")
    
    ui.db.close()
    pygame.quit()
    print("✓ UI initialization tests passed\n")


def test_screens():
    """Test screen creation and drawing"""
    print("Testing screen creation...")
    
    # Initialize hardware
    rfid = MockRFIDReader()
    qr = MockQRScanner()
    cam = MockCamera()
    scale_top = MockScale(level="top")
    scale_bottom = MockScale(level="bottom")
    
    # Create UI
    ui = TouchUI(rfid=rfid, qr=qr, camera=cam, scale_top=scale_top, scale_bottom=scale_bottom)
    
    # Test MainScreen
    main_screen = MainScreen(ui)
    assert len(main_screen.buttons) == 4, "Main screen should have 4 buttons"
    main_screen.draw(ui.screen)
    print("  ✓ MainScreen renders")
    
    # Test CardScanScreen
    card_screen = CardScanScreen(ui, "Test", "main")
    assert len(card_screen.buttons) == 1, "Card scan screen should have 1 button (back)"
    card_screen.draw(ui.screen)
    print("  ✓ CardScanScreen renders")
    
    # Test StockInventoryScreen
    stock_screen = StockInventoryScreen(ui)
    assert len(stock_screen.inventory) == 5, "Should have 5 inventory items"
    stock_screen.draw(ui.screen)
    print("  ✓ StockInventoryScreen renders")
    
    # Test AdminScreen
    user_info = {"rfid_number": "1", "name": "Alice Johnson"}
    admin_screen = AdminScreen(ui, user_info)
    admin_screen.draw(ui.screen)
    print("  ✓ AdminScreen renders")
    
    # Test OpenDoorsScreen
    open_screen = OpenDoorsScreen(ui, user_info)
    open_screen.draw(ui.screen)
    print("  ✓ OpenDoorsScreen renders")
    
    # Test ReturnDrinkScreen
    return_screen = ReturnDrinkScreen(ui, user_info)
    return_screen.draw(ui.screen)
    print("  ✓ ReturnDrinkScreen renders")
    
    ui.db.close()
    pygame.quit()
    print("✓ Screen creation tests passed\n")


def test_button_interactions():
    """Test button click detection"""
    print("Testing button interactions...")
    
    # Initialize hardware
    rfid = MockRFIDReader()
    qr = MockQRScanner()
    cam = MockCamera()
    scale_top = MockScale(level="top")
    scale_bottom = MockScale(level="bottom")
    
    # Create UI
    ui = TouchUI(rfid=rfid, qr=qr, camera=cam, scale_top=scale_top, scale_bottom=scale_bottom)
    
    main_screen = MainScreen(ui)
    
    # Test button contains
    btn = main_screen.buttons[0]
    assert btn.contains((btn.rect.centerx, btn.rect.centery)), "Button should contain its center"
    assert not btn.contains((0, 0)), "Button should not contain (0,0)"
    print("  ✓ Button collision detection works")
    
    # Test hover
    btn.handle_mouse_motion((btn.rect.centerx, btn.rect.centery))
    assert btn.is_hovered, "Button should be hovered"
    btn.handle_mouse_motion((0, 0))
    assert not btn.is_hovered, "Button should not be hovered"
    print("  ✓ Button hover detection works")
    
    ui.db.close()
    pygame.quit()
    print("✓ Button interaction tests passed\n")


def main():
    """Run all tests"""
    print("=" * 60)
    print("Running Pygame UI Integration Tests")
    print("=" * 60 + "\n")
    
    try:
        test_database()
        test_ui_initialization()
        test_screens()
        test_button_interactions()
        
        print("=" * 60)
        print("✓ All tests passed!")
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
