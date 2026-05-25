"""Shared colors and fonts for the pygame touchscreen UI."""

import pygame


# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------

class Colors:
    BACKGROUND = (255, 255, 255)
    DARK_BG    = (200, 200, 240)
    WHITE      = (255, 255, 255)
    GREY       = (150, 150, 150)
    GREEN      = (0, 150, 50)
    BLUE       = (0, 80, 180)
    DK_BLUE    = (0, 50, 120)
    RED        = (200, 50, 50)
    YELLOW     = (240, 200, 0)
    TEXT_PRIMARY = (0, 0, 0)


# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------

class FontManager:
    """Load the font sizes used by screen classes."""

    def __init__(self):
        self.header = pygame.font.SysFont("arial", 48, bold=True)
        self.body   = pygame.font.SysFont("arial", 32, bold=True)
        self.small  = pygame.font.SysFont("arial", 24)
        self.huge   = pygame.font.SysFont("arial", 72, bold=True)

    def render(self, font_type, text, color=Colors.TEXT_PRIMARY):
        """Render text with one of the preloaded pygame fonts."""
        return font_type.render(text, True, color)
