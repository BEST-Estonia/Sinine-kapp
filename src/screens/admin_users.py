# src/screens/admin_users.py
"""
Admin users list screen
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


class AdminUsersScreen(BaseScreen):
    """Screen showing all registered users"""
    
    def __init__(self, ui_manager, screen_manager, user_info):
        super().__init__(ui_manager, screen_manager)
        self.user_info = user_info
        self.users = self.ui.db.get_all_users()
        self.scroll_offset = 0
        
        # Back button
        back_btn = Button(
            (20, self.ui.height - 200, 200, 70), 
            "← Back", 
            SECONDARY, 
            WHITE
        )
        self.buttons = [back_btn]
        
        # User selection buttons
        self.user_buttons = []
        self._build_user_buttons()
    
    def _build_user_buttons(self):
        """Build clickable buttons for each user"""
        self.user_buttons = []
        user_y = 200
        
        for i, user in enumerate(self.users):
            if user_y > self.ui.height - 350:
                break
            
            btn = Button(
                (30, user_y, self.ui.width - 60, 70),
                f"{user['name']} (Card: {user['card_id']})",
                WHITE,
                TEXT_COLOR,
                shadow=False,
                font_size=28
            )
            btn.user_id = user['id']
            self.user_buttons.append(btn)
            user_y += 80
    
    def on_button_click(self, button):
        if button.text == "← Back":
            self.screen_manager.pop()
        return None
    
    def handle_event(self, event):
        """Handle events including user selection"""
        if event.type == pygame.MOUSEBUTTONUP:
            pos = event.pos
            for btn in self.user_buttons:
                if btn.contains(pos):
                    # Push user details screen
                    from .admin_user_details import AdminUserDetailsScreen
                    details_screen = AdminUserDetailsScreen(
                        self.ui, 
                        self.screen_manager, 
                        self.user_info, 
                        btn.user_id
                    )
                    self.screen_manager.push(details_screen, payload={
                        'admin_info': self.user_info,
                        'user_id': btn.user_id
                    })
                    return None
        
        return super().handle_event(event)
    
    def draw(self, surface):
        # Draw common elements
        self.draw_common_elements(surface)
        
        # Draw title
        title_font = pygame.font.SysFont('Arial', 44, bold=True)
        title_txt = title_font.render("Registered Users", True, TEXT_COLOR)
        title_rect = title_txt.get_rect(centerx=self.ui.width // 2, top=50)
        surface.blit(title_txt, title_rect)
        
        # Draw user count
        count_font = pygame.font.SysFont('Arial', 30)
        count_txt = count_font.render(f"Total: {len(self.users)} users", True, TEAL)
        count_rect = count_txt.get_rect(centerx=self.ui.width // 2, top=110)
        surface.blit(count_txt, count_rect)
        
        # Draw instruction
        instr_font = pygame.font.SysFont('Arial', 26)
        instr_txt = instr_font.render("Tap user to view details", True, GRAY)
        instr_rect = instr_txt.get_rect(centerx=self.ui.width // 2, top=150)
        surface.blit(instr_txt, instr_rect)
        
        # Draw user buttons
        for btn in self.user_buttons:
            # Custom draw for user buttons
            btn_rect = btn.rect
            
            # Background
            pygame.draw.rect(surface, WHITE, btn_rect, border_radius=12)
            pygame.draw.rect(surface, TEAL, btn_rect, width=2, border_radius=12)
            
            # Get user info for this button
            user = next((u for u in self.users if u['id'] == btn.user_id), None)
            if user:
                # Draw user name
                name_font = pygame.font.SysFont('Arial', 32, bold=True)
                name_txt = name_font.render(user['name'], True, TEXT_COLOR)
                surface.blit(name_txt, (btn_rect.x + 15, btn_rect.y + 10))
                
                # Draw card ID
                card_font = pygame.font.SysFont('Arial', 26)
                card_txt = card_font.render(f"Card: {user['card_id']}", True, GRAY)
                surface.blit(card_txt, (btn_rect.x + 15, btn_rect.y + 42))
                
                # Draw admin badge if admin
                if user.get('is_admin'):
                    badge_font = pygame.font.SysFont('Arial', 22, bold=True)
                    badge_txt = badge_font.render("ADMIN", True, WHITE)
                    badge_rect = badge_txt.get_rect()
                    badge_bg = pygame.Rect(
                        btn_rect.right - badge_rect.width - 30,
                        btn_rect.centery - 15,
                        badge_rect.width + 20,
                        30
                    )
                    pygame.draw.rect(surface, (255, 107, 107), badge_bg, border_radius=8)
                    badge_txt_rect = badge_txt.get_rect(center=badge_bg.center)
                    surface.blit(badge_txt, badge_txt_rect)
        
        # Draw main buttons
        button_font = pygame.font.SysFont('Arial', 42, bold=True)
        for btn in self.buttons:
            btn.draw(surface, button_font)
