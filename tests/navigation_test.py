#!/usr/bin/env python3
"""
Navigation tests for the stack-based ScreenManager
Tests screen stack operations, lifecycle hooks, and navigation flows
"""
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'  # Use dummy video driver for testing

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from screen_manager import ScreenManager
from screens.base_screen import BaseScreen


class MockUIManager:
    """Mock UI manager for testing"""
    def __init__(self):
        self.width = 600
        self.height = 1024


class MockScreen(BaseScreen):
    """Mock screen for testing"""
    def __init__(self, name, ui_manager, screen_manager):
        super().__init__(ui_manager, screen_manager)
        self.name = name
        self.enter_count = 0
        self.exit_count = 0
        self.last_payload = None
    
    def on_enter(self, payload=None):
        super().on_enter(payload)
        self.enter_count += 1
        self.last_payload = payload
    
    def on_exit(self):
        super().on_exit()
        self.exit_count += 1
    
    def draw(self, surface):
        pass


def test_screen_manager_initialization():
    """Test ScreenManager initialization"""
    print("Testing ScreenManager initialization...")
    sm = ScreenManager()
    assert sm.current() is None, "ScreenManager should start with no screens"
    assert len(sm.screen_stack) == 0, "Screen stack should be empty"
    print("  ✓ ScreenManager initializes correctly")


def test_go_to():
    """Test go_to method"""
    print("Testing go_to...")
    sm = ScreenManager()
    ui = MockUIManager()
    
    screen1 = MockScreen("screen1", ui, sm)
    sm.go_to(screen1, payload={'test': 'data'})
    
    assert sm.current() == screen1, "Current screen should be screen1"
    assert screen1.enter_count == 1, "on_enter should be called once"
    assert screen1.last_payload == {'test': 'data'}, "Payload should be passed"
    assert len(sm.screen_stack) == 1, "Stack should have 1 screen"
    print("  ✓ go_to works correctly")


def test_push():
    """Test push method"""
    print("Testing push...")
    sm = ScreenManager()
    ui = MockUIManager()
    
    screen1 = MockScreen("screen1", ui, sm)
    screen2 = MockScreen("screen2", ui, sm)
    
    sm.go_to(screen1)
    sm.push(screen2, payload={'key': 'value'})
    
    assert sm.current() == screen2, "Current screen should be screen2"
    assert screen1.exit_count == 1, "screen1 on_exit should be called"
    assert screen2.enter_count == 1, "screen2 on_enter should be called"
    assert screen2.last_payload == {'key': 'value'}, "Payload should be passed to screen2"
    assert len(sm.screen_stack) == 2, "Stack should have 2 screens"
    print("  ✓ push works correctly")


def test_pop():
    """Test pop method"""
    print("Testing pop...")
    sm = ScreenManager()
    ui = MockUIManager()
    
    screen1 = MockScreen("screen1", ui, sm)
    screen2 = MockScreen("screen2", ui, sm)
    
    sm.go_to(screen1)
    sm.push(screen2)
    
    popped = sm.pop()
    
    assert popped == screen2, "Popped screen should be screen2"
    assert sm.current() == screen1, "Current screen should be screen1"
    assert screen2.exit_count == 1, "screen2 on_exit should be called"
    assert screen1.enter_count == 2, "screen1 on_enter should be called again (re-entry)"
    assert len(sm.screen_stack) == 1, "Stack should have 1 screen"
    print("  ✓ pop works correctly")


def test_pop_root_screen():
    """Test that popping the root screen doesn't remove it"""
    print("Testing pop on root screen...")
    sm = ScreenManager()
    ui = MockUIManager()
    
    screen1 = MockScreen("screen1", ui, sm)
    sm.go_to(screen1)
    
    popped = sm.pop()
    
    assert popped is None, "Cannot pop root screen"
    assert sm.current() == screen1, "Root screen should remain"
    assert len(sm.screen_stack) == 1, "Stack should still have 1 screen"
    print("  ✓ pop on root screen works correctly")


def test_stack_depth():
    """Test multiple push operations"""
    print("Testing stack depth...")
    sm = ScreenManager()
    ui = MockUIManager()
    
    screens = [MockScreen(f"screen{i}", ui, sm) for i in range(5)]
    
    sm.go_to(screens[0])
    for screen in screens[1:]:
        sm.push(screen)
    
    assert len(sm.screen_stack) == 5, "Stack should have 5 screens"
    assert sm.current() == screens[4], "Current should be last pushed screen"
    
    # Pop all but root
    for i in range(3):
        sm.pop()
    
    assert len(sm.screen_stack) == 2, "Stack should have 2 screens after 3 pops"
    assert sm.current() == screens[1], "Current should be screen1"
    print("  ✓ Stack depth works correctly")


def test_go_to_clears_stack():
    """Test that go_to clears the entire stack"""
    print("Testing go_to clears stack...")
    sm = ScreenManager()
    ui = MockUIManager()
    
    screens = [MockScreen(f"screen{i}", ui, sm) for i in range(3)]
    
    sm.go_to(screens[0])
    sm.push(screens[1])
    
    # Now go_to should clear the stack
    sm.go_to(screens[2])
    
    assert len(sm.screen_stack) == 1, "Stack should have only 1 screen after go_to"
    assert sm.current() == screens[2], "Current should be screen2"
    # screens[0] exits when screens[1] is pushed, then exits again when go_to clears the stack
    assert screens[0].exit_count == 2, "screen0 should have exited twice"
    assert screens[1].exit_count == 1, "screen1 should have exited once"
    print("  ✓ go_to clears stack correctly")


def test_lifecycle_hooks():
    """Test that lifecycle hooks are called correctly"""
    print("Testing lifecycle hooks...")
    sm = ScreenManager()
    ui = MockUIManager()
    
    screen1 = MockScreen("screen1", ui, sm)
    screen2 = MockScreen("screen2", ui, sm)
    
    # go_to screen1
    sm.go_to(screen1)
    assert screen1.enter_count == 1, "screen1 should enter once"
    assert screen1.exit_count == 0, "screen1 should not exit yet"
    
    # push screen2
    sm.push(screen2)
    assert screen1.exit_count == 1, "screen1 should exit when screen2 is pushed"
    assert screen2.enter_count == 1, "screen2 should enter once"
    
    # pop screen2
    sm.pop()
    assert screen2.exit_count == 1, "screen2 should exit when popped"
    assert screen1.enter_count == 2, "screen1 should re-enter when screen2 is popped"
    
    print("  ✓ Lifecycle hooks work correctly")


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Running ScreenManager Navigation Tests")
    print("=" * 60)
    
    try:
        test_screen_manager_initialization()
        test_go_to()
        test_push()
        test_pop()
        test_pop_root_screen()
        test_stack_depth()
        test_go_to_clears_stack()
        test_lifecycle_hooks()
        
        print("=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
        return True
    except AssertionError as e:
        print("=" * 60)
        print(f"Test failed: {e}")
        print("=" * 60)
        return False
    except Exception as e:
        print("=" * 60)
        print(f"Test error: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
