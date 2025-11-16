# src/screens/register_user.py
"""
Register new user screen with on-screen keyboard
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
from ui.input_box import InputBox
from ui.keyboard import OnScreenKeyboard


class RegisterUserScreen(BaseScreen):
    """Screen for registering new users with on-screen keyboard"""
    
    def __init__(self, ui_manager, screen_manager, card_id):
        super().__init__(ui_manager, screen_manager)

        
        # Cache fonts
        self._font_44_bold = get_font(44, bold=True)
        self._font_32 = get_font(32)
        self._font_30 = get_font(30)
        self._font_40_bold = get_font(40, bold=True)
        self.card_id = card_id
        self.status = f"Card {card_id} is not registered."
        self.registered = False
        self.next_action = None  # Will be set from payload
        
        # Input box for name
        self.input_box = InputBox(
            (30, 250, self.ui.width - 60, 70),
            placeholder="Enter your name",
            font_size=38
        )
        self.input_box.active = True
        
        # On-screen keyboard
        keyboard_height = 280
        self.keyboard = OnScreenKeyboard(
            0, 
            self.ui.height - keyboard_height - 140,  # Leave room for Sneaky
            self.ui.width,
            keyboard_height
        )
        
        # Buttons
        btn_width = (self.ui.width - 90) // 2
        
        cancel_btn = Button(
            (30, 350, btn_width, 65), 
            "Cancel", 
            SECONDARY, 
            WHITE
        )
        
        save_btn = Button(
            (30 + btn_width + 30, 350, btn_width, 65), 
            "Register", 
            TEAL, 
            WHITE
        )
        
        self.buttons = [cancel_btn, save_btn]
    
    def on_enter(self, payload=None):
        """Store the next action from payload"""
        super().on_enter(payload)
        if payload and 'next_action' in payload:
            self.next_action = payload['next_action']
        if payload and 'card_id' in payload:
            self.card_id = payload['card_id']
            self.status = f"Card {self.card_id} is not registered."
    
    def on_button_click(self, button):
        if button.text == "Cancel":
            # Pop back to registration prompt
            self.screen_manager.pop()
        elif button.text == "Register":
            name = self.input_box.get_text().strip()
            if name:
                # Add user to database
                success = self.ui.db.add_user(name, self.card_id, is_admin=False)
                if success:
                    self.status = f"Welcome, {name}! Registration successful."
                    self.registered = True
                    pygame.time.wait(1500)
                    
                    # Get the newly created user
                    user = self.ui.db.get_user_by_card(self.card_id)
                    
                    # Pop this registration screen
                    self.screen_manager.pop()
                    
                    # Now push the appropriate next screen based on the action
                    if self.next_action == "admin":
                        # Check if user_id == 1 (won't be since we just registered)
                        # Show access denied or go back to main
                        # For simplicity, just pop back to main (already done above)
                        # The CardScanScreen will handle admin check
                        pass
                    elif self.next_action in ["borrow", "return"]:
                        # Push QR scan screen
                        from .qr_scan import QRScanScreen
                        qr_screen = QRScanScreen(self.ui, self.screen_manager, user, action=self.next_action)
                        self.screen_manager.push(qr_screen, payload={'user_info': user, 'action': self.next_action})
                else:
                    self.status = "Registration failed. Please try again."
            else:
                self.status = "Please enter a name."
        return None
    
    def handle_event(self, event):
        """Handle events including keyboard input"""
        # Handle keyboard input first
        char = self.keyboard.handle_event(event)
        if char:
            if char == 'BACKSPACE':
                self.input_box.backspace()
            else:
                self.input_box.add_char(char)
            return None
        
        # Handle input box
        result = self.input_box.handle_event(event)
        if result == 'submit':
            # Trigger register button
            return self.on_button_click(self.buttons[1])
        
        # Handle button clicks
        return super().handle_event(event)
    
    def update(self):
        """Update input box cursor"""
        self.input_box.update()
        return None
    
    def draw(self, surface):
        # Draw common elements
        self.draw_common_elements(surface)
        
        # Draw title
        title_font = self._font_44_bold
        title_txt = title_font.render("Register New User", True, TEXT_COLOR)
        title_rect = title_txt.get_rect(centerx=self.ui.width // 2, top=60)
        surface.blit(title_txt, title_rect)
        
        # Draw status
        status_font = self._font_32
        status_color = GREEN if self.registered else TEXT_COLOR
        
        # Wrap status text
        max_width = self.ui.width - 60
        words = self.status.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = status_font.render(test_line, True, status_color)
            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        
        y_pos = 140
        for line in lines:
            status_txt = status_font.render(line, True, status_color)
            status_rect = status_txt.get_rect(center=(self.ui.width // 2, y_pos))
            surface.blit(status_txt, status_rect)
            y_pos += 40
        
        # Draw prompt
        prompt_font = self._font_30
        prompt_txt = prompt_font.render("Please enter your name:", True, TEXT_COLOR)
        prompt_rect = prompt_txt.get_rect(x=30, y=210)
        surface.blit(prompt_txt, prompt_rect)
        
        # Draw input box
        self.input_box.draw(surface)
        
        # Draw buttons
        button_font = self._font_40_bold
        for btn in self.buttons:
            btn.draw(surface, button_font)
        
        # Draw keyboard
        self.keyboard.draw(surface)
