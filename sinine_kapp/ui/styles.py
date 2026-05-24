# style.py
import pygame

# --- COLORS (Define them once here) ---
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
# --- FONT MANAGER ---
class FontManager:
    def __init__(self):
       #Predefined font styles
        self.header = pygame.font.SysFont("arial", 48, bold=True)
        self.body   = pygame.font.SysFont("arial", 32, bold=True)
        self.small  = pygame.font.SysFont("arial", 24)
        self.huge   = pygame.font.SysFont("arial", 72, bold=True)

    # Helper to make text rendering cleaner
    def render(self, font_type, text, color=Colors.TEXT_PRIMARY):
        """
        Usage: fonts.render(fonts.header, "Hello")
        """
        return font_type.render(text, True, color)