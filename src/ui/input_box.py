# src/ui/input_box.py
"""
Input box widget for text input
"""
import pygame

# Color constants
WHITE = (255, 255, 255)
TEAL = (32, 178, 170)
GRAY = (200, 200, 200)
TEXT_COLOR = (30, 30, 30)


class InputBox:
    """Text input box with touch-friendly design"""
    
    def __init__(self, rect, placeholder="", font_size=40):
        self.rect = pygame.Rect(rect)
        self.text = ""
        self.placeholder = placeholder
        self.font_size = font_size
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        self.max_length = 50
    
    def draw(self, surface):
        """Draw the input box"""
        # Background
        bg_color = WHITE if self.active else (245, 245, 245)
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=10)
        
        # Border
        border_color = TEAL if self.active else GRAY
        border_width = 3 if self.active else 2
        pygame.draw.rect(surface, border_color, self.rect, width=border_width, border_radius=10)
        
        # Text
        font = pygame.font.SysFont('Arial', self.font_size)
        if self.text:
            txt_surface = font.render(self.text, True, TEXT_COLOR)
        else:
            txt_surface = font.render(self.placeholder, True, (150, 150, 150))
        
        # Position text with padding
        txt_rect = txt_surface.get_rect(midleft=(self.rect.x + 15, self.rect.centery))
        
        # Clip text if too long
        if txt_rect.width > self.rect.width - 50:
            # Show only the end of the text
            visible_width = self.rect.width - 50
            clip_rect = pygame.Rect(txt_rect.right - visible_width, txt_rect.top, visible_width, txt_rect.height)
            surface.set_clip(pygame.Rect(self.rect.x + 15, self.rect.y, self.rect.width - 30, self.rect.height))
            surface.blit(txt_surface, (self.rect.x + 15 - (txt_rect.width - visible_width), txt_rect.y))
            surface.set_clip(None)
        else:
            surface.blit(txt_surface, txt_rect)
        
        # Draw cursor if active
        if self.active and self.cursor_visible and self.text:
            cursor_x = min(txt_rect.right + 3, self.rect.right - 15)
            cursor_y1 = self.rect.centery - self.font_size // 2
            cursor_y2 = self.rect.centery + self.font_size // 2
            pygame.draw.line(surface, TEXT_COLOR, (cursor_x, cursor_y1), (cursor_x, cursor_y2), 2)
    
    def update(self):
        """Update cursor blink"""
        self.cursor_timer += 1
        if self.cursor_timer >= 30:  # Blink every 30 frames
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def handle_event(self, event):
        """Handle input events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            if self.active:
                self.cursor_visible = True
                self.cursor_timer = 0
        
        if self.active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return 'submit'
            elif len(self.text) < self.max_length:
                self.text += event.unicode
        
        return None
    
    def add_char(self, char):
        """Add a character from on-screen keyboard"""
        if len(self.text) < self.max_length:
            self.text += char
    
    def backspace(self):
        """Remove last character"""
        self.text = self.text[:-1]
    
    def clear(self):
        """Clear all text"""
        self.text = ""
    
    def get_text(self):
        """Get current text"""
        return self.text
    
    def set_text(self, text):
        """Set text"""
        self.text = text[:self.max_length]
    
    def contains(self, pos):
        """Check if position is within input box"""
        return self.rect.collidepoint(pos)
