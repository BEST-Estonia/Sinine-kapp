# src/screens/input_dialog.py
"""
Modal input dialog for entering text with on-screen keyboard
Used by mock hardware to get input when running without terminal
"""
import pygame
from .base_screen import BaseScreen
from ui.theme import (
    PRIMARY, SECONDARY, TEXT_ON_PRIMARY, TEXT_PRIMARY, WHITE, 
    get_font, RADIUS_LG
)
from ui.buttons import Button
from ui.input_box import InputBox
from ui.keyboard import OnScreenKeyboard

TEXT_COLOR = (20, 20, 20)  # dark gray


class InputDialogScreen(BaseScreen):
    """Modal dialog for text input with on-screen keyboard"""
    
    def __init__(self, ui_manager, screen_manager, title, placeholder="", callback=None):
        """
        Initialize input dialog
        
        Args:
            ui_manager: UI manager reference
            screen_manager: Screen manager reference
            title: Dialog title text
            placeholder: Placeholder text for input box
            callback: Function to call with input value (or None if cancelled)
        """
        super().__init__(ui_manager, screen_manager)
        
        self.title = title
        self.callback = callback
        self.result = None
        
        # Cache fonts
        self._title_font = get_font(40, bold=True)
        self._button_font = get_font(36, bold=True)
        
        # Input box for text entry
        self.input_box = InputBox(
            (50, 200, self.ui.width - 100, 70),
            placeholder=placeholder,
            font_size=36
        )
        self.input_box.active = True
        
        # On-screen keyboard
        keyboard_height = 280
        keyboard_y = self.ui.height - keyboard_height - 140  # Leave room for Sneaky
        self.keyboard = OnScreenKeyboard(
            0, 
            keyboard_y,
            self.ui.width,
            keyboard_height
        )
        
        # Buttons
        btn_y = keyboard_y - 80
        btn_width = (self.ui.width - 90) // 2
        
        cancel_btn = Button(
            (30, btn_y, btn_width, 65), 
            "Cancel", 
            SECONDARY, 
            WHITE
        )
        
        ok_btn = Button(
            (30 + btn_width + 30, btn_y, btn_width, 65), 
            "OK", 
            PRIMARY, 
            WHITE
        )
        
        self.buttons = [cancel_btn, ok_btn]
    
    def on_enter(self, payload=None):
        """Initialize from payload"""
        super().on_enter(payload)
        if payload:
            if 'title' in payload:
                self.title = payload['title']
            if 'placeholder' in payload:
                self.input_box.placeholder = payload['placeholder']
            if 'callback' in payload:
                self.callback = payload['callback']
        # Clear previous input
        self.input_box.clear()
    
    def on_button_click(self, button):
        """Handle button clicks"""
        if button.text == "Cancel":
            # User cancelled
            self.result = None
            if self.callback:
                self.callback(None)
            self.screen_manager.pop()
        elif button.text == "OK":
            # User confirmed
            self.result = self.input_box.get_text().strip()
            if self.callback:
                self.callback(self.result)
            self.screen_manager.pop()
        return None
    
    def handle_event(self, event):
        """Handle events including keyboard input"""
        # Handle keyboard input first
        char = self.keyboard.handle_event(event)
        if char:
            if char == 'BACKSPACE':
                self.input_box.backspace()
            else:
                self.input_box.add_char(char)
            return None
        
        # Handle input box
        result = self.input_box.handle_event(event)
        if result == 'submit':
            # Trigger OK button
            return self.on_button_click(self.buttons[1])
        
        # Handle button clicks
        return super().handle_event(event)
    
    def update(self):
        """Update input box cursor"""
        self.input_box.update()
        return None
    
    def draw(self, surface):
        # Draw semi-transparent overlay over previous screen
        overlay = pygame.Surface((self.ui.width, self.ui.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Semi-transparent black
        surface.blit(overlay, (0, 0))
        
        # Draw dialog background
        dialog_rect = pygame.Rect(20, 100, self.ui.width - 40, self.ui.height - 200)
        pygame.draw.rect(surface, WHITE, dialog_rect, border_radius=RADIUS_LG)
        pygame.draw.rect(surface, PRIMARY, dialog_rect, width=4, border_radius=RADIUS_LG)
        
        # Draw title
        title_txt = self._title_font.render(self.title, True, TEXT_PRIMARY)
        title_rect = title_txt.get_rect(centerx=self.ui.width // 2, top=130)
        surface.blit(title_txt, title_rect)
        
        # Draw input box
        self.input_box.draw(surface)
        
        # Draw buttons
        for btn in self.buttons:
            btn.draw(surface, self._button_font)
        
        # Draw keyboard
        self.keyboard.draw(surface)
