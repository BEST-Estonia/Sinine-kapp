# src/screens/admin_inventory.py
"""
Admin inventory management screen
"""
import pygame
from .base_screen import BaseScreen, WHITE, TEAL, GREEN, RED, TEXT_COLOR, SECONDARY, GRAY
from ui.buttons import Button


class AdminInventoryScreen(BaseScreen):
    """Screen for managing inventory and stock levels"""
    
    def __init__(self, ui_manager, screen_manager, user_info):
        super().__init__(ui_manager, screen_manager)
        self.user_info = user_info
        self.items = self.ui.db.get_all_items()
        self.scroll_offset = 0
        self.selected_item = None
        
        # Back button
        back_btn = Button(
            (20, self.ui.height - 200, 200, 70), 
            "← Back", 
            SECONDARY, 
            WHITE
        )
        self.buttons = [back_btn]
        
        # Item buttons
        self.item_buttons = []
        self._build_item_buttons()
    
    def _build_item_buttons(self):
        """Build +/- buttons for each item"""
        self.item_buttons = []
        item_y = 200
        
        for i, item in enumerate(self.items):
            if item_y > self.ui.height - 380:
                break
            
            # Decrease button
            dec_btn = Button(
                (self.ui.width - 150, item_y + 20, 50, 50),
                "−",
                GRAY,
                TEXT_COLOR,
                shadow=False,
                font_size=32
            )
            dec_btn.item_qr = item['qr_code']
            dec_btn.action = 'decrease'
            
            # Increase button
            inc_btn = Button(
                (self.ui.width - 80, item_y + 20, 50, 50),
                "+",
                TEAL,
                WHITE,
                shadow=False,
                font_size=32
            )
            inc_btn.item_qr = item['qr_code']
            inc_btn.action = 'increase'
            
            self.item_buttons.extend([dec_btn, inc_btn])
            item_y += 90
    
    def on_button_click(self, button):
        if button.text == "← Back":
            self.screen_manager.pop()
            return None
        return None
    
    def handle_event(self, event):
        """Handle events including stock adjustment"""
        if event.type == pygame.MOUSEBUTTONUP:
            pos = event.pos
            for btn in self.item_buttons:
                if btn.contains(pos):
                    if btn.action == 'increase':
                        self.ui.db.adjust_stock(btn.item_qr, 1)
                        self.items = self.ui.db.get_all_items()
                        self._build_item_buttons()
                    elif btn.action == 'decrease':
                        self.ui.db.adjust_stock(btn.item_qr, -1)
                        self.items = self.ui.db.get_all_items()
                        self._build_item_buttons()
                    return None
        
        return super().handle_event(event)
    
    def draw(self, surface):
        # Draw common elements
        self.draw_common_elements(surface)
        
        # Draw title
        title_font = pygame.font.SysFont('Arial', 44, bold=True)
        title_txt = title_font.render("Inventory Manager", True, TEXT_COLOR)
        title_rect = title_txt.get_rect(centerx=self.ui.width // 2, top=50)
        surface.blit(title_txt, title_rect)
        
        # Draw item count
        count_font = pygame.font.SysFont('Arial', 28)
        count_txt = count_font.render(f"{len(self.items)} items in stock", True, TEAL)
        count_rect = count_txt.get_rect(centerx=self.ui.width // 2, top=110)
        surface.blit(count_txt, count_rect)
        
        # Draw instruction
        instr_font = pygame.font.SysFont('Arial', 24)
        instr_txt = instr_font.render("Tap +/− to adjust quantity", True, GRAY)
        instr_rect = instr_txt.get_rect(centerx=self.ui.width // 2, top=148)
        surface.blit(instr_txt, instr_rect)
        
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
            qty_txt = qty_font.render(str(qty), True, qty_color)
            surface.blit(qty_txt, (self.ui.width - 230, item_box.y + 22))
            
            # Draw +/− buttons for this item
            for btn in self.item_buttons:
                if btn.item_qr == item['qr_code']:
                    btn_font = pygame.font.SysFont('Arial', btn.font_size, bold=True)
                    btn.draw(surface, btn_font)
            
            item_y += 90
        
        # Draw main buttons
        button_font = pygame.font.SysFont('Arial', 42, bold=True)
        for btn in self.buttons:
            btn.draw(surface, button_font)
