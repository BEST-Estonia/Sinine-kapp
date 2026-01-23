# src/main.py
"""
Main entry point for the Simple Camera Application
A simple Pygame app with two buttons: Open Camera and Close Program
"""
import pygame
import sys

# Import configuration
import config

# Import hardware
from hardware.mock_camera import MockCamera

# Import screen manager
from screen_manager import ScreenManager

# Import screens
from screens import MainMenuScreen


class SimpleCameraUI:
    """Main UI manager for the Simple Camera application"""
    
    def __init__(self, camera):
        pygame.init()
        pygame.font.init()
        
        self.width = config.SCREEN_WIDTH
        self.height = config.SCREEN_HEIGHT
        
        # Fullscreen, no borders (configure via config.py)
        flags = 0
        if config.FULLSCREEN:
            flags |= pygame.FULLSCREEN
        if config.NOFRAME:
            flags |= pygame.NOFRAME
        
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), flags)
        pygame.display.set_caption("Simple Camera")
        self.clock = pygame.time.Clock()
        
        # Hardware references
        self.camera = camera
        
        # Screen management with stack-based ScreenManager
        self.screen_manager = ScreenManager()
        
        # Create and load main menu as root screen
        main_screen = MainMenuScreen(self, self.screen_manager)
        self.screen_manager.go_to(main_screen)
        
        self.running = True
    
    def quit(self):
        """Signal the application to quit"""
        self.running = False
    
    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(config.FPS) / 1000.0  # Delta time in seconds
            
            # Handle events - delegate to screen manager
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                
                # Let screen manager delegate to current screen
                self.screen_manager.handle_event(event)
            
            # Update current screen through screen manager
            self.screen_manager.update(dt)
            
            # Render current screen through screen manager
            self.screen_manager.render(self.screen)
            
            pygame.display.flip()
        
        # Cleanup
        pygame.quit()
        sys.exit()


def main():
    """Main entry point"""
    # Instantiate mock hardware
    cam = MockCamera()
    
    # Create and run UI
    ui = SimpleCameraUI(camera=cam)
    ui.run()


if __name__ == "__main__":
    main()
