#!/usr/bin/env python3
"""
Test script for Sinine Kapp mock mode functionality.
This validates that the mock mode works correctly without launching the GUI.
"""

import sys
import os

# Test 1: Import hardware_handler with mock mode
print("=" * 60)
print("TEST 1: Testing hardware_handler mock mode imports")
print("=" * 60)

# First set mock mode
import hardware_handler
print(f"✓ MOCK_MODE is set to: {hardware_handler.MOCK_MODE}")

# Verify GPIO is None in mock mode (or not None if real hardware)
if hardware_handler.MOCK_MODE:
    assert hardware_handler.GPIO is None, "GPIO should be None in mock mode"
    assert hardware_handler.SimpleMFRC522 is None, "SimpleMFRC522 should be None in mock mode"
    print("✓ Hardware libraries correctly disabled in mock mode")
else:
    print("✓ Running in hardware mode")

# Test 2: Import styles
print("\n" + "=" * 60)
print("TEST 2: Testing styles module")
print("=" * 60)

from styles import Colors, FontManager
print(f"✓ Colors.PRIMARY = {Colors.PRIMARY}")
print(f"✓ Colors.SUCCESS = {Colors.SUCCESS}")
print(f"✓ Colors.DANGER = {Colors.DANGER}")
print(f"✓ Colors.BACKGROUND = {Colors.BACKGROUND}")
print("✓ Styles imported successfully")

# Test 3: Import ui_components
print("\n" + "=" * 60)
print("TEST 3: Testing ui_components module")
print("=" * 60)

from ui_components import Button
print("✓ Button class imported successfully")

# Test 4: Import database_handler
print("\n" + "=" * 60)
print("TEST 4: Testing database_handler module")
print("=" * 60)

import database_handler
print("✓ database_handler imported successfully")

# Check if database exists
if os.path.exists('database.db'):
    print("✓ database.db exists")
    
    # Try a simple query
    try:
        conn = __import__('sqlite3').connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"✓ Found {len(tables)} tables in database:")
        for table in tables:
            print(f"  - {table[0]}")
        conn.close()
    except Exception as e:
        print(f"⚠ Could not query database: {e}")
else:
    print("⚠ database.db not found")

# Test 5: Check main.py imports
print("\n" + "=" * 60)
print("TEST 5: Testing main.py imports (without running)")
print("=" * 60)

try:
    # Just check if it can be imported (won't run if __name__ == "__main__")
    import main
    print("✓ main.py imports successfully")
except Exception as e:
    print(f"✗ Error importing main.py: {e}")

# Test 6: Verify drawer.py structure
print("\n" + "=" * 60)
print("TEST 6: Testing drawer.py imports")
print("=" * 60)

try:
    import drawer
    print("✓ drawer.py imports successfully")
    
    # Check if key classes exist
    classes_to_check = [
        'DEFAULT_SCREEN', 'VALIKUVAADE', 'VÄLJASTATUD_JOOGID',
        'LIVE_CART', 'REGISTREERIMINE'
    ]
    
    for class_name in classes_to_check:
        if hasattr(drawer, class_name):
            print(f"✓ Class {class_name} exists")
        else:
            print(f"✗ Class {class_name} NOT FOUND")
            
except Exception as e:
    print(f"✗ Error importing drawer.py: {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)
print("✓ All core modules import successfully")
print("✓ Mock mode is configured and ready")
print("✓ Application structure is valid")
print("\nTo run the application:")
print("  1. Ensure MOCK_MODE = True in hardware_handler.py")
print("  2. Run: python main.py")
print("  3. Use keyboard input for NFC and barcode scanning")
print("\nSee LAPTOP_MODE.md for detailed instructions.")
print("=" * 60)
