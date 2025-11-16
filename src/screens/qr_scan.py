# src/screens/qr_scan.py
"""
QR scan screen for borrowing/returning items with basket
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


class QRScanScreen(BaseScreen):
    """Screen for scanning QR codes with multi-item basket support"""
    
    def __init__(self, ui_manager, screen_manager, user_info, action='borrow'):
        super().__init__(ui_manager, screen_manager)
        self.user_info = user_info
        self.action = action  # 'borrow' or 'return'
        self.basket = []  # List of {'qr_code': str, 'name': str, 'quantity': int}
        self.scanning = False
        self.status = "Scan QR code on item..."
        
        title = "Borrow Items" if action == 'borrow' else "Return Items"
        self.title = title
        
        # Buttons
        btn_y = self.ui.height - 220
        btn_width = (self.ui.width - 90) // 3
        
        back_btn = Button(
            (30, btn_y, btn_width, 65), 
            "← Back", 
            SECONDARY, 
            WHITE,
            font_size=36
        )
        
        scan_btn = Button(
            (30 + btn_width + 30, btn_y, btn_width, 65), 
            "Scan Item", 
            TEAL, 
            WHITE,
            font_size=36
        )
        
        done_btn = Button(
            (30 + (btn_width + 30) * 2, btn_y, btn_width, 65), 
            "Done", 
            GREEN, 
            WHITE,
            font_size=36
        )
        
        self.buttons = [back_btn, scan_btn, done_btn]
        
        # Item delete buttons
        self.item_buttons = []
        self._build_item_buttons()
    
    def _build_item_buttons(self):
        """Build delete buttons for each basket item"""
        self.item_buttons = []
        basket_y = 220
        item_y = basket_y + 50
        
        for i, item in enumerate(self.basket):
            # Delete button (small red X)
            delete_btn = Button(
                (self.ui.width - 80, item_y + 10, 50, 40),
                "✕",
                (255, 80, 80),  # RED
                WHITE,
                shadow=False,
                font_size=28
            )
            delete_btn.item_index = i
            self.item_buttons.append(delete_btn)
            item_y += 70
            
            # Don't create buttons for items that won't be visible
            if item_y > self.ui.height - 400:
                break
    
    def on_enter(self, payload=None):
        """Initialize from payload"""
        super().on_enter(payload)
        if payload:
            if 'user_info' in payload:
                self.user_info = payload['user_info']
            if 'action' in payload:
                self.action = payload['action']
                self.title = "Borrow Items" if self.action == 'borrow' else "Return Items"
        # Rebuild item buttons when entering
        self._build_item_buttons()
    
    def on_button_click(self, button):
        if button.text == "← Back":
            # Pop back to previous screen
            self.screen_manager.pop()
        elif button.text == "Scan Item":
            self.scan_item()
        elif button.text == "Done":
            if self.basket:
                # Push finalize/confirmation screen
                from .finalize import FinalizeScreen
                finalize_screen = FinalizeScreen(self.ui, self.screen_manager, self.user_info, self.basket, self.action)
                self.screen_manager.push(finalize_screen, payload={
                    'user_info': self.user_info, 
                    'basket': self.basket, 
                    'action': self.action
                })
            else:
                self.status = "Basket is empty. Scan items first."
        return None
    
    def handle_event(self, event):
        """Handle events including item delete button clicks"""
        # Check item delete buttons first
        if event.type == pygame.MOUSEBUTTONUP:
            pos = event.pos
            for btn in self.item_buttons:
                if btn.contains(pos):
                    # Remove item from basket
                    if btn.item_index < len(self.basket):
                        self.basket.pop(btn.item_index)
                        self._build_item_buttons()
                        self.status = "Item removed from basket"
                    return None
        
        # Handle main button clicks
        return super().handle_event(event)
    
    def scan_item(self):
        """Scan a QR code and add to basket"""
        if not self.scanning:
            self.scanning = True
            self.status = "Scanning QR code..."
            
            # Scan QR code
            qr_code = self.ui.qr.scan()
            
            if not qr_code:
                self.status = "Scan cancelled"
                self.scanning = False
                return
            
            # Look up item in database
            item = self.ui.db.get_item(qr_code)
            
            if not item:
                self.status = f"Unknown item: {qr_code}"
                self.scanning = False
                return
            
            # Check if item already in basket
            found = False
            for basket_item in self.basket:
                if basket_item['qr_code'] == qr_code:
                    basket_item['quantity'] += 1
                    found = True
                    break
            
            if not found:
                self.basket.append({
                    'qr_code': qr_code,
                    'name': item['name'],
                    'quantity': 1
                })
            
            self.status = f"Added: {item['name']}"
            self.scanning = False
            self._build_item_buttons()  # Rebuild buttons after adding item
    
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
        
        # Draw status
        status_font = pygame.font.SysFont('Arial', 32)
        status_txt = status_font.render(self.status, True, TEXT_COLOR)
        status_rect = status_txt.get_rect(centerx=self.ui.width // 2, top=160)
        surface.blit(status_txt, status_rect)
        
        # Draw basket header
        basket_y = 220
        basket_font = pygame.font.SysFont('Arial', 36, bold=True)
        basket_txt = basket_font.render(f"Basket ({len(self.basket)} items)", True, TEAL)
        surface.blit(basket_txt, (30, basket_y))
        
        # Draw basket items
        if self.basket:
            item_y = basket_y + 50
            item_font = pygame.font.SysFont('Arial', 28)
            
            for i, item in enumerate(self.basket):
                # Create item box
                item_box = pygame.Rect(30, item_y, self.ui.width - 60, 60)
                pygame.draw.rect(surface, WHITE, item_box, border_radius=10)
                pygame.draw.rect(surface, GRAY, item_box, width=2, border_radius=10)
                
                # Draw item name
                name_txt = item_font.render(item['name'], True, TEXT_COLOR)
                surface.blit(name_txt, (item_box.x + 15, item_box.y + 10))
                
                # Draw quantity
                qty_txt = item_font.render(f"x{item['quantity']}", True, TEAL)
                qty_rect = qty_txt.get_rect(right=item_box.right - 100, centery=item_box.centery)
                surface.blit(qty_txt, qty_rect)
                
                # Draw delete button for this item
                for btn in self.item_buttons:
                    if btn.item_index == i:
                        btn_font = pygame.font.SysFont('Arial', btn.font_size, bold=True)
                        btn.draw(surface, btn_font)
                
                item_y += 70
                
                # Don't draw too many items (leave room for buttons and Sneaky)
                if item_y > self.ui.height - 400:
                    remaining = len(self.basket) - i - 1
                    if remaining > 0:
                        more_txt = item_font.render(f"...and {remaining} more", True, GRAY)
                        surface.blit(more_txt, (30, item_y))
                    break
        else:
            # Empty basket message
            empty_font = pygame.font.SysFont('Arial', 30)
            empty_txt = empty_font.render("No items scanned yet", True, GRAY)
            empty_rect = empty_txt.get_rect(centerx=self.ui.width // 2, top=basket_y + 80)
            surface.blit(empty_txt, empty_rect)
        
        # Draw buttons
        button_font = pygame.font.SysFont('Arial', 36, bold=True)
        for btn in self.buttons:
            btn.draw(surface, button_font)
