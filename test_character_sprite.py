#!/usr/bin/env python3
"""
Test script to verify character sprite system and take screenshots
"""
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'  # Use dummy driver initially

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import pygame
pygame.init()

# Test imports
print("Testing character sprite imports...")
from ui.character_sprite import CharacterSprite, CharacterManager, CharacterState, get_character_manager
print("✓ Character sprite imports successful")

# Test character manager
print("\nTesting character manager...")
manager = get_character_manager()
manager.initialize(600, 1024)
char = manager.get_character()
assert char is not None, "Character should be initialized"
print(f"✓ Character initialized at position ({char.x}, {char.y})")

# Test state changes
print("\nTesting character states...")
states = [
    (CharacterState.NEUTRAL, "neutral"),
    (CharacterState.HAPPY, "happy"),
    (CharacterState.SAD, "sad"),
    (CharacterState.SURPRISED, "surprised"),
    (CharacterState.CONFUSED, "confused"),
    (CharacterState.WAVING, "waving"),
]

for state, name in states:
    char.set_state(state)
    assert char.state == state, f"State should be {state}"
    print(f"✓ State '{name}' set successfully")

# Test convenience methods
print("\nTesting convenience methods...")
manager.set_happy()
assert char.state == CharacterState.HAPPY, "Should be happy"
print("✓ set_happy() works")

manager.set_sad()
assert char.state == CharacterState.SAD, "Should be sad"
print("✓ set_sad() works")

manager.set_surprised()
assert char.state == CharacterState.SURPRISED, "Should be surprised"
print("✓ set_surprised() works")

manager.set_confused()
assert char.state == CharacterState.CONFUSED, "Should be confused"
print("✓ set_confused() works")

manager.set_waving()
assert char.state == CharacterState.WAVING, "Should be waving"
print("✓ set_waving() works")

manager.set_neutral()
assert char.state == CharacterState.NEUTRAL, "Should be neutral"
print("✓ set_neutral() works")

# Test update and animation
print("\nTesting animation...")
initial_bob = char.bob_offset
char.update(0.1)  # Update with 100ms
assert char.bob_offset != initial_bob, "Bob offset should change"
print(f"✓ Animation working (bob offset: {initial_bob:.2f} -> {char.bob_offset:.2f})")

print("\n" + "=" * 60)
print("✓ All character sprite tests passed!")
print("=" * 60)
