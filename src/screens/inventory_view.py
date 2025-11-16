# src/screens/inventory_view.py
"""
Read-only inventory view screen (for non-admin users)
"""
import pygame
from .base_screen import BaseScreen, WHITE, TEAL, GREEN, RED, TEXT_COLOR, SECONDARY, GRAY
from ui.buttons import Button


class InventoryViewScreen(BaseScreen):
    """Screen for viewing inventory (read-only)"""
    
    def __init__(self, ui_manager, screen_manager):
        super().__init__(ui_manager, screen_manager)
        self.items = self.ui.db.get_all_items()
        self.scroll_offset = 0
        
        # Back button
        back_btn = Button(
            (20, self.ui.height - 200, 200, 70), 
            "← Back", 
            SECONDARY, 
            WHITE
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
        
        # Draw title
        title_font = pygame.font.SysFont('Arial', 44, bold=True)
        title_txt = title_font.render("Stock Inventory", True, TEXT_COLOR)
        title_rect = title_txt.get_rect(centerx=self.ui.width // 2, top=50)
        surface.blit(title_txt, title_rect)
        
        # Draw item count
        count_font = pygame.font.SysFont('Arial', 28)
        count_txt = count_font.render(f"{len(self.items)} items in stock", True, TEAL)
        count_rect = count_txt.get_rect(centerx=self.ui.width // 2, top=110)
        surface.blit(count_txt, count_rect)
        
        # Draw read-only note
        note_font = pygame.font.SysFont('Arial', 24)
        note_txt = note_font.render("(Read-only view)", True, GRAY)
        note_rect = note_txt.get_rect(centerx=self.ui.width // 2, top=148)
        surface.blit(note_txt, note_rect)
        
        # Draw items
        item_y = 200
        item_font = pygame.font.SysFont('Arial', 28)
        
        for i, item in enumerate(self.items):
            if item_y > self.ui.height - 380:
                remaining = len(self.items) - i
                more_txt = item_font.render(f"...and {remaining} more", True, GRAY)
                surface.blit(more_txt, (30, item_y))
                break
            
            # Item box
            item_box = pygame.Rect(30, item_y, self.ui.width - 60, 80)
            pygame.draw.rect(surface, WHITE, item_box, border_radius=12)
            pygame.draw.rect(surface, TEAL, item_box, width=2, border_radius=12)
            
            # Item name
            name_txt = item_font.render(item['name'], True, TEXT_COLOR)
            surface.blit(name_txt, (item_box.x + 15, item_box.y + 12))
            
            # QR code
            qr_font = pygame.font.SysFont('Arial', 22)
            qr_txt = qr_font.render(f"QR: {item['qr_code']}", True, GRAY)
            surface.blit(qr_txt, (item_box.x + 15, item_box.y + 45))
            
            # Quantity with color
            qty = item['quantity']
            qty_color = GREEN if qty > 5 else (RED if qty == 0 else (255, 165, 0))
            qty_font = pygame.font.SysFont('Arial', 36, bold=True)
            qty_txt = qty_font.render(f"Stock: {qty}", True, qty_color)
            qty_rect = qty_txt.get_rect(right=item_box.right - 15, centery=item_box.centery)
            surface.blit(qty_txt, qty_rect)
            
            item_y += 90
        
        # Draw buttons
        button_font = pygame.font.SysFont('Arial', 42, bold=True)
        for btn in self.buttons:
            btn.draw(surface, button_font)
