# src/screens/main_menu.py
"""
Main menu screen with 4 options
"""
import pygame
from .base_screen import BaseScreen, load_sneaky_image
from ui.buttons import Button
from ui.character_sprite import get_character_manager
from ui.theme import (
    PRIMARY, TEXT_ON_PRIMARY, TEXT_PRIMARY, WHITE, 
    PADDING_MD, SPACING_MD, BUTTON_HEIGHT,
    get_font, FONT_SIZE_HEADING, FONT_SIZE_BUTTON,
    RADIUS_LG, SHADOW
)
from .card_scan import CardScanScreen


class MainMenuScreen(BaseScreen):
    """Main menu screen with 4 option buttons"""
    
    def __init__(self, ui_manager, screen_manager):
        super().__init__(ui_manager, screen_manager)
        
        # Get character manager
        self.character_mgr = get_character_manager()
        
        # Load Sneaky at larger size for main screen
        self.sneaky_large = load_sneaky_image(scale=(180, 180))
        
        # Cache fonts
        self._button_font = get_font(FONT_SIZE_BUTTON, bold=True)
        self._bubble_font = get_font(FONT_SIZE_HEADING, bold=True)
        
        # Portrait layout - vertically stacked buttons
        # Calculate button layout based on screen dimensions
        padding = PADDING_MD
        btn_w = self.ui.width - (padding * 2)
        btn_h = BUTTON_HEIGHT
        start_y = 400  # Start buttons in middle-lower area
        spacing = SPACING_MD
        
        self.buttons = [
            Button((padding, start_y, btn_w, btn_h), "Open Doors", PRIMARY, TEXT_ON_PRIMARY),
            Button((padding, start_y + (btn_h + spacing), btn_w, btn_h), "Return Drink", PRIMARY, TEXT_ON_PRIMARY),
            Button((padding, start_y + (btn_h + spacing) * 2, btn_w, btn_h), "Admin Panel", PRIMARY, TEXT_ON_PRIMARY),
            Button((padding, start_y + (btn_h + spacing) * 3, btn_w, btn_h), "Stock/Inventory", PRIMARY, TEXT_ON_PRIMARY),
        ]
    
    def on_enter(self, payload=None):
        """Called when screen becomes active - set character to waving"""
        super().on_enter(payload)
        self.character_mgr.set_waving()
    
    def on_button_click(self, button):
        """Handle button clicks using screen_manager.push()"""
        if button.text == "Open Doors":
            # Push card scan screen for borrow action
            card_screen = CardScanScreen(self.ui, self.screen_manager, "Open Doors - Scan Card", "borrow")
            self.screen_manager.push(card_screen)
        elif button.text == "Return Drink":
            # Push card scan screen for return action
            card_screen = CardScanScreen(self.ui, self.screen_manager, "Return Drink - Scan Card", "return")
            self.screen_manager.push(card_screen)
        elif button.text == "Admin Panel":
            # Push card scan screen for admin access
            card_screen = CardScanScreen(self.ui, self.screen_manager, "Admin Panel - Scan Card", "admin")
            self.screen_manager.push(card_screen)
        elif button.text == "Stock/Inventory":
            # Push read-only inventory screen
            from .inventory_view import InventoryViewScreen
            inventory_screen = InventoryViewScreen(self.ui, self.screen_manager)
            self.screen_manager.push(inventory_screen)
        return None
    
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
        bubble_padding = PADDING_MD
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
        pygame.draw.rect(shadow_surf, SHADOW, shadow_surf.get_rect(), border_radius=RADIUS_LG)
        surface.blit(shadow_surf, shadow_rect.topleft)
        
        # Draw bubble background
        pygame.draw.rect(surface, WHITE, bubble_rect, border_radius=RADIUS_LG)
        pygame.draw.rect(surface, PRIMARY, bubble_rect, width=3, border_radius=RADIUS_LG)
        
        # Draw bubble pointer (triangle pointing to character)
        pointer_points = [
            (self.ui.width // 2 - 15, bubble_y),
            (self.ui.width // 2 + 15, bubble_y),
            (self.ui.width // 2, bubble_y - 20)
        ]
        pygame.draw.polygon(surface, WHITE, pointer_points)
        pygame.draw.lines(surface, PRIMARY, False, [pointer_points[0], pointer_points[2], pointer_points[1]], 3)
        
        # Draw text in bubble (use cached font)
        msg = self._bubble_font.render(bubble_text, True, TEXT_PRIMARY)
        msg_rect = msg.get_rect(center=bubble_rect.center)
        surface.blit(msg, msg_rect)
        
        # Draw buttons with cached font
        for btn in self.buttons:
            btn.draw(surface, self._button_font)
