# src/screens/main_menu.py
"""
Main menu screen with 2 buttons: Open Camera and Close Program
"""
import pygame
from .base_screen import BaseScreen
from ui.buttons import Button
from ui.theme import (
    PRIMARY, SECONDARY, TEXT_ON_PRIMARY, TEXT_PRIMARY, WHITE,
    PADDING_MD, SPACING_LG, BUTTON_HEIGHT_LG,
    get_font, FONT_SIZE_TITLE, FONT_SIZE_BUTTON,
    draw_gradient_background, BG_GRADIENT_TOP, BG_GRADIENT_BOTTOM
)


class MainMenuScreen(BaseScreen):
    """Main menu screen with 2 option buttons: Open Camera and Close Program"""
    
    def __init__(self, ui_manager, screen_manager):
        super().__init__(ui_manager, screen_manager)
        
        # Cache fonts
        self._title_font = get_font(FONT_SIZE_TITLE, bold=True)
        self._button_font = get_font(FONT_SIZE_BUTTON, bold=True)
        
        # Calculate button layout - center buttons vertically
        padding = PADDING_MD
        btn_w = self.ui.width - (padding * 2)
        btn_h = BUTTON_HEIGHT_LG
        spacing = SPACING_LG
        
        # Calculate starting Y to center the two buttons
        total_button_height = (btn_h * 2) + spacing
        start_y = (self.ui.height - total_button_height) // 2
        
        self.buttons = [
            Button((padding, start_y, btn_w, btn_h), "Open Camera", PRIMARY, TEXT_ON_PRIMARY),
            Button((padding, start_y + btn_h + spacing, btn_w, btn_h), "Close Program", SECONDARY, TEXT_ON_PRIMARY),
        ]
    
    def on_button_click(self, button):
        """Handle button clicks"""
        if button.text == "Open Camera":
            # Open the camera
            if hasattr(self.ui, 'camera'):
                self.ui.camera.capture()
                print("Camera opened!")
        elif button.text == "Close Program":
            # Close the program
            if hasattr(self.ui, 'quit'):
                self.ui.quit()
        return None
    
    def draw(self, surface):
        # Draw gradient background
        draw_gradient_background(surface, BG_GRADIENT_TOP, BG_GRADIENT_BOTTOM)
        
        # Draw title
        title_text = "Simple Camera"
        title = self._title_font.render(title_text, True, TEXT_PRIMARY)
        title_rect = title.get_rect(centerx=self.ui.width // 2, y=100)
        surface.blit(title, title_rect)
        
        # Draw buttons
        for btn in self.buttons:
            btn.draw(surface, self._button_font)
