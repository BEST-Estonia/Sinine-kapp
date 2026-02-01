# style.py
import pygame

# --- COLORS (Modern Fast Food Kiosk Theme) ---
class Colors:
    # Primary background - Clean white
    BACKGROUND = (255, 255, 255)
    # Lighter shade for sections
    LIGHT_BG   = (248, 248, 250)
    # Card/panel background
    CARD_BG    = (242, 245, 247)
    
    # Standard colors
    WHITE      = (255, 255, 255)
    GREY       = (150, 150, 150)
    LIGHT_GREY = (200, 200, 200)
    DARK_GREY  = (80, 80, 80)
    
    # Brand colors - Vibrant and eye-catching
    PRIMARY    = (0, 122, 255)      # iOS-style blue
    SUCCESS    = (52, 199, 89)      # Bright green
    WARNING    = (255, 149, 0)      # Orange
    DANGER     = (255, 59, 48)      # Red
    INFO       = (90, 200, 250)     # Light blue
    
    # Legacy color mappings for compatibility
    DARK_BG    = CARD_BG
    GREEN      = SUCCESS
    BLUE       = PRIMARY
    DK_BLUE    = (0, 80, 180)
    RED        = DANGER
    YELLOW     = WARNING
    
    # Text colors
    TEXT_PRIMARY   = (28, 28, 30)   # Almost black
    TEXT_SECONDARY = (142, 142, 147) # Grey text
    TEXT_ON_COLOR  = (255, 255, 255) # White text for colored buttons
    
# --- FONT MANAGER (Adjusted for vertical 1080x1920) ---
class FontManager:
    def __init__(self):
       # Larger fonts for vertical kiosk display
        self.huge   = pygame.font.SysFont("arial", 120, bold=True)  # Main titles
        self.header = pygame.font.SysFont("arial", 72, bold=True)   # Section headers
        self.title  = pygame.font.SysFont("arial", 60, bold=True)   # Subtitles
        self.body   = pygame.font.SysFont("arial", 48, bold=False)  # Body text
        self.small  = pygame.font.SysFont("arial", 36)              # Small text
        self.tiny   = pygame.font.SysFont("arial", 28)              # Tiny text

    # Helper to make text rendering cleaner
    def render(self, font_type, text, color=Colors.TEXT_PRIMARY):
        """
        Usage: fonts.render(fonts.header, "Hello")
        """
        return font_type.render(text, True, color)