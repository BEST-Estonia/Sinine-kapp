#!/usr/bin/env python3
"""
Integration test for the Simple Camera UI
Tests the application initialization and button functionality
"""
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'  # Use dummy video driver for testing

import sys
import pygame
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from screen_manager import ScreenManager
from screens import MainMenuScreen
from hardware.mock_camera import MockCamera


class MockUIManager:
    """Mock UI manager for testing"""
    def __init__(self):
        self.width = 600
        self.height = 1024
        self.camera = MockCamera()
        self.quit_called = False
    
    def quit(self):
        self.quit_called = True


def test_main_menu_creation():
    """Test main menu screen creation"""
    print("Testing main menu creation...")
    
    pygame.init()
    pygame.font.init()
    
    ui = MockUIManager()
    sm = ScreenManager()
    screen = MainMenuScreen(ui, sm)
    
    # Verify buttons
    assert len(screen.buttons) == 2, f"Expected 2 buttons, got {len(screen.buttons)}"
    assert screen.buttons[0].text == "Open Camera", f"First button should be 'Open Camera'"
    assert screen.buttons[1].text == "Close Program", f"Second button should be 'Close Program'"
    print("  ✓ Main menu has 2 buttons: 'Open Camera' and 'Close Program'")
    
    pygame.quit()
    print("✓ Main menu creation tests passed\n")


def test_open_camera_button():
    """Test Open Camera button"""
    print("Testing Open Camera button...")
    
    pygame.init()
    pygame.font.init()
    
    ui = MockUIManager()
    sm = ScreenManager()
    screen = MainMenuScreen(ui, sm)
    
    # Find and click Open Camera button
    camera_btn = screen.buttons[0]
    assert camera_btn.text == "Open Camera"
    
    # Simulate button click
    screen.on_button_click(camera_btn)
    print("  ✓ Open Camera button clicked successfully")
    
    pygame.quit()
    print("✓ Open Camera button tests passed\n")


def test_close_program_button():
    """Test Close Program button"""
    print("Testing Close Program button...")
    
    pygame.init()
    pygame.font.init()
    
    ui = MockUIManager()
    sm = ScreenManager()
    screen = MainMenuScreen(ui, sm)
    
    # Find and click Close Program button
    close_btn = screen.buttons[1]
    assert close_btn.text == "Close Program"
    
    # Simulate button click
    screen.on_button_click(close_btn)
    
    # Verify quit was called
    assert ui.quit_called, "quit() should be called when Close Program is clicked"
    print("  ✓ Close Program button triggers quit")
    
    pygame.quit()
    print("✓ Close Program button tests passed\n")


def test_button_interactions():
    """Test button click detection"""
    print("Testing button interactions...")
    
    pygame.init()
    pygame.font.init()
    
    ui = MockUIManager()
    sm = ScreenManager()
    screen = MainMenuScreen(ui, sm)
    
    # Test button contains
    btn = screen.buttons[0]
    assert btn.contains((btn.rect.centerx, btn.rect.centery)), "Button should contain its center"
    assert not btn.contains((0, 0)), "Button should not contain (0,0)"
    print("  ✓ Button collision detection works")
    
    # Test hover
    btn.handle_mouse_motion((btn.rect.centerx, btn.rect.centery))
    assert btn.is_hovered, "Button should be hovered"
    btn.handle_mouse_motion((0, 0))
    assert not btn.is_hovered, "Button should not be hovered"
    print("  ✓ Button hover detection works")
    
    pygame.quit()
    print("✓ Button interaction tests passed\n")


def main():
    """Run all tests"""
    print("=" * 60)
    print("Running Simple Camera UI Integration Tests")
    print("=" * 60 + "\n")
    
    try:
        test_main_menu_creation()
        test_open_camera_button()
        test_close_program_button()
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
