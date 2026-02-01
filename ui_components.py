# ui_components.py
import pygame
from styles import Colors

class Button:
    
    def __init__(self, x, y, width, height, text, font, color, command_id, border_radius=20, text_color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.command_id = command_id
        self.border_radius = border_radius
        self.is_hovered = False
        # Default to white text on colored buttons
        self.text_color = text_color if text_color is not None else Colors.TEXT_ON_COLOR

    def draw(self, screen):
        # Logic to brighten color on hover and add shadow effect
        draw_color = self.color
        if self.is_hovered:
            # Simple way to make color lighter: limit at 255
            draw_color = (min(self.color[0]+30, 255), min(self.color[1]+30, 255), min(self.color[2]+30, 255))
        
        # Draw subtle shadow for depth
        shadow_rect = self.rect.copy()
        shadow_rect.y += 4
        pygame.draw.rect(screen, (0, 0, 0, 30), shadow_rect, border_radius=self.border_radius)
        
        # Draw main button
        pygame.draw.rect(screen, draw_color, self.rect, border_radius=self.border_radius)
        
        # Draw subtle border only if not hovered
        if not self.is_hovered:
            border_color = (max(self.color[0]-20, 0), max(self.color[1]-20, 0), max(self.color[2]-20, 0))
            pygame.draw.rect(screen, border_color, self.rect, 3, border_radius=self.border_radius)
        
        # Render text
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
    # ... check_input 
    def check_input(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return self.command_id
        return None