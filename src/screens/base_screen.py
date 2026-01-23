# src/screens/base_screen.py
"""
Base screen class and common utilities
"""
import pygame
from typing import Optional

from ui.theme import (
    PRIMARY, TEXT_PRIMARY, TEXT_ON_PRIMARY, WHITE,
    BG_GRADIENT_TOP, BG_GRADIENT_BOTTOM,
    get_font, draw_gradient_background,
    FONT_SIZE_TITLE, FONT_SIZE_HEADING, FONT_SIZE_BODY,
    PADDING_MD
)


class BaseScreen:
    """Base class for all screens"""
    
    def __init__(self, ui_manager, screen_manager=None):
        self.ui = ui_manager
        self.screen_manager = screen_manager
        self.buttons = []
        self.pressed_button = None
        self.payload = None  # Store payload from on_enter
        # Cache commonly used fonts
        self._title_font = get_font(FONT_SIZE_TITLE, bold=True)
        self._heading_font = get_font(FONT_SIZE_HEADING, bold=True)
        self._body_font = get_font(FONT_SIZE_BODY)
    
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
        """Draw common elements like background"""
        # Draw gradient background
        draw_gradient_background(surface, BG_GRADIENT_TOP, BG_GRADIENT_BOTTOM)
