#!/usr/bin/env python3
"""
Test that main_menu.py has all required imports for button handlers
"""
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'  # Use dummy video driver for testing

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pygame
pygame.init()

from screen_manager import ScreenManager
from screens.main_menu import MainMenuScreen


class MockUIManager:
    """Mock UI manager for testing"""
    def __init__(self):
        self.width = 600
        self.height = 1024
        self.db = None
        self.rfid = None


def test_main_menu_imports():
    """Test that all required classes are importable in main_menu"""
    print("Testing main_menu.py imports...")
    
    # Verify CardScanScreen can be imported
    from screens.card_scan import CardScanScreen
    assert CardScanScreen is not None, "CardScanScreen should be importable"
    print("  ✓ CardScanScreen imported successfully")
    
    # Verify AdminInventoryScreen can be imported
    from screens.admin_inventory import AdminInventoryScreen
    assert AdminInventoryScreen is not None, "AdminInventoryScreen should be importable"
    print("  ✓ AdminInventoryScreen imported successfully")


def test_main_menu_button_handlers():
    """Test that button handlers don't raise NameError"""
    print("Testing main_menu button handlers...")
    
    ui = MockUIManager()
    sm = ScreenManager()
    screen = MainMenuScreen(ui, sm)
    
    # Test each button's handler
    for i, btn in enumerate(screen.buttons):
        try:
            # Call the handler - it will fail due to missing mock methods,
            # but should NOT fail with NameError for missing classes
            screen.on_button_click(btn)
            print(f"  ✓ Button {i+1} ({btn.text}): No import errors")
        except NameError as e:
            # This would indicate missing imports
            print(f"  ✗ Button {i+1} ({btn.text}): NameError - {e}")
            raise AssertionError(f"Button handler has missing import: {e}")
        except (AttributeError, TypeError) as e:
            # Expected - our mocks don't have all methods
            # But this means the imports worked!
            print(f"  ✓ Button {i+1} ({btn.text}): Imports OK (mock limitation)")
    
    print("✓ All button handlers have required imports\n")


def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing Main Menu Imports")
    print("=" * 60 + "\n")
    
    try:
        test_main_menu_imports()
        test_main_menu_button_handlers()
        
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
