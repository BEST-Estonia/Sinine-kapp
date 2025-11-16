# src/screens/admin_logs.py
"""
Admin system logs screen showing borrow/return history
"""
import pygame
from .base_screen import BaseScreen, WHITE, TEAL, GREEN, RED, TEXT_COLOR, SECONDARY, GRAY
from ui.buttons import Button


class AdminLogsScreen(BaseScreen):
    """Screen showing chronological system logs"""
    
    def __init__(self, ui_manager, screen_manager, user_info):
        super().__init__(ui_manager, screen_manager)
        self.user_info = user_info
        self.logs = self.ui.db.get_all_borrows(limit=100)
        self.scroll_offset = 0
        
        # Back button
        back_btn = Button(
            (20, self.ui.height - 200, 200, 70), 
            "← Back", 
            SECONDARY, 
            WHITE
        )
        self.buttons = [back_btn]
    
    def on_button_click(self, button):
        if button.text == "← Back":
            self.screen_manager.pop()
            return None
        return None
    
    def draw(self, surface):
        # Draw common elements
        self.draw_common_elements(surface)
        
        # Draw title
        title_font = pygame.font.SysFont('Arial', 44, bold=True)
        title_txt = title_font.render("System Logs", True, TEXT_COLOR)
        title_rect = title_txt.get_rect(centerx=self.ui.width // 2, top=50)
        surface.blit(title_txt, title_rect)
        
        # Draw log count
        count_font = pygame.font.SysFont('Arial', 28)
        count_txt = count_font.render(f"{len(self.logs)} recent transactions", True, TEAL)
        count_rect = count_txt.get_rect(centerx=self.ui.width // 2, top=110)
        surface.blit(count_txt, count_rect)
        
        # Draw logs
        log_y = 170
        log_font = pygame.font.SysFont('Arial', 24)
        
        if not self.logs:
            no_logs_txt = log_font.render("No transactions yet", True, GRAY)
            no_logs_rect = no_logs_txt.get_rect(centerx=self.ui.width // 2, top=log_y + 50)
            surface.blit(no_logs_txt, no_logs_rect)
        else:
            for i, log in enumerate(self.logs):
                if log_y > self.ui.height - 380:
                    remaining = len(self.logs) - i
                    more_txt = log_font.render(f"...and {remaining} more", True, GRAY)
                    surface.blit(more_txt, (30, log_y))
                    break
                
                # Log box
                log_box = pygame.Rect(30, log_y, self.ui.width - 60, 100)
                pygame.draw.rect(surface, WHITE, log_box, border_radius=10)
                
                # Color based on return status
                is_returned = log.get('timestamp_returned') is not None
                border_color = GREEN if is_returned else TEAL
                pygame.draw.rect(surface, border_color, log_box, width=2, border_radius=10)
                
                # User name
                user_txt = pygame.font.SysFont('Arial', 26, bold=True).render(
                    log['user_name'], True, TEXT_COLOR
                )
                surface.blit(user_txt, (log_box.x + 15, log_box.y + 10))
                
                # Item name
                item_txt = log_font.render(
                    log['item_name'], True, TEXT_COLOR
                )
                surface.blit(item_txt, (log_box.x + 15, log_box.y + 38))
                
                # Timestamp
                timestamp = log['timestamp_out'][:16] if len(log['timestamp_out']) > 16 else log['timestamp_out']
                time_txt = pygame.font.SysFont('Arial', 20).render(
                    f"Out: {timestamp}", True, GRAY
                )
                surface.blit(time_txt, (log_box.x + 15, log_box.y + 65))
                
                # Return status
                if is_returned:
                    return_time = log['timestamp_returned'][:16] if len(log['timestamp_returned']) > 16 else log['timestamp_returned']
                    status_txt = pygame.font.SysFont('Arial', 20).render(
                        f"Returned: {return_time}", True, GREEN
                    )
                    surface.blit(status_txt, (log_box.x + 15, log_box.y + 82))
                else:
                    # Show due date
                    due_date = log.get('due_date', 'N/A')
                    status_txt = pygame.font.SysFont('Arial', 20, bold=True).render(
                        f"Due: {due_date}", True, TEAL
                    )
                    surface.blit(status_txt, (log_box.x + 15, log_box.y + 82))
                
                log_y += 110
        
        # Draw main buttons
        button_font = pygame.font.SysFont('Arial', 42, bold=True)
        for btn in self.buttons:
            btn.draw(surface, button_font)
