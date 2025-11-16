# src/screens/admin_user_details.py
"""
Admin user details screen showing borrowed items and history
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


class AdminUserDetailsScreen(BaseScreen):
    """Screen showing detailed information about a specific user"""
    
    def __init__(self, ui_manager, screen_manager, admin_info, user_id):
        super().__init__(ui_manager, screen_manager)

        
        # Cache fonts
        self._font_36_bold = get_font(36, bold=True)
        self._font_40_bold = get_font(40, bold=True)
        self._font_28 = get_font(28)
        self._font_24 = get_font(24)
        self._font_32_bold = get_font(32, bold=True)
        self._font_26 = get_font(26)
        self._font_22 = get_font(22)
        self._font_42_bold = get_font(42, bold=True)
        self.admin_info = admin_info
        self.user_id = user_id
        self.user = self.ui.db.get_user_by_id(user_id)
        self.borrowed_items = self.ui.db.get_user_borrows(user_id, include_returned=False)
        self.overdue_items = self.ui.db.get_overdue_items(user_id)
        self.history = self.ui.db.get_user_borrows(user_id, include_returned=True)
        
        # Back button
        back_btn = Button(
            (20, self.ui.height - 200, 200, 70), 
            "← Back", 
            SECONDARY, 
            WHITE
        )
        self.buttons = [back_btn]
    
    def on_enter(self, payload=None):
        """Initialize from payload"""
        super().on_enter(payload)
        if payload:
            if 'admin_info' in payload:
                self.admin_info = payload['admin_info']
            if 'user_id' in payload:
                self.user_id = payload['user_id']
                # Reload user data
                self.user = self.ui.db.get_user_by_id(self.user_id)
                self.borrowed_items = self.ui.db.get_user_borrows(self.user_id, include_returned=False)
                self.overdue_items = self.ui.db.get_overdue_items(self.user_id)
                self.history = self.ui.db.get_user_borrows(self.user_id, include_returned=True)
    
    def on_button_click(self, button):
        if button.text == "← Back":
            # Pop back to admin users screen
            self.screen_manager.pop()
        return None
    
    def draw(self, surface):
        # Draw common elements
        self.draw_common_elements(surface)
        
        if not self.user:
            # User not found
            error_font = self._font_36_bold
            error_txt = error_font.render("User not found", True, RED)
            error_rect = error_txt.get_rect(centerx=self.ui.width // 2, centery=self.ui.height // 2)
            surface.blit(error_txt, error_rect)
        else:
            # Draw title
            title_font = self._font_40_bold
            title_txt = title_font.render(self.user['name'], True, TEXT_COLOR)
            title_rect = title_txt.get_rect(centerx=self.ui.width // 2, top=50)
            surface.blit(title_txt, title_rect)
            
            # Draw card ID
            card_font = self._font_28
            card_txt = card_font.render(f"Card ID: {self.user['card_id']}", True, GRAY)
            card_rect = card_txt.get_rect(centerx=self.ui.width // 2, top=100)
            surface.blit(card_txt, card_rect)
            
            # Draw statistics boxes
            y_pos = 150
            box_width = (self.ui.width - 90) // 2
            box_height = 80
            
            # Borrowed items box
            borrowed_box = pygame.Rect(30, y_pos, box_width, box_height)
            pygame.draw.rect(surface, WHITE, borrowed_box, border_radius=12)
            color = TEAL if len(self.borrowed_items) > 0 else GRAY
            pygame.draw.rect(surface, color, borrowed_box, width=3, border_radius=12)
            
            borrowed_label = self._font_24.render("Borrowed", True, TEXT_COLOR)
            borrowed_count = self._font_40_bold.render(str(len(self.borrowed_items)), True, color)
            surface.blit(borrowed_label, (borrowed_box.x + 15, borrowed_box.y + 15))
            surface.blit(borrowed_count, (borrowed_box.x + 15, borrowed_box.y + 40))
            
            # Overdue items box
            overdue_box = pygame.Rect(30 + box_width + 30, y_pos, box_width, box_height)
            pygame.draw.rect(surface, WHITE, overdue_box, border_radius=12)
            color = RED if len(self.overdue_items) > 0 else GREEN
            pygame.draw.rect(surface, color, overdue_box, width=3, border_radius=12)
            
            overdue_label = self._font_24.render("Overdue", True, TEXT_COLOR)
            overdue_count = self._font_40_bold.render(str(len(self.overdue_items)), True, color)
            surface.blit(overdue_label, (overdue_box.x + 15, overdue_box.y + 15))
            surface.blit(overdue_count, (overdue_box.x + 15, overdue_box.y + 40))
            
            # Draw current borrowed items
            y_pos = 260
            section_font = self._font_32_bold
            section_txt = section_font.render("Currently Borrowed", True, TEAL)
            surface.blit(section_txt, (30, y_pos))
            
            y_pos += 50
            if self.borrowed_items:
                item_font = self._font_26
                for i, borrow in enumerate(self.borrowed_items):
                    if y_pos > self.ui.height - 380:
                        remaining = len(self.borrowed_items) - i
                        more_txt = item_font.render(f"...and {remaining} more", True, GRAY)
                        surface.blit(more_txt, (40, y_pos))
                        break
                    
                    # Item box
                    item_box = pygame.Rect(30, y_pos, self.ui.width - 60, 70)
                    pygame.draw.rect(surface, WHITE, item_box, border_radius=10)
                    
                    # Color based on overdue status
                    is_overdue = any(o['id'] == borrow['id'] for o in self.overdue_items)
                    border_color = RED if is_overdue else TEAL
                    pygame.draw.rect(surface, border_color, item_box, width=2, border_radius=10)
                    
                    # Item name
                    item_txt = item_font.render(borrow['item_name'], True, TEXT_COLOR)
                    surface.blit(item_txt, (item_box.x + 15, item_box.y + 10))
                    
                    # Due date
                    due_text = f"Due: {borrow.get('due_date', 'N/A')}"
                    if is_overdue:
                        due_text += " (OVERDUE)"
                    due_txt = self._font_22.render(due_text, True, border_color)
                    surface.blit(due_txt, (item_box.x + 15, item_box.y + 40))
                    
                    y_pos += 80
            else:
                no_items_font = self._font_28
                no_items_txt = no_items_font.render("No items currently borrowed", True, GRAY)
                surface.blit(no_items_txt, (40, y_pos))
        
        # Draw buttons
        button_font = self._font_42_bold
        for btn in self.buttons:
            btn.draw(surface, button_font)
