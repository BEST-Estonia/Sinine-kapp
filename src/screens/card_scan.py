# src/screens/card_scan.py
"""
Card scan screen for RFID authentication
"""
import pygame
from .base_screen import BaseScreen, WHITE, TEAL, GREEN, RED, TEXT_COLOR, SECONDARY
from ui.buttons import Button


class CardScanScreen(BaseScreen):
    """Screen for scanning RFID cards with user verification"""
    
    def __init__(self, ui_manager, title, next_action):
        super().__init__(ui_manager)
        self.title = title
        self.next_action = next_action  # Where to go on successful scan
        self.status = "Please scan your card..."
        self.user_info = None
        self.scanning = False
        self.scanned = False
        self.admin_only = (next_action == "admin_main")
        
        # Back button
        back_btn = Button(
            (20, self.ui.height - 140, 200, 70), 
            "← Back", 
            SECONDARY, 
            WHITE
        )
        self.buttons.append(back_btn)
    
    def on_button_click(self, button):
        if button.text == "← Back":
            return "main"
        return None
    
    def scan_card(self):
        """Initiate card scanning"""
        if not self.scanning and not self.scanned:
            self.scanning = True
            self.status = "Waiting for card scan..."
            
            # Read RFID (this will prompt in console for mock)
            card_id = self.ui.rfid.read()
            
            if not card_id:
                self.status = "Card scan cancelled"
                self.scanning = False
                return None
            
            # Check database
            user = self.ui.db.get_user_by_card(card_id)
            
            if user:
                # Check admin access if required
                if self.admin_only and not user.get('is_admin'):
                    self.status = f"Access denied! Admin access required."
                    self.user_info = None
                    self.scanned = True
                    self.scanning = False
                    return None
                
                self.user_info = user
                self.status = f"Welcome, {user['name']}!"
                self.scanned = True
                self.scanning = False
                # Wait a moment then proceed
                pygame.time.wait(800)
                return (self.next_action, {'user_info': user})
            else:
                # Card not registered - offer to register
                self.status = f"Card {card_id} not registered."
                self.scanned = True
                self.scanning = False
                # Go to registration screen
                return ("register_user", {'card_id': card_id})
            
        return None
    
    def update(self):
        """Auto-scan when screen is shown"""
        if not self.scanning and not self.scanned:
            result = self.scan_card()
            if result:
                return result
        return None
    
    def draw(self, surface):
        # Draw common elements
        self.draw_common_elements(surface)
        
        # Draw title
        title_font = pygame.font.SysFont('Arial', 48, bold=True)
        title_txt = title_font.render(self.title, True, TEXT_COLOR)
        title_rect = title_txt.get_rect(centerx=self.ui.width // 2, top=60)
        surface.blit(title_txt, title_rect)
        
        # Draw card icon/box in center
        card_box = pygame.Rect(
            self.ui.width // 2 - 140,
            300,
            280,
            180
        )
        pygame.draw.rect(surface, WHITE, card_box, border_radius=15)
        pygame.draw.rect(surface, TEAL, card_box, width=4, border_radius=15)
        
        # Draw "RFID" text in card box
        rfid_font = pygame.font.SysFont('Arial', 52, bold=True)
        rfid_txt = rfid_font.render("RFID", True, TEAL)
        rfid_rect = rfid_txt.get_rect(center=card_box.center)
        surface.blit(rfid_txt, rfid_rect)
        
        # Draw status below card box
        status_color = GREEN if self.user_info else (RED if "denied" in self.status.lower() or "not registered" in self.status.lower() else TEXT_COLOR)
        
        status_font = pygame.font.SysFont('Arial', 36, bold=False)
        # Wrap status text if too long
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
        
        y_pos = 520
        for line in lines:
            status_txt = status_font.render(line, True, status_color)
            status_rect = status_txt.get_rect(center=(self.ui.width // 2, y_pos))
            surface.blit(status_txt, status_rect)
            y_pos += 45
        
        # Draw user info if available
        if self.user_info:
            info_font = pygame.font.SysFont('Arial', 32)
            info_txt = info_font.render(
                f"Card: {self.user_info['card_id']}", 
                True, TEXT_COLOR
            )
            info_rect = info_txt.get_rect(center=(self.ui.width // 2, y_pos + 20))
            surface.blit(info_txt, info_rect)
        
        # Draw buttons
        button_font = pygame.font.SysFont('Arial', 42, bold=True)
        for btn in self.buttons:
            btn.draw(surface, button_font)
