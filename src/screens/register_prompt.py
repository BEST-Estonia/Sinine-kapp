# src/screens/register_prompt.py
"""
Registration prompt screen - asks if user wants to register unrecognized card
"""
import pygame
from .base_screen import BaseScreen, WHITE, TEAL, TEXT_COLOR, SECONDARY, GREEN
from ui.buttons import Button


class RegisterPromptScreen(BaseScreen):
    """Screen asking if user wants to register their card"""
    
    def __init__(self, ui_manager, screen_manager, card_id, next_action):
        super().__init__(ui_manager, screen_manager)
        self.card_id = card_id
        self.next_action = next_action  # 'borrow', 'return', or 'admin'
        
        # Buttons
        btn_width = (self.ui.width - 90) // 2
        btn_y = 450
        
        no_btn = Button(
            (30, btn_y, btn_width, 80), 
            "No", 
            SECONDARY, 
            WHITE,
            font_size=44
        )
        
        yes_btn = Button(
            (30 + btn_width + 30, btn_y, btn_width, 80), 
            "Yes", 
            GREEN, 
            WHITE,
            font_size=44
        )
        
        self.buttons = [no_btn, yes_btn]
    
    def on_enter(self, payload=None):
        """Initialize from payload"""
        super().on_enter(payload)
        if payload:
            if 'card_id' in payload:
                self.card_id = payload['card_id']
            if 'next_action' in payload:
                self.next_action = payload['next_action']
    
    def on_button_click(self, button):
        if button.text == "No":
            # Pop back to card scan, then to main menu
            self.screen_manager.pop()  # Pop this prompt
            self.screen_manager.pop()  # Pop card scan
        elif button.text == "Yes":
            # Go to name entry screen
            from .register_user import RegisterUserScreen
            register_screen = RegisterUserScreen(self.ui, self.screen_manager, self.card_id)
            payload = {
                'card_id': self.card_id,
                'next_action': self.next_action
            }
            self.screen_manager.push(register_screen, payload=payload)
        return None
    
    def draw(self, surface):
        # Draw common elements
        self.draw_common_elements(surface)
        
        # Draw title
        title_font = pygame.font.SysFont('Arial', 48, bold=True)
        title_txt = title_font.render("Card Not Registered", True, TEXT_COLOR)
        title_rect = title_txt.get_rect(centerx=self.ui.width // 2, top=100)
        surface.blit(title_txt, title_rect)
        
        # Draw card info box
        card_box = pygame.Rect(
            self.ui.width // 2 - 140,
            200,
            280,
            120
        )
        pygame.draw.rect(surface, WHITE, card_box, border_radius=15)
        pygame.draw.rect(surface, TEAL, card_box, width=4, border_radius=15)
        
        # Draw card ID
        card_font = pygame.font.SysFont('Arial', 40, bold=True)
        card_txt = card_font.render(f"Card: {self.card_id}", True, TEAL)
        card_rect = card_txt.get_rect(center=card_box.center)
        surface.blit(card_txt, card_rect)
        
        # Draw prompt text
        prompt_y = 360
        prompt_font = pygame.font.SysFont('Arial', 36)
        
        line1 = "This card is not registered."
        line2 = "Would you like to register it?"
        
        line1_txt = prompt_font.render(line1, True, TEXT_COLOR)
        line1_rect = line1_txt.get_rect(centerx=self.ui.width // 2, top=prompt_y)
        surface.blit(line1_txt, line1_rect)
        
        line2_txt = prompt_font.render(line2, True, TEXT_COLOR)
        line2_rect = line2_txt.get_rect(centerx=self.ui.width // 2, top=prompt_y + 50)
        surface.blit(line2_txt, line2_rect)
        
        # Draw buttons
        button_font = pygame.font.SysFont('Arial', 44, bold=True)
        for btn in self.buttons:
            btn.draw(surface, button_font)
