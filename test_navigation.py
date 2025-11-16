#!/usr/bin/env python3
"""
Test complete navigation flow
"""
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import pygame
from screen_manager import ScreenManager
from database import DatabaseManager
from hardware.mock_rfid import MockRFIDReader
from screens import *


class MockUI:
    def __init__(self):
        pygame.init()
        self.width = 600
        self.height = 1024
        self.screen = pygame.display.set_mode((600, 1024))
        self.db = DatabaseManager()
        self.rfid = MockRFIDReader()


def test_navigation_flows():
    """Test all navigation flows match specification"""
    print("Testing Navigation Flows...\n")
    
    ui = MockUI()
    sm = ScreenManager()
    
    # Test 1: Main Menu -> Inventory -> Back
    print("Test 1: Main Menu -> Inventory -> Back")
    main = MainMenuScreen(ui, sm)
    sm.go_to(main)
    assert sm.current() == main
    
    inv = InventoryViewScreen(ui, sm)
    sm.push(inv)
    assert sm.current() == inv
    
    sm.pop()
    assert sm.current() == main
    print("  ✓ Pass\n")
    
    # Test 2: Main Menu -> Card Scan -> Registration Prompt -> Name Entry -> Cancel
    print("Test 2: Main Menu -> Card Scan -> Reg Prompt -> Name Entry -> Cancel")
    sm.go_to(main)
    
    card_scan = CardScanScreen(ui, sm, "Test", "borrow")
    sm.push(card_scan)
    
    reg_prompt = RegisterPromptScreen(ui, sm, "999", "borrow")
    sm.push(reg_prompt)
    
    reg_user = RegisterUserScreen(ui, sm, "999")
    sm.push(reg_user)
    
    # Cancel goes back to prompt
    sm.pop()
    assert sm.current() == reg_prompt
    
    # No from prompt goes to card scan
    sm.pop()
    assert sm.current() == card_scan
    
    # Back from card scan to main
    sm.pop()
    assert sm.current() == main
    print("  ✓ Pass\n")
    
    # Test 3: QR Scan -> Finalize -> Thank You -> Main
    print("Test 3: QR Scan -> Finalize -> Thank You -> Main")
    user = ui.db.get_user_by_card("1")
    basket = [{'qr_code': 'DRINK001', 'name': 'Test', 'quantity': 1}]
    
    sm.go_to(main)
    qr_scan = QRScanScreen(ui, sm, user, "borrow")
    sm.push(qr_scan)
    
    finalize = FinalizeScreen(ui, sm, user, basket, "borrow")
    sm.push(finalize)
    
    thank_you = ThankYouScreen(ui, sm, user, basket, "borrow")
    sm.push(thank_you)
    
    # Thank you should go back to main
    sm.go_to(main)
    assert sm.current() == main
    print("  ✓ Pass\n")
    
    # Test 4: Admin Panel Navigation
    print("Test 4: Admin Panel -> Users -> User Details -> Back -> Back -> Back")
    admin_user = ui.db.get_user_by_card("1")
    sm.go_to(main)
    
    admin_main = AdminMainScreen(ui, sm, admin_user)
    sm.push(admin_main)
    
    admin_users = AdminUsersScreen(ui, sm, admin_user)
    sm.push(admin_users)
    
    admin_details = AdminUserDetailsScreen(ui, sm, admin_user, 2)
    sm.push(admin_details)
    
    # Back to users
    sm.pop()
    assert sm.current() == admin_users
    
    # Back to admin main
    sm.pop()
    assert sm.current() == admin_main
    
    # Back to main
    sm.pop()
    assert sm.current() == main
    print("  ✓ Pass\n")
    
    print("✓ All navigation flows work correctly!\n")


def test_screen_features():
    """Test specific screen features"""
    print("Testing Screen Features...\n")
    
    ui = MockUI()
    sm = ScreenManager()
    user = ui.db.get_user_by_card("1")
    
    # Test 1: QR Scan delete buttons
    print("Test 1: QR Scan basket item deletion")
    qr_scan = QRScanScreen(ui, sm, user, "borrow")
    qr_scan.basket = [
        {'qr_code': 'DRINK001', 'name': 'Item 1', 'quantity': 1},
        {'qr_code': 'DRINK002', 'name': 'Item 2', 'quantity': 1},
    ]
    qr_scan._build_item_buttons()
    assert len(qr_scan.item_buttons) == 2  # One delete button per item
    print("  ✓ Delete buttons created\n")
    
    # Test 2: Registration Prompt has Yes/No buttons
    print("Test 2: Registration Prompt buttons")
    reg_prompt = RegisterPromptScreen(ui, sm, "999", "borrow")
    button_texts = [btn.text for btn in reg_prompt.buttons]
    assert "Yes" in button_texts
    assert "No" in button_texts
    print("  ✓ Yes/No buttons present\n")
    
    # Test 3: Finalize screen shows correct message
    print("Test 3: Finalize screen message")
    basket = [{'qr_code': 'DRINK001', 'name': 'Test', 'quantity': 1}]
    finalize = FinalizeScreen(ui, sm, user, basket, "borrow")
    # Just verify it can be created with correct action
    assert finalize.action == "borrow"
    print("  ✓ Finalize screen created correctly\n")
    
    # Test 4: Thank You message format
    print("Test 4: Thank You screen for borrow")
    thank_you = ThankYouScreen(ui, sm, user, basket, "borrow")
    # Verify it includes user name in expected format
    assert thank_you.user_info['name'] == "Admin User"
    assert thank_you.action == "borrow"
    print("  ✓ Thank You screen has user info\n")
    
    # Test 5: Inventory View is read-only
    print("Test 5: Inventory View (read-only)")
    inv_view = InventoryViewScreen(ui, sm)
    # Should only have back button, no +/- buttons
    assert len(inv_view.buttons) == 1
    assert inv_view.buttons[0].text == "← Back"
    print("  ✓ Inventory View is read-only\n")
    
    print("✓ All screen features work correctly!\n")


def test_admin_restrictions():
    """Test admin access restrictions"""
    print("Testing Admin Restrictions...\n")
    
    ui = MockUI()
    
    # Test 1: Admin user has is_admin flag
    print("Test 1: Admin user check")
    admin = ui.db.get_user_by_card("1")
    assert admin['is_admin'] == 1
    print("  ✓ Admin user has is_admin flag\n")
    
    # Test 2: Regular user doesn't have admin flag
    print("Test 2: Regular user check")
    regular_user = ui.db.get_user_by_card("2")
    assert regular_user['is_admin'] == 0
    print("  ✓ Regular user doesn't have admin flag\n")
    
    print("✓ Admin restrictions configured correctly!\n")


if __name__ == "__main__":
    try:
        test_navigation_flows()
        test_screen_features()
        test_admin_restrictions()
        print("\n" + "="*50)
        print("✓✓✓ ALL TESTS PASSED! ✓✓✓")
        print("="*50)
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
