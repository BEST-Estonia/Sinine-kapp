# src/screens/basket.py
"""
Basket confirmation screen with item management
"""
import pygame
from .base_screen import BaseScreen
from ui.theme import (
    PRIMARY, SECONDARY, TEXT_ON_PRIMARY, TEXT_PRIMARY, WHITE, SUCCESS, ERROR,
    PADDING_SM, PADDING_MD, SPACING_MD, BUTTON_HEIGHT, BUTTON_HEIGHT_SM,
    get_font, FONT_SIZE_TITLE, FONT_SIZE_HEADING, FONT_SIZE_BODY, FONT_SIZE_BUTTON,
    RADIUS_MD, RADIUS_LG, SHADOW
)
from ui.buttons import Button


class BasketScreen(BaseScreen):
    """Screen for reviewing and confirming basket contents"""
    
    def __init__(self, ui_manager, screen_manager, user_info, basket, action='borrow'):
        super().__init__(ui_manager, screen_manager)
        self.user_info = user_info
        self.basket = basket  # List of {'qr_code': str, 'name': str, 'quantity': int}
        self.action = action  # 'borrow' or 'return'
        self.scroll_offset = 0
        
        title = "Confirm Borrow" if action == 'borrow' else "Confirm Return"
        self.title = title
        
        # Buttons
        btn_y = self.ui.height - 220
        btn_width = (self.ui.width - 90) // 2
        
        back_btn = Button(
            (30, btn_y, btn_width, 65), 
            "← Back", 
            SECONDARY, 
            WHITE,
            font_size=40
        )
        
        confirm_btn = Button(
            (30 + btn_width + 30, btn_y, btn_width, 65), 
            "Confirm", 
            GREEN, 
            WHITE,
            font_size=40
        )
        
        self.buttons = [back_btn, confirm_btn]
        
        # Item management buttons (remove, adjust quantity)
        self.item_buttons = []
        self._build_item_buttons()
    
    def on_enter(self, payload=None):
        """Initialize from payload"""
        super().on_enter(payload)
        if payload:
            if 'user_info' in payload:
                self.user_info = payload['user_info']
            if 'basket' in payload:
                self.basket = payload['basket']
            if 'action' in payload:
                self.action = payload['action']
                self.title = "Confirm Borrow" if self.action == 'borrow' else "Confirm Return"
        self._build_item_buttons()
    
    def _build_item_buttons(self):
        """Build remove/adjust buttons for each item"""
        self.item_buttons = []
        item_y = 230
        
        for i, item in enumerate(self.basket):
            # Remove button (small)
            remove_btn = Button(
                (self.ui.width - 90, item_y + 15, 60, 40),
                "✕",
                RED,
                WHITE,
                shadow=False,
                font_size=30
            )
            remove_btn.item_index = i
            remove_btn.action = 'remove'
            
            # Decrease quantity button
            dec_btn = Button(
                (self.ui.width - 160, item_y + 15, 40, 40),
                "−",
                GRAY,
                TEXT_COLOR,
                shadow=False,
                font_size=30
            )
            dec_btn.item_index = i
            dec_btn.action = 'decrease'
            
            self.item_buttons.extend([remove_btn, dec_btn])
            item_y += 70
    
    def on_button_click(self, button):
        if button.text == "← Back":
            # Pop back to QR scan screen
            self.screen_manager.pop()
        elif button.text == "Confirm":
            # Process basket
            self.process_basket()
        return None
    
    def handle_event(self, event):
        """Handle events including item button clicks"""
        # Check item buttons first
        if event.type == pygame.MOUSEBUTTONUP:
            pos = event.pos
            for btn in self.item_buttons:
                if btn.contains(pos):
                    if btn.action == 'remove':
                        # Remove item from basket
                        if btn.item_index < len(self.basket):
                            self.basket.pop(btn.item_index)
                            self._build_item_buttons()
                    elif btn.action == 'decrease':
                        # Decrease quantity
                        if btn.item_index < len(self.basket):
                            item = self.basket[btn.item_index]
                            item['quantity'] -= 1
                            if item['quantity'] <= 0:
                                self.basket.pop(btn.item_index)
                            self._build_item_buttons()
                    return None
        
        # Handle main button clicks
        return super().handle_event(event)
    
    def process_basket(self):
        """Process the basket (borrow or return items)"""
        if not self.basket:
            # Pop back to main menu
            self.screen_manager.pop()
            self.screen_manager.pop()
            return
        
        # Process each item in basket
        for item in self.basket:
            for _ in range(item['quantity']):
                if self.action == 'borrow':
                    self.ui.db.borrow_item(self.user_info['id'], item['qr_code'])
                else:  # return
                    self.ui.db.return_item(self.user_info['id'], item['qr_code'])
        
        # Push thank you screen
        from .thank_you import ThankYouScreen
        thank_you_screen = ThankYouScreen(self.ui, self.screen_manager, self.user_info, self.basket, self.action)
        self.screen_manager.push(thank_you_screen, payload={
            'user_info': self.user_info,
            'basket': self.basket,
            'action': self.action
        })
    
    def draw(self, surface):
        # Draw common elements
        self.draw_common_elements(surface)
        
        # Draw title
        title_font = pygame.font.SysFont('Arial', 44, bold=True)
        title_txt = title_font.render(self.title, True, TEXT_COLOR)
        title_rect = title_txt.get_rect(centerx=self.ui.width // 2, top=50)
        surface.blit(title_txt, title_rect)
        
        # Draw user name
        user_font = pygame.font.SysFont('Arial', 30)
        user_txt = user_font.render(f"User: {self.user_info['name']}", True, TEXT_COLOR)
        user_rect = user_txt.get_rect(centerx=self.ui.width // 2, top=110)
        surface.blit(user_txt, user_rect)
        
        # Draw summary
        summary_font = pygame.font.SysFont('Arial', 32)
        total_items = sum(item['quantity'] for item in self.basket)
        summary_txt = summary_font.render(f"Total: {total_items} items", True, TEAL)
        summary_rect = summary_txt.get_rect(centerx=self.ui.width // 2, top=160)
        surface.blit(summary_txt, summary_rect)
        
        # Draw basket items
        item_y = 230
        item_font = pygame.font.SysFont('Arial', 28)
        
        for i, item in enumerate(self.basket):
            # Create item box
            item_box = pygame.Rect(30, item_y, self.ui.width - 60, 60)
            pygame.draw.rect(surface, WHITE, item_box, border_radius=10)
            pygame.draw.rect(surface, TEAL, item_box, width=2, border_radius=10)
            
            # Draw item name
            name_txt = item_font.render(item['name'], True, TEXT_COLOR)
            surface.blit(name_txt, (item_box.x + 15, item_box.y + 18))
            
            # Draw quantity
            qty_txt = item_font.render(f"x{item['quantity']}", True, TEAL)
            surface.blit(qty_txt, (item_box.x + 15, item_box.y + 40))
            
            # Draw item buttons (from item_buttons list)
            for btn in self.item_buttons:
                if btn.item_index == i:
                    btn_font = pygame.font.SysFont('Arial', btn.font_size, bold=True)
                    btn.draw(surface, btn_font)
            
            item_y += 70
            
            # Don't draw too many items
            if item_y > self.ui.height - 380:
                remaining = len(self.basket) - i - 1
                if remaining > 0:
                    more_txt = item_font.render(f"...and {remaining} more (scroll down)", True, GRAY)
                    surface.blit(more_txt, (30, item_y))
                break
        
        # Draw buttons
        button_font = pygame.font.SysFont('Arial', 40, bold=True)
        for btn in self.buttons:
            btn.draw(surface, button_font)
