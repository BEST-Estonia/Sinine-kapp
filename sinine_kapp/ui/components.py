# ui_components.py
import pygame
from .styles import Colors

USE_FINGER_EVENTS = False


def _touch_event_to_screen_pos(event):
    surface = pygame.display.get_surface()
    if surface is None:
        return None

    width, height = surface.get_size()
    x_norm = max(0.0, min(1.0, event.x))
    y_norm = max(0.0, min(1.0, event.y))
    return int(x_norm * width), int(y_norm * height)


def get_event_pos(event):
    if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
        return event.pos

    if USE_FINGER_EVENTS and event.type in (pygame.FINGERMOTION, pygame.FINGERDOWN):
        return _touch_event_to_screen_pos(event)

    return None


def is_press_event(event):
    if event.type == pygame.MOUSEBUTTONDOWN:
        return True

    return USE_FINGER_EVENTS and event.type == pygame.FINGERDOWN

class Button:
    
    def __init__(self, x, y, width, height, text, font, color, command_id, border_radius=15):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.command_id = command_id
        self.border_radius = border_radius
        self.is_hovered = False

    def draw(self, screen):
        # Logic to brighten color on hover
        draw_color = self.color
        if self.is_hovered:
            # Simple way to make color lighter: limit at 255
            draw_color = (min(self.color[0]+30, 255), min(self.color[1]+30, 255), min(self.color[2]+30, 255))

        pygame.draw.rect(screen, draw_color, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(screen, Colors.WHITE, self.rect, 2, border_radius=self.border_radius)
        
        # Render text
        text_surf = self.font.render(self.text, True, Colors.WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
    # ... check_input 
    def check_input(self, event):
        pos = get_event_pos(event)
        if event.type == pygame.MOUSEMOTION and pos is not None:
            self.is_hovered = self.rect.collidepoint(pos)
        if is_press_event(event) and pos is not None:
            if self.rect.collidepoint(pos):
                return self.command_id
        return None
