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
        self.camera = None
        self.quit_called = False
    
    def quit(self):
        self.quit_called = True


def test_main_menu_imports():
    """Test that all required classes are importable in main_menu"""
    print("Testing main_menu.py imports...")
    
    # Verify MainMenuScreen can be imported
    from screens.main_menu import MainMenuScreen
    assert MainMenuScreen is not None, "MainMenuScreen should be importable"
    print("  ✓ MainMenuScreen imported successfully")
    
    # Verify BaseScreen can be imported
    from screens.base_screen import BaseScreen
    assert BaseScreen is not None, "BaseScreen should be importable"
    print("  ✓ BaseScreen imported successfully")


def test_main_menu_button_handlers():
    """Test that button handlers don't raise errors"""
    print("Testing main_menu button handlers...")
    
    ui = MockUIManager()
    sm = ScreenManager()
    screen = MainMenuScreen(ui, sm)
    
    # Test each button's handler
    for i, btn in enumerate(screen.buttons):
        try:
            # Call the handler
            screen.on_button_click(btn)
            print(f"  ✓ Button {i+1} ({btn.text}): Handler works")
        except NameError as e:
            # This would indicate missing imports
            print(f"  ✗ Button {i+1} ({btn.text}): NameError - {e}")
            raise AssertionError(f"Button handler has missing import: {e}")
        except (AttributeError, TypeError) as e:
            # Expected for some handlers if mock doesn't have all methods
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
