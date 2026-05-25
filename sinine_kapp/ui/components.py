"""Reusable pygame UI primitives used by touchscreen screen classes."""

import pygame
from .styles import Colors


# ---------------------------------------------------------------------------
# Input settings
# ---------------------------------------------------------------------------

USE_FINGER_EVENTS = False
SHOW_SCREEN_NAME = True
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768


# ---------------------------------------------------------------------------
# Input helpers
# ---------------------------------------------------------------------------

def _touch_event_to_screen_pos(event):
    """Map normalized pygame finger coordinates into screen pixels."""
    surface = pygame.display.get_surface()
    if surface is None:
        return None

    width, height = surface.get_size()
    x_norm = max(0.0, min(1.0, event.x))
    y_norm = max(0.0, min(1.0, event.y))
    return int(x_norm * width), int(y_norm * height)


def get_event_pos(event):
    """Return a screen pixel position for supported mouse/touch events."""
    if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
        return event.pos

    if USE_FINGER_EVENTS and event.type in (pygame.FINGERMOTION, pygame.FINGERDOWN):
        return _touch_event_to_screen_pos(event)

    return None


def is_press_event(event):
    """Return True when an event should count as a button press."""
    if event.type == pygame.MOUSEBUTTONDOWN:
        return True

    return USE_FINGER_EVENTS and event.type == pygame.FINGERDOWN


# ---------------------------------------------------------------------------
# Primitive widgets
# ---------------------------------------------------------------------------

class Button:
    """Rectangular button that returns its command_id when pressed."""

    def __init__(self, x, y, width, height, text, font, color, command_id, border_radius=15):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.command_id = command_id
        self.border_radius = border_radius
        self.is_hovered = False

    def draw(self, screen):
        draw_color = self.color
        if self.is_hovered:
            draw_color = (min(self.color[0]+30, 255), min(self.color[1]+30, 255), min(self.color[2]+30, 255))

        pygame.draw.rect(screen, draw_color, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(screen, Colors.WHITE, self.rect, 2, border_radius=self.border_radius)
        
        text_surf = self.font.render(self.text, True, Colors.WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
    def check_input(self, event):
        """Update hover state and return command_id when this button is pressed."""
        pos = get_event_pos(event)
        if event.type == pygame.MOUSEMOTION and pos is not None:
            self.is_hovered = self.rect.collidepoint(pos)
        if is_press_event(event) and pos is not None:
            if self.rect.collidepoint(pos):
                return self.command_id
        return None


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def render_centered(screen, font, text, center, color=Colors.TEXT_PRIMARY):
    """Render text centered around a point."""
    surface = font.render(str(text), True, color)
    screen.blit(surface, surface.get_rect(center=center))
    return surface


def render_at(screen, font, text, position, color=Colors.TEXT_PRIMARY):
    """Render text with its top-left corner at a fixed position."""
    surface = font.render(str(text), True, color)
    screen.blit(surface, position)
    return surface


def wrap_text(text, font, max_width):
    """Wrap text into lines that fit within max_width."""
    words = str(text).split()
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        if font.size(test_line)[0] < max_width:
            current_line.append(word)
            continue

        if current_line:
            lines.append(' '.join(current_line))
        current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    return lines


def draw_button_group(screen, buttons):
    """Draw every button in a list."""
    for button in buttons:
        button.draw(screen)


def handle_button_group(buttons, event):
    """Return the first non-empty command from a group of buttons."""
    for button in buttons:
        result = button.check_input(event)
        if result is not None:
            return result
    return None


def draw_screen_name(screen, fonts, screen_name):
    """Draw the current screen class name for kiosk debugging."""
    if not SHOW_SCREEN_NAME:
        return

    debug_surf = fonts.small.render(screen_name, True, Colors.YELLOW)
    screen.blit(debug_surf, debug_surf.get_rect(topright=(1014, 10)))


def draw_count_list(
    screen,
    fonts,
    items,
    *,
    empty_text,
    start_y=150,
    line_h=38,
    x_name=100,
    x_count=850,
    max_y=600,
    count_prefix='x',
    count_suffix='',
):
    """Draw a name/count list with overflow handling."""
    if not items:
        render_at(screen, fonts.body, empty_text, (x_name, start_y), Colors.GREY)
        return

    for i, (name, count) in enumerate(items.items()):
        y = start_y + i * line_h
        if y > max_y:
            render_at(screen, fonts.small, "... rohkem tooteid", (x_name, y), Colors.GREY)
            break

        render_at(screen, fonts.body, name, (x_name, y))
        render_at(screen, fonts.body, f"{count_prefix}{count}{count_suffix}", (x_count, y))


# ---------------------------------------------------------------------------
# Base screen
# ---------------------------------------------------------------------------

class BaseScreen:
    """Shared base class for screens that mostly draw buttons and text."""

    background = Colors.BACKGROUND

    def __init__(self, fonts):
        self.fonts = fonts
        self.buttons = []

    def fill(self, screen, color=None):
        screen.fill(color or self.background)

    def draw_buttons(self, screen):
        draw_button_group(screen, self.buttons)

    def draw_debug_name(self, screen):
        draw_screen_name(screen, self.fonts, self.__class__.__name__)

    def handle_buttons(self, event):
        return handle_button_group(self.buttons, event)

    def handle_input(self, event):
        return self.handle_buttons(event)
