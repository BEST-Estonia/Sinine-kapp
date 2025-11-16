# src/screen_manager.py
"""
Stack-based screen manager for proper navigation and Z-order rendering
"""
import pygame


class ScreenManager:
    """
    Stack-based screen manager that ensures:
    - Screens render in correct Z-order
    - Only the active/top screen receives events and updates
    - Transitions (push/pop/go_to) behave predictably
    """
    
    def __init__(self):
        self.screen_stack = []  # Stack of screen instances
    
    def push(self, screen_instance, payload=None):
        """
        Push a new screen on top of the stack (for modal/subscreens).
        Calls on_exit() on current screen (if any), then on_enter(payload) on new screen.
        
        Args:
            screen_instance: The screen object to push
            payload: Optional data to pass to the screen's on_enter method
        """
        # Exit current screen
        if self.screen_stack:
            current = self.screen_stack[-1]
            if hasattr(current, 'on_exit'):
                current.on_exit()
        
        # Push new screen
        self.screen_stack.append(screen_instance)
        
        # Enter new screen
        if hasattr(screen_instance, 'on_enter'):
            screen_instance.on_enter(payload)
    
    def pop(self):
        """
        Pop current screen and return to previous.
        Calls on_exit() on current screen and on_enter(None) on the revealed screen.
        
        Returns:
            The popped screen instance, or None if stack is empty or has only one screen
        """
        if len(self.screen_stack) <= 1:
            return None  # Don't pop the root screen
        
        # Exit current screen
        popped = self.screen_stack.pop()
        if hasattr(popped, 'on_exit'):
            popped.on_exit()
        
        # Re-enter previous screen
        if self.screen_stack:
            current = self.screen_stack[-1]
            if hasattr(current, 'on_enter'):
                current.on_enter(None)
        
        return popped
    
    def go_to(self, screen_instance, payload=None):
        """
        Clear stack and set the given screen as root.
        Useful for returning to main menu or switching to a completely different flow.
        
        Args:
            screen_instance: The screen object to set as root
            payload: Optional data to pass to the screen's on_enter method
        """
        # Exit all screens in reverse order
        while self.screen_stack:
            screen = self.screen_stack.pop()
            if hasattr(screen, 'on_exit'):
                screen.on_exit()
        
        # Set new root screen
        self.screen_stack.append(screen_instance)
        
        # Enter new screen
        if hasattr(screen_instance, 'on_enter'):
            screen_instance.on_enter(payload)
    
    def current(self):
        """
        Return the top screen (currently active).
        
        Returns:
            The current screen instance, or None if stack is empty
        """
        return self.screen_stack[-1] if self.screen_stack else None
    
    def render(self, surface):
        """
        Render only the current (top) screen.
        Only the active screen should be visible.
        
        Args:
            surface: Pygame surface to render to
        """
        current = self.current()
        if current and hasattr(current, 'draw'):
            current.draw(surface)
    
    def update(self, dt=None):
        """
        Update only the current (top) screen.
        
        Args:
            dt: Delta time (optional)
            
        Returns:
            Result from screen's update method, if any
        """
        current = self.current()
        if current and hasattr(current, 'update'):
            return current.update()
        return None
    
    def handle_event(self, event):
        """
        Delegate event to only the current (top) screen.
        
        Args:
            event: Pygame event
            
        Returns:
            Result from screen's handle_event method, if any
        """
        current = self.current()
        if current and hasattr(current, 'handle_event'):
            return current.handle_event(event)
        return None
