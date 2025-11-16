# src/ui/theme.py
"""
Central design system for the Smart Cupboard UI.
Defines colors, spacing, and provides cached font access.
"""
import pygame
from typing import Tuple, Optional

# ============================================================================
# COLOR PALETTE
# ============================================================================

# Primary colors
PRIMARY = (32, 178, 170)  # Teal
PRIMARY_DARK = (25, 140, 135)  # Darker teal
PRIMARY_LIGHT = (60, 200, 190)  # Lighter teal

# Secondary colors
SECONDARY = (255, 107, 107)  # Coral red
SECONDARY_DARK = (200, 85, 85)  # Darker coral
SECONDARY_LIGHT = (255, 140, 140)  # Lighter coral

# Background colors
BG_GRADIENT_TOP = (173, 216, 230)  # Light blue
BG_GRADIENT_BOTTOM = (255, 255, 255)  # White
BG_LIGHT = (220, 240, 255)  # Light blue background

# Text colors
TEXT_PRIMARY = (30, 30, 30)  # Dark gray
TEXT_SECONDARY = (100, 100, 100)  # Medium gray
TEXT_ON_PRIMARY = (255, 255, 255)  # White (for buttons)

# Status colors
SUCCESS = (50, 200, 100)  # Green
WARNING = (255, 193, 7)  # Amber
ERROR = (255, 80, 80)  # Red
INFO = (33, 150, 243)  # Blue

# Neutral colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY_LIGHT = (200, 200, 200)
GRAY = (150, 150, 150)
GRAY_DARK = (60, 60, 60)

# Shadow color (with alpha)
SHADOW = (0, 0, 0, 60)

# ============================================================================
# SPACING & LAYOUT
# ============================================================================

# Padding
PADDING_XS = 10
PADDING_SM = 20
PADDING_MD = 30
PADDING_LG = 40
PADDING_XL = 50

# Spacing between elements
SPACING_XS = 10
SPACING_SM = 15
SPACING_MD = 20
SPACING_LG = 30
SPACING_XL = 40

# Border radius
RADIUS_SM = 10
RADIUS_MD = 15
RADIUS_LG = 20
RADIUS_XL = 25

# Button dimensions
BUTTON_HEIGHT = 90
BUTTON_HEIGHT_SM = 70
BUTTON_HEIGHT_LG = 110

# Component dimensions
HEADER_HEIGHT = 100
FOOTER_HEIGHT = 100
PANEL_BORDER_WIDTH = 3

# ============================================================================
# FONT SYSTEM
# ============================================================================

class FontCache:
    """
    Singleton font cache to avoid loading fonts every frame.
    Fonts are loaded once and reused throughout the application.
    """
    _instance: Optional['FontCache'] = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not FontCache._initialized:
            pygame.font.init()
            self._fonts = {}
            FontCache._initialized = True
    
    def get_font(self, size: int, bold: bool = False, italic: bool = False) -> pygame.font.Font:
        """
        Get a cached font with the specified properties.
        
        Args:
            size: Font size in pixels
            bold: Whether the font should be bold
            italic: Whether the font should be italic
            
        Returns:
            Cached pygame.font.Font object
        """
        key = (size, bold, italic)
        if key not in self._fonts:
            self._fonts[key] = pygame.font.SysFont('Arial', size, bold=bold, italic=italic)
        return self._fonts[key]
    
    def clear(self):
        """Clear all cached fonts (useful for cleanup)"""
        self._fonts.clear()


# Global font cache instance
_font_cache = FontCache()


def get_font(size: int, bold: bool = False, italic: bool = False) -> pygame.font.Font:
    """
    Get a cached font with the specified properties.
    This is the main function to use for getting fonts throughout the app.
    
    Args:
        size: Font size in pixels
        bold: Whether the font should be bold
        italic: Whether the font should be italic
        
    Returns:
        Cached pygame.font.Font object
        
    Example:
        title_font = get_font(48, bold=True)
        body_font = get_font(24)
    """
    return _font_cache.get_font(size, bold, italic)


# ============================================================================
# PREDEFINED FONT SIZES
# ============================================================================

# Font sizes for common use cases
FONT_SIZE_XS = 22
FONT_SIZE_SM = 26
FONT_SIZE_MD = 32
FONT_SIZE_LG = 40
FONT_SIZE_XL = 48
FONT_SIZE_XXL = 56

# Semantic font sizes
FONT_SIZE_TITLE = 48
FONT_SIZE_HEADING = 40
FONT_SIZE_SUBHEADING = 32
FONT_SIZE_BODY = 26
FONT_SIZE_BUTTON = 42
FONT_SIZE_CAPTION = 22


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def draw_gradient_background(surface: pygame.Surface, 
                            color_top: Tuple[int, int, int] = BG_GRADIENT_TOP,
                            color_bottom: Tuple[int, int, int] = BG_GRADIENT_BOTTOM):
    """
    Draw a vertical gradient background on the surface.
    
    Args:
        surface: Pygame surface to draw on
        color_top: RGB color at the top
        color_bottom: RGB color at the bottom
    """
    height = surface.get_height()
    width = surface.get_width()
    
    # Draw gradient line by line
    for y in range(height):
        ratio = y / height
        r = int(color_top[0] * (1 - ratio) + color_bottom[0] * ratio)
        g = int(color_top[1] * (1 - ratio) + color_bottom[1] * ratio)
        b = int(color_top[2] * (1 - ratio) + color_bottom[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (width, y))


def create_shadow_surface(width: int, height: int, 
                         color: Tuple[int, int, int, int] = SHADOW,
                         border_radius: int = RADIUS_MD) -> pygame.Surface:
    """
    Create a shadow surface with alpha channel.
    
    Args:
        width: Width of the shadow
        height: Height of the shadow
        color: RGBA color for the shadow
        border_radius: Border radius for rounded corners
        
    Returns:
        Pygame surface with alpha channel
    """
    shadow_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surf, color, shadow_surf.get_rect(), border_radius=border_radius)
    return shadow_surf


def center_x(screen_width: int, element_width: int) -> int:
    """
    Calculate X position to center an element horizontally.
    
    Args:
        screen_width: Width of the screen/container
        element_width: Width of the element to center
        
    Returns:
        X coordinate for centered element
    """
    return (screen_width - element_width) // 2


def center_y(screen_height: int, element_height: int) -> int:
    """
    Calculate Y position to center an element vertically.
    
    Args:
        screen_height: Height of the screen/container
        element_height: Height of the element to center
        
    Returns:
        Y coordinate for centered element
    """
    return (screen_height - element_height) // 2
