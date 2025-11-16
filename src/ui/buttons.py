# src/ui/buttons.py
"""
Enhanced button widget with modern styling
"""
import pygame

# Color constants
WHITE = (255, 255, 255)
TEAL = (32, 178, 170)
TEAL_DARK = (25, 140, 135)
SECONDARY = (255, 107, 107)
SECONDARY_DARK = (200, 85, 85)
TEXT_COLOR = (30, 30, 30)


class Button:
    """Reusable button widget with enhanced visual design"""
    
    def __init__(self, rect, text, color=TEAL, text_color=WHITE, shadow=True, font_size=48):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.shadow = shadow
        self.font_size = font_size
        # Slightly darker color for hover effect
        self.hover_color = tuple(max(c - 20, 0) for c in color)
        self.is_hovered = False
        self.is_pressed = False
        self.enabled = True
    
    def draw(self, surface, font=None):
        """Draw the button on the surface"""
        if font is None:
            font = pygame.font.SysFont('Arial', self.font_size)
        
        # Don't draw if not enabled
        if not self.enabled:
            color = (150, 150, 150)
            text_color = (100, 100, 100)
        else:
            # Determine colors based on state
            if self.is_pressed:
                color = tuple(max(c - 40, 0) for c in self.color)
                offset = 2
                text_color = self.text_color
            elif self.is_hovered:
                color = self.hover_color
                offset = 0
                text_color = self.text_color
            else:
                color = self.color
                offset = 0
                text_color = self.text_color
        
        # Draw shadow
        if self.shadow and self.enabled:
            shadow_rect = self.rect.copy()
            shadow_rect.x += 4
            shadow_rect.y += 4
            shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surf, (0, 0, 0, 60), shadow_surf.get_rect(), border_radius=15)
            surface.blit(shadow_surf, shadow_rect.topleft)
        
        # Draw main button
        button_rect = self.rect.copy()
        button_rect.y += offset
        
        pygame.draw.rect(surface, color, button_rect, border_radius=15)
        
        # Draw subtle gradient
        if self.enabled:
            gradient_surf = pygame.Surface((button_rect.width, button_rect.height), pygame.SRCALPHA)
            for y in range(button_rect.height):
                alpha = int(30 * (1 - y / button_rect.height))
                pygame.draw.line(gradient_surf, (255, 255, 255, alpha), (0, y), (button_rect.width, y))
            surface.blit(gradient_surf, button_rect.topleft)
        
        # Draw border
        border_color = tuple(max(c - 30, 0) for c in color)
        pygame.draw.rect(surface, border_color, button_rect, width=3, border_radius=15)
        
        # Draw text
        txt = font.render(self.text, True, text_color)
        txt_rect = txt.get_rect(center=button_rect.center)
        surface.blit(txt, txt_rect)
    
    def contains(self, pos):
        """Check if position is within button bounds"""
        return self.rect.collidepoint(pos) if self.enabled else False
    
    def handle_mouse_motion(self, pos):
        """Handle mouse motion for hover effect"""
        if self.enabled:
            self.is_hovered = self.contains(pos)
    
    def set_pressed(self, pressed):
        """Set pressed state"""
        if self.enabled:
            self.is_pressed = pressed
    
    def set_enabled(self, enabled):
        """Enable or disable the button"""
        self.enabled = enabled
