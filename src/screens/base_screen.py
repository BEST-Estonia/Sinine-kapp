# src/screens/base_screen.py
"""
Base screen class and common utilities
"""
import pygame
from pathlib import Path

# Color constants
WHITE = (255, 255, 255)
LIGHT_BLUE = (220, 240, 255)
GRADIENT_TOP = (173, 216, 230)
GRADIENT_BOTTOM = (255, 255, 255)
TEAL = (32, 178, 170)
TEAL_DARK = (25, 140, 135)
SECONDARY = (255, 107, 107)
SECONDARY_DARK = (200, 85, 85)
GRAY = (200, 200, 200)
DARK_GRAY = (60, 60, 60)
GREEN = (50, 200, 100)
RED = (255, 80, 80)
TEXT_COLOR = (30, 30, 30)
SHADOW_COLOR = (0, 0, 0, 60)


def draw_gradient_background(surface, color_top, color_bottom):
    """Draw a vertical gradient background"""
    height = surface.get_height()
    for y in range(height):
        ratio = y / height
        r = int(color_top[0] * (1 - ratio) + color_bottom[0] * ratio)
        g = int(color_top[1] * (1 - ratio) + color_bottom[1] * ratio)
        b = int(color_top[2] * (1 - ratio) + color_bottom[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (surface.get_width(), y))


def load_sneaky_image(scale=(120, 120)):
    """Load the Sneaky character PNG"""
    try:
        img_path = Path(__file__).parent.parent.parent / "assets" / "sneaky.png"
        if img_path.exists():
            img = pygame.image.load(str(img_path))
            if scale:
                img = pygame.transform.scale(img, scale)
            return img
    except Exception as e:
        print(f"Could not load sneaky.png: {e}")
    return None


def draw_sneaky_bottom(surface, sneaky_img, width):
    """Draw Sneaky anchored at the bottom center of the screen"""
    if sneaky_img:
        img_rect = sneaky_img.get_rect()
        img_rect.centerx = width // 2
        img_rect.bottom = surface.get_height() - 10
        surface.blit(sneaky_img, img_rect)


class BaseScreen:
    """Base class for all screens"""
    
    def __init__(self, ui_manager, screen_manager=None):
        self.ui = ui_manager
        self.screen_manager = screen_manager
        self.buttons = []
        self.pressed_button = None
        self.sneaky_img = load_sneaky_image()
        self.payload = None  # Store payload from on_enter
    
    def on_enter(self, payload=None):
        """
        Called when screen becomes active (pushed or revealed by pop).
        Override in subclasses to initialize state based on payload.
        
        Args:
            payload: Optional data passed to the screen (dict or other data)
        """
        self.payload = payload
    
    def on_exit(self):
        """
        Called when screen is about to become inactive (being popped or covered by push).
        Override in subclasses to cleanup resources.
        """
        pass
    
    def handle_event(self, event):
        """Handle pygame events - override in subclasses if needed"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            for btn in self.buttons:
                if btn.contains(pos):
                    btn.set_pressed(True)
                    self.pressed_button = btn
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.pressed_button:
                self.pressed_button.set_pressed(False)
                pos = event.pos
                if self.pressed_button.contains(pos):
                    result = self.on_button_click(self.pressed_button)
                    self.pressed_button = None
                    return result
                self.pressed_button = None
        elif event.type == pygame.MOUSEMOTION:
            pos = event.pos
            for btn in self.buttons:
                btn.handle_mouse_motion(pos)
        return None
    
    def on_button_click(self, button):
        """Override in subclasses to handle button clicks"""
        return None
    
    def update(self):
        """Update screen state - override in subclasses"""
        return None
    
    def draw(self, surface):
        """Draw the screen - must be implemented in subclasses"""
        raise NotImplementedError("Subclasses must implement draw()")
    
    def draw_common_elements(self, surface):
        """Draw common elements like background and Sneaky"""
        # Draw gradient background
        draw_gradient_background(surface, GRADIENT_TOP, GRADIENT_BOTTOM)
        
        # Draw Sneaky at bottom
        draw_sneaky_bottom(surface, self.sneaky_img, self.ui.width)
