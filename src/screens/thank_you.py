# src/screens/thank_you.py
"""
Thank you screen after completing transaction
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


class ThankYouScreen(BaseScreen):
    """Screen shown after successful borrow/return transaction"""
    
    def __init__(self, ui_manager, screen_manager, user_info, basket, action='borrow'):
        super().__init__(ui_manager, screen_manager)
        self.user_info = user_info
        self.basket = basket
        self.action = action
        self.auto_return_timer = 0
        self.auto_return_delay = 180  # 6 seconds at 30 FPS
        
        # Load Sneaky at larger size
        from .base_screen import load_sneaky_image
        self.sneaky_large = load_sneaky_image(scale=(150, 150))
        
        # Button
        ok_btn = Button(
            (self.ui.width // 2 - 120, self.ui.height - 200, 240, 70), 
            "OK", 
            TEAL, 
            WHITE,
            font_size=44
        )
        self.buttons = [ok_btn]
    
    def on_enter(self, payload=None):
        """Initialize from payload and reset timer"""
        super().on_enter(payload)
        if payload:
            if 'user_info' in payload:
                self.user_info = payload['user_info']
            if 'basket' in payload:
                self.basket = payload['basket']
            if 'action' in payload:
                self.action = payload['action']
        # Reset auto-return timer when entering
        self.auto_return_timer = 0
    
    def on_button_click(self, button):
        # Pop all screens and go back to main menu
        # Clear the stack and go to main
        from .main_menu import MainMenuScreen
        main_screen = MainMenuScreen(self.ui, self.screen_manager)
        self.screen_manager.go_to(main_screen)
        return None
    
    def update(self):
        """Auto-return to main after delay"""
        self.auto_return_timer += 1
        if self.auto_return_timer >= self.auto_return_delay:
            # Auto return to main menu
            from .main_menu import MainMenuScreen
            main_screen = MainMenuScreen(self.ui, self.screen_manager)
            self.screen_manager.go_to(main_screen)
        return None
    
    def draw(self, surface):
        # Draw common elements
        self.draw_common_elements(surface)
        
        # Draw Sneaky at top
        if self.sneaky_large:
            char_x = (self.ui.width - 150) // 2
            char_y = 80
            surface.blit(self.sneaky_large, (char_x, char_y))
        
        # Draw thank you message
        y_pos = 260
        
        title_font = pygame.font.SysFont('Arial', 48, bold=True)
        title_txt = title_font.render("Thank You!", True, GREEN)
        title_rect = title_txt.get_rect(centerx=self.ui.width // 2, top=y_pos)
        surface.blit(title_txt, title_rect)
        
        # Draw message based on action
        y_pos += 80
        msg_font = pygame.font.SysFont('Arial', 32)
        
        total_items = sum(item['quantity'] for item in self.basket)
        
        if self.action == 'borrow':
            # Format: "Thank you, username! Please return borrowed items by the first Wednesday of next month."
            # Calculate due date
            due_date = self.ui.db.calculate_due_date()
            
            msg1 = f"Thank you, {self.user_info['name']}!"
            msg2 = "Please return borrowed items by"
            msg3 = f"the first Wednesday of next month."
            msg4 = f"(Due: {due_date})"
        else:
            msg1 = f"Thank you, {self.user_info['name']}!"
            msg2 = f"You returned {total_items} item(s)."
            msg3 = "Thank you for returning!"
            msg4 = ""
        
        # Draw messages centered
        msg1_txt = msg_font.render(msg1, True, TEXT_COLOR)
        msg1_rect = msg1_txt.get_rect(centerx=self.ui.width // 2, top=y_pos)
        surface.blit(msg1_txt, msg1_rect)
        
        y_pos += 50
        msg2_txt = msg_font.render(msg2, True, TEXT_COLOR)
        msg2_rect = msg2_txt.get_rect(centerx=self.ui.width // 2, top=y_pos)
        surface.blit(msg2_txt, msg2_rect)
        
        y_pos += 50
        msg3_txt = msg_font.render(msg3, True, TEXT_COLOR)
        msg3_rect = msg3_txt.get_rect(centerx=self.ui.width // 2, top=y_pos)
        surface.blit(msg3_txt, msg3_rect)
        
        if msg4:
            y_pos += 50
            msg4_txt = msg_font.render(msg4, True, TEAL)
            msg4_rect = msg4_txt.get_rect(centerx=self.ui.width // 2, top=y_pos)
            surface.blit(msg4_txt, msg4_rect)
        
        # Draw item summary box
        y_pos += 80
        summary_box = pygame.Rect(40, y_pos, self.ui.width - 80, 200)
        pygame.draw.rect(surface, WHITE, summary_box, border_radius=15)
        pygame.draw.rect(surface, TEAL, summary_box, width=3, border_radius=15)
        
        # Draw items in box
        item_y = summary_box.y + 20
        item_font = pygame.font.SysFont('Arial', 26)
        
        for i, item in enumerate(self.basket):
            if i >= 4:  # Show max 4 items
                remaining = len(self.basket) - 4
                more_txt = item_font.render(f"...and {remaining} more", True, TEXT_COLOR)
                surface.blit(more_txt, (summary_box.x + 20, item_y))
                break
            
            item_txt = item_font.render(f"• {item['name']} x{item['quantity']}", True, TEXT_COLOR)
            surface.blit(item_txt, (summary_box.x + 20, item_y))
            item_y += 35
        
        # Draw buttons
        button_font = pygame.font.SysFont('Arial', 44, bold=True)
        for btn in self.buttons:
            btn.draw(surface, button_font)
