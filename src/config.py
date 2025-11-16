# src/config.py
"""
Central configuration for the Smart Cupboard application.
Contains window dimensions, FPS, and other application-wide settings.
"""

# Display configuration
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 1024
FPS = 30

# Window settings
FULLSCREEN = False  # Set to True for production on Raspberry Pi
NOFRAME = True  # Borderless window

# Hardware configuration
MOCK_HARDWARE = True  # Use mock hardware for development/testing

# Database configuration
DB_PATH = "database/users.db"

# Asset paths
ASSETS_DIR = "assets"
SNEAKY_IMAGE = "sneaky.png"
