# src/screens/inventory_view.py
"""
Read-only inventory view screen (for non-admin users)
"""
import pygame
from .base_screen import BaseScreen
from ui.theme import (
    PRIMARY, SECONDARY, TEXT_ON_PRIMARY, TEXT_PRIMARY, WHITE, SUCCESS, ERROR, GRAY,
    PADDING_SM, PADDING_MD, SPACING_MD, BUTTON_HEIGHT, BUTTON_HEIGHT_SM,
    get_font, FONT_SIZE_TITLE, FONT_SIZE_HEADING, FONT_SIZE_BODY, FONT_SIZE_BUTTON,
    FONT_SIZE_CAPTION, RADIUS_MD, RADIUS_LG, SHADOW
)
from ui.buttons import Button


class InventoryViewScreen(BaseScreen):
    """Screen for viewing inventory (read-only)"""
    
    def __init__(self, ui_manager, screen_manager):
        super().__init__(ui_manager, screen_manager)
        self.items = self.ui.db.get_all_items()
        self.scroll_offset = 0
        
        # Cache fonts
        self._title_font = get_font(FONT_SIZE_HEADING, bold=True)
        self._count_font = get_font(28)
        self._note_font = get_font(24)
        self._item_font = get_font(28)
        self._qr_font = get_font(FONT_SIZE_CAPTION)
        self._qty_font = get_font(FONT_SIZE_HEADING, bold=True)
        self._button_font = get_font(FONT_SIZE_BUTTON, bold=True)
        
        # Back button
        back_btn = Button(
            (PADDING_SM, self.ui.height - 200, 200, BUTTON_HEIGHT_SM), 
            "← Back", 
            SECONDARY, 
            TEXT_ON_PRIMARY
        )
        self.buttons = [back_btn]
    
    def on_enter(self, payload=None):
        """Refresh items when entering"""
        super().on_enter(payload)
        self.items = self.ui.db.get_all_items()
    
    def on_button_click(self, button):
        if button.text == "← Back":
            self.screen_manager.pop()
        return None
    
    def draw(self, surface):
        # Draw common elements
        self.draw_common_elements(surface)
        
        # Draw title (use cached font)
        title_txt = self._title_font.render("Stock Inventory", True, TEXT_PRIMARY)
        title_rect = title_txt.get_rect(centerx=self.ui.width // 2, top=50)
        surface.blit(title_txt, title_rect)
        
        # Draw item count (use cached font)
        count_txt = self._count_font.render(f"{len(self.items)} items in stock", True, PRIMARY)
        count_rect = count_txt.get_rect(centerx=self.ui.width // 2, top=110)
        surface.blit(count_txt, count_rect)
        
        # Draw read-only note (use cached font)
        note_txt = self._note_font.render("(Read-only view)", True, GRAY)
        note_rect = note_txt.get_rect(centerx=self.ui.width // 2, top=148)
        surface.blit(note_txt, note_rect)
        
        # Draw items
        item_y = 200
        
        for i, item in enumerate(self.items):
            if item_y > self.ui.height - 380:
                remaining = len(self.items) - i
                more_txt = self._item_font.render(f"...and {remaining} more", True, GRAY)
                surface.blit(more_txt, (30, item_y))
                break
            
            # Item box
            item_box = pygame.Rect(30, item_y, self.ui.width - 60, 80)
            pygame.draw.rect(surface, WHITE, item_box, border_radius=12)
            pygame.draw.rect(surface, PRIMARY, item_box, width=2, border_radius=12)
            
            # Item name (use cached font)
            name_txt = self._item_font.render(item['name'], True, TEXT_PRIMARY)
            surface.blit(name_txt, (item_box.x + 15, item_box.y + 12))
            
            # QR code (use cached font)
            qr_txt = self._qr_font.render(f"QR: {item['qr_code']}", True, GRAY)
            surface.blit(qr_txt, (item_box.x + 15, item_box.y + 45))
            
            # Quantity with color (use cached font)
            qty = item['quantity']
            qty_color = SUCCESS if qty > 5 else (ERROR if qty == 0 else (255, 165, 0))
            qty_txt = self._qty_font.render(f"Stock: {qty}", True, qty_color)
            qty_rect = qty_txt.get_rect(right=item_box.right - 15, centery=item_box.centery)
            surface.blit(qty_txt, qty_rect)
            
            item_y += 90
        
        # Draw buttons (use cached font)
        for btn in self.buttons:
            btn.draw(surface, self._button_font)
