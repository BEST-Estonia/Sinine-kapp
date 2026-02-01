#!/usr/bin/env python3
"""
Simple visualization of the Sinine Kapp UI screens.
This creates a mock display showing the default screen without actually running the full app.
"""

import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame
from styles import FontManager, Colors
from ui_components import Button

def visualize_default_screen():
    """Create a visualization of the default welcome screen"""
    pygame.init()
    
    # Create the vertical kiosk display
    screen = pygame.display.set_mode((1080, 1920))
    pygame.display.set_caption("Sinine Kapp - Default Screen Preview")
    
    # Initialize fonts
    fonts = FontManager()
    
    # Create UI elements like in DEFAULT_SCREEN
    btn_drink = Button(140, 800, 800, 200, "Login sisse, tahan juua", fonts.title, Colors.SUCCESS, "START_LOGIN")
    btn_kontohaldus = Button(140, 1750, 800, 120, "KONTOHALDUS", fonts.body, Colors.PRIMARY, "GOTO_OPTIONS")
    
    # Draw the screen
    screen.fill(Colors.BACKGROUND)
    rect = screen.get_rect()
    
    # Welcome header at top
    line1 = fonts.huge.render("Tere tulemast!", True, Colors.TEXT_PRIMARY)
    line2 = fonts.header.render("Sinine Kapp", True, Colors.PRIMARY)
    
    screen.blit(line1, line1.get_rect(center=(rect.centerx, 300)))
    screen.blit(line2, line2.get_rect(center=(rect.centerx, 450)))
    
    # Draw buttons
    btn_drink.draw(screen)
    btn_kontohaldus.draw(screen)
    
    # Footer info
    info_text = fonts.small.render("Puuduta ekraani alustamiseks", True, Colors.TEXT_SECONDARY)
    screen.blit(info_text, info_text.get_rect(center=(rect.centerx, 1600)))
    
    # Resolution indicator
    resolution_text = fonts.tiny.render("1080x1920 Vertical Kiosk Mode", True, Colors.TEXT_SECONDARY)
    screen.blit(resolution_text, resolution_text.get_rect(bottomright=(1070, 1910)))
    
    pygame.display.flip()
    
    # Save screenshot
    pygame.image.save(screen, "default_screen_preview.png")
    print("✓ Screenshot saved to default_screen_preview.png")
    print("✓ Resolution: 1080x1920 (vertical kiosk mode)")
    print("✓ Press any key to exit or close window...")
    
    # Wait for user to close
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                running = False
    
    pygame.quit()

if __name__ == "__main__":
    print("=" * 60)
    print("Sinine Kapp - UI Visualization")
    print("=" * 60)
    print("Creating preview of default welcome screen...")
    print()
    
    try:
        visualize_default_screen()
        print("\n✓ Visualization complete!")
        print("✓ The application now uses a modern vertical kiosk design")
        print("✓ Perfect for fast-food style self-service interfaces")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
