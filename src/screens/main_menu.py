# src/screens/main_menu.py
"""
Main menu screen with 4 options
"""
import pygame
from .base_screen import BaseScreen, TEAL, WHITE, TEXT_COLOR
from ui.buttons import Button


class MainMenuScreen(BaseScreen):
    """Main menu screen with 4 option buttons"""
    
    def __init__(self, ui_manager):
        super().__init__(ui_manager)
        
        # Load Sneaky at larger size for main screen
        from .base_screen import load_sneaky_image
        self.sneaky_large = load_sneaky_image(scale=(180, 180))
        
        # Portrait layout - vertically stacked buttons
        padding = 30
        btn_w = self.ui.width - (padding * 2)
        btn_h = 90
        start_y = 400  # Start buttons in middle-lower area
        spacing = 20
        
        self.buttons = [
            Button((padding, start_y, btn_w, btn_h), "Open Doors", TEAL, WHITE),
            Button((padding, start_y + (btn_h + spacing), btn_w, btn_h), "Return Drink", TEAL, WHITE),
            Button((padding, start_y + (btn_h + spacing) * 2, btn_w, btn_h), "Admin Panel", TEAL, WHITE),
            Button((padding, start_y + (btn_h + spacing) * 3, btn_w, btn_h), "Stock/Inventory", TEAL, WHITE),
        ]
        
        self.button_actions = [
            "card_scan_borrow",
            "card_scan_return",
            "card_scan_admin",
            "stock_inventory"
        ]
    
    def on_button_click(self, button):
        idx = self.buttons.index(button)
        return self.button_actions[idx]
    
    def draw(self, surface):
        # Draw common elements
        self.draw_common_elements(surface)
        
        # Draw Sneaky at top center (larger)
        if self.sneaky_large:
            char_x = (self.ui.width - 180) // 2
            char_y = 50
            surface.blit(self.sneaky_large, (char_x, char_y))
        
        # Draw speech bubble with message
        bubble_y = 250
        bubble_padding = 30
        bubble_text = "Please pick an option"
        
        # Create speech bubble
        bubble_rect = pygame.Rect(
            bubble_padding, 
            bubble_y, 
            self.ui.width - bubble_padding * 2, 
            120
        )
        
        # Draw bubble shadow
        shadow_rect = bubble_rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 40), shadow_surf.get_rect(), border_radius=20)
        surface.blit(shadow_surf, shadow_rect.topleft)
        
        # Draw bubble background
        pygame.draw.rect(surface, WHITE, bubble_rect, border_radius=20)
        pygame.draw.rect(surface, TEAL, bubble_rect, width=3, border_radius=20)
        
        # Draw bubble pointer (triangle pointing to character)
        pointer_points = [
            (self.ui.width // 2 - 15, bubble_y),
            (self.ui.width // 2 + 15, bubble_y),
            (self.ui.width // 2, bubble_y - 20)
        ]
        pygame.draw.polygon(surface, WHITE, pointer_points)
        pygame.draw.lines(surface, TEAL, False, [pointer_points[0], pointer_points[2], pointer_points[1]], 3)
        
        # Draw text in bubble
        font = pygame.font.SysFont('Arial', 44, bold=True)
        msg = font.render(bubble_text, True, TEXT_COLOR)
        msg_rect = msg.get_rect(center=bubble_rect.center)
        surface.blit(msg, msg_rect)
        
        # Draw buttons
        button_font = pygame.font.SysFont('Arial', 48, bold=True)
        for btn in self.buttons:
            btn.draw(surface, button_font)
