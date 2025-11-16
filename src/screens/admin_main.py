# src/screens/admin_main.py
"""
Admin main panel screen
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


class AdminMainScreen(BaseScreen):
    """Admin panel main screen with options"""
    
    def __init__(self, ui_manager, screen_manager, user_info):
        super().__init__(ui_manager, screen_manager)
        self.user_info = user_info
        
        # Verify admin access - should already be checked in CardScanScreen
        # but double-check here
        self.access_denied = False
        
        # Buttons
        padding = 30
        btn_w = self.ui.width - (padding * 2)
        btn_h = 80
        start_y = 250
        spacing = 20
        
        if not self.access_denied:
            self.buttons = [
                Button((padding, start_y, btn_w, btn_h), "Users List", TEAL, WHITE),
                Button((padding, start_y + (btn_h + spacing), btn_w, btn_h), "Inventory Manager", TEAL, WHITE),
                Button((padding, start_y + (btn_h + spacing) * 2, btn_w, btn_h), "System Logs", TEAL, WHITE),
                Button((padding, self.ui.height - 200, 200, 70), "← Back", SECONDARY, WHITE),
            ]
        else:
            self.buttons = [
                Button((padding, self.ui.height - 200, 200, 70), "← Back", SECONDARY, WHITE),
            ]
    
    def on_enter(self, payload=None):
        """Initialize from payload"""
        super().on_enter(payload)
        if payload and 'user_info' in payload:
            self.user_info = payload['user_info']
    
    def on_button_click(self, button):
        if button.text == "← Back":
            # Pop back to previous screen
            self.screen_manager.pop()
        elif button.text == "Users List":
            from .admin_users import AdminUsersScreen
            users_screen = AdminUsersScreen(self.ui, self.screen_manager, self.user_info)
            self.screen_manager.push(users_screen, payload={'user_info': self.user_info})
        elif button.text == "Inventory Manager":
            from .admin_inventory import AdminInventoryScreen
            inventory_screen = AdminInventoryScreen(self.ui, self.screen_manager, self.user_info)
            self.screen_manager.push(inventory_screen, payload={'user_info': self.user_info})
        elif button.text == "System Logs":
            from .admin_logs import AdminLogsScreen
            logs_screen = AdminLogsScreen(self.ui, self.screen_manager, self.user_info)
            self.screen_manager.push(logs_screen, payload={'user_info': self.user_info})
        return None
    
    def draw(self, surface):
        # Draw common elements
        self.draw_common_elements(surface)
        
        # Draw title
        title_font = pygame.font.SysFont('Arial', 48, bold=True)
        title_txt = title_font.render("Admin Panel", True, TEXT_COLOR)
        title_rect = title_txt.get_rect(centerx=self.ui.width // 2, top=60)
        surface.blit(title_txt, title_rect)
        
        # Draw admin name
        admin_font = pygame.font.SysFont('Arial', 32)
        admin_txt = admin_font.render(f"Admin: {self.user_info['name']}", True, TEXT_COLOR)
        admin_rect = admin_txt.get_rect(centerx=self.ui.width // 2, top=130)
        surface.blit(admin_txt, admin_rect)
        
        if self.access_denied:
            # Show access denied message
            denied_font = pygame.font.SysFont('Arial', 40, bold=True)
            denied_txt = denied_font.render("Access Denied", True, (255, 80, 80))
            denied_rect = denied_txt.get_rect(centerx=self.ui.width // 2, centery=self.ui.height // 2 - 100)
            surface.blit(denied_txt, denied_rect)
            
            msg_font = pygame.font.SysFont('Arial', 30)
            msg_txt = msg_font.render("Admin privileges required", True, TEXT_COLOR)
            msg_rect = msg_txt.get_rect(centerx=self.ui.width // 2, centery=self.ui.height // 2 - 40)
            surface.blit(msg_txt, msg_rect)
        
        # Draw buttons
        button_font = pygame.font.SysFont('Arial', 44, bold=True)
        for btn in self.buttons:
            btn.draw(surface, button_font)
