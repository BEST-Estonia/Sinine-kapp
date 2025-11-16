# src/screen_manager.py
"""
Centralized screen manager for handling navigation between screens
"""
import pygame


class ScreenManager:
    """Manages screen transitions and navigation"""
    
    def __init__(self, ui_manager):
        self.ui = ui_manager
        self.current_screen = None
        self.screen_name = None
        self.screen_history = []
        self.screen_data = {}  # Store data passed between screens
    
    def load_screen(self, screen_class, screen_name, **kwargs):
        """Load a new screen"""
        self.screen_name = screen_name
        self.current_screen = screen_class(self.ui, **kwargs)
        return self.current_screen
    
    def navigate_to(self, screen_name, **kwargs):
        """Navigate to a screen by name"""
        # Store current screen in history (for back navigation)
        if self.screen_name:
            self.screen_history.append(self.screen_name)
        
        # Store any data for the new screen
        if kwargs:
            self.screen_data[screen_name] = kwargs
        
        return screen_name
    
    def go_back(self):
        """Go back to previous screen"""
        if self.screen_history:
            previous_screen = self.screen_history.pop()
            return previous_screen
        return "main"
    
    def reset(self):
        """Reset to main screen and clear history"""
        self.screen_history = []
        self.screen_data = {}
        return "main"
    
    def get_data(self, screen_name):
        """Get data stored for a screen"""
        return self.screen_data.get(screen_name, {})
    
    def clear_data(self, screen_name):
        """Clear data for a screen"""
        if screen_name in self.screen_data:
            del self.screen_data[screen_name]
