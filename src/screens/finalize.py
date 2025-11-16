# src/screens/finalize.py
"""
Finalize/Confirmation screen - asks user to close cupboard doors to confirm
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


class FinalizeScreen(BaseScreen):
    """Screen for finalizing borrow/return transaction"""
    
    def __init__(self, ui_manager, screen_manager, user_info, basket, action='borrow'):
        super().__init__(ui_manager, screen_manager)

        
        # Cache fonts
        self._font_44_bold = get_font(44, bold=True)
        self._font_36_bold = get_font(36, bold=True)
        self._font_32_bold = get_font(32, bold=True)
        self._font_28 = get_font(28)
        self.user_info = user_info
        self.basket = basket  # List of {'qr_code': str, 'name': str, 'quantity': int}
        self.action = action  # 'borrow' or 'return'
        
        # Buttons
        btn_y = self.ui.height - 220
        btn_width = (self.ui.width - 90) // 2
        
        back_btn = Button(
            (30, btn_y, btn_width, 65), 
            "Back to QR Scan", 
            SECONDARY, 
            WHITE,
            font_size=32
        )
        
        confirm_btn = Button(
            (30 + btn_width + 30, btn_y, btn_width, 65), 
            f"Confirm {action.title()}", 
            GREEN, 
            WHITE,
            font_size=32
        )
        
        self.buttons = [back_btn, confirm_btn]
    
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
                # Update confirm button text
                self.buttons[1].text = f"Confirm {self.action.title()}"
    
    def on_button_click(self, button):
        if button.text == "Back to QR Scan":
            # Pop back to QR scan screen
            self.screen_manager.pop()
        elif "Confirm" in button.text:
            # Process basket
            self.process_basket()
        return None
    
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
        title_font = self._font_44_bold
        title_text = "Finalize Borrow" if self.action == 'borrow' else "Finalize Return"
        title_txt = title_font.render(title_text, True, TEXT_COLOR)
        title_rect = title_txt.get_rect(centerx=self.ui.width // 2, top=50)
        surface.blit(title_txt, title_rect)
        
        # Draw instruction
        instr_y = 120
        instr_font = self._font_36_bold
        instr1_txt = instr_font.render("Please close the cupboard", True, TEAL)
        instr1_rect = instr1_txt.get_rect(centerx=self.ui.width // 2, top=instr_y)
        surface.blit(instr1_txt, instr1_rect)
        
        instr2_txt = instr_font.render("doors to confirm.", True, TEAL)
        instr2_rect = instr2_txt.get_rect(centerx=self.ui.width // 2, top=instr_y + 45)
        surface.blit(instr2_txt, instr2_rect)
        
        # Draw summary header
        summary_y = 230
        summary_font = self._font_32_bold
        total_items = sum(item['quantity'] for item in self.basket)
        summary_txt = summary_font.render(f"Items to {self.action}: {total_items}", True, TEXT_COLOR)
        summary_rect = summary_txt.get_rect(centerx=self.ui.width // 2, top=summary_y)
        surface.blit(summary_txt, summary_rect)
        
        # Draw items in a box
        items_box = pygame.Rect(30, summary_y + 60, self.ui.width - 60, 450)
        pygame.draw.rect(surface, WHITE, items_box, border_radius=15)
        pygame.draw.rect(surface, TEAL, items_box, width=3, border_radius=15)
        
        # Draw items list
        item_y = items_box.y + 20
        item_font = self._font_28
        
        for i, item in enumerate(self.basket):
            if item_y > items_box.bottom - 50:
                # Show remaining count if needed
                remaining = len(self.basket) - i
                if remaining > 0:
                    more_txt = item_font.render(f"...and {remaining} more items", True, GRAY)
                    more_rect = more_txt.get_rect(centerx=items_box.centerx, top=item_y)
                    surface.blit(more_txt, more_rect)
                break
            
            # Draw item
            item_text = f"• {item['name']}"
            item_txt = item_font.render(item_text, True, TEXT_COLOR)
            surface.blit(item_txt, (items_box.x + 20, item_y))
            
            # Draw quantity on right
            qty_txt = item_font.render(f"x{item['quantity']}", True, TEAL)
            qty_rect = qty_txt.get_rect(right=items_box.right - 20, centery=item_y + 15)
            surface.blit(qty_txt, qty_rect)
            
            item_y += 40
        
        # Draw buttons
        button_font = self._font_32_bold
        for btn in self.buttons:
            btn.draw(surface, button_font)
