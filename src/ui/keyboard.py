# src/ui/keyboard.py
"""
On-screen keyboard widget for touch input
"""
import pygame
from ui.theme import WHITE, PRIMARY, GRAY, GRAY_DARK, TEXT_PRIMARY, get_font


class OnScreenKeyboard:
    """Touch-friendly on-screen keyboard"""
    
    # Keyboard layouts
    LAYOUT_LOWERCASE = [
        ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
        ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
        ['SHIFT', 'z', 'x', 'c', 'v', 'b', 'n', 'm', 'BACK'],
        ['SPACE']
    ]
    
    LAYOUT_UPPERCASE = [
        ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
        ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
        ['SHIFT', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', 'BACK'],
        ['SPACE']
    ]
    
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.keys = []
        self.shift_active = False
        self.pressed_key = None
        self.callback = None
        # Cache font
        self._font = get_font(28, bold=True)
        self._build_keyboard()
    
    def _build_keyboard(self):
        """Build keyboard button layout"""
        self.keys = []
        layout = self.LAYOUT_UPPERCASE if self.shift_active else self.LAYOUT_LOWERCASE
        
        key_height = 55
        key_spacing = 8
        row_spacing = 10
        
        y_offset = self.rect.y + 10
        
        for row_idx, row in enumerate(layout):
            row_width = len(row)
            
            if row == ['SPACE']:
                # Special handling for space bar
                key_width = self.rect.width - 20
                x_offset = self.rect.x + 10
                key_rect = pygame.Rect(x_offset, y_offset, key_width, key_height)
                self.keys.append({
                    'rect': key_rect,
                    'char': ' ',
                    'label': 'SPACE',
                    'special': True
                })
            else:
                # Calculate key width for this row
                total_spacing = (row_width - 1) * key_spacing + 20
                available_width = self.rect.width - total_spacing
                key_width = available_width // row_width
                
                # Center the row
                row_total_width = row_width * key_width + (row_width - 1) * key_spacing
                x_offset = self.rect.x + (self.rect.width - row_total_width) // 2
                
                for key in row:
                    if key == 'SHIFT':
                        label = '⇧'
                        char = 'SHIFT'
                        width = key_width * 1.5
                        special = True
                    elif key == 'BACK':
                        label = '⌫'
                        char = 'BACKSPACE'
                        width = key_width * 1.5
                        special = True
                    else:
                        label = key
                        char = key
                        width = key_width
                        special = False
                    
                    key_rect = pygame.Rect(x_offset, y_offset, width, key_height)
                    self.keys.append({
                        'rect': key_rect,
                        'char': char,
                        'label': label,
                        'special': special
                    })
                    x_offset += width + key_spacing
            
            y_offset += key_height + row_spacing
    
    def draw(self, surface):
        """Draw the keyboard"""
        # Draw keyboard background
        bg_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surf, (240, 240, 240, 250), bg_surf.get_rect(), border_radius=15)
        surface.blit(bg_surf, self.rect.topleft)
        
        # Draw keys (use cached font)
        
        for key_info in self.keys:
            key_rect = key_info['rect']
            is_pressed = (self.pressed_key == key_info)
            is_special = key_info['special']
            
            # Determine key color
            if is_special:
                color = GRAY_DARK if not is_pressed else (60, 60, 60)
                text_color = WHITE
            else:
                color = WHITE if not is_pressed else GRAY
                text_color = TEXT_PRIMARY
            
            # Draw key background
            pygame.draw.rect(surface, color, key_rect, border_radius=8)
            
            # Draw key border
            border_color = (180, 180, 180)
            pygame.draw.rect(surface, border_color, key_rect, width=2, border_radius=8)
            
            # Draw key label
            label = key_info['label']
            txt = self._font.render(label, True, text_color)
            txt_rect = txt.get_rect(center=key_rect.center)
            surface.blit(txt, txt_rect)
    
    def handle_event(self, event):
        """Handle touch events and return pressed character"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            for key_info in self.keys:
                if key_info['rect'].collidepoint(pos):
                    self.pressed_key = key_info
                    return None
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.pressed_key:
                pos = event.pos
                if self.pressed_key['rect'].collidepoint(pos):
                    char = self.pressed_key['char']
                    self.pressed_key = None
                    
                    # Handle special keys
                    if char == 'SHIFT':
                        self.shift_active = not self.shift_active
                        self._build_keyboard()
                        return None
                    elif char == 'BACKSPACE':
                        return 'BACKSPACE'
                    else:
                        # Auto-shift off after typing
                        if self.shift_active:
                            self.shift_active = False
                            self._build_keyboard()
                        return char
                
                self.pressed_key = None
        
        return None
    
    def set_callback(self, callback):
        """Set callback function for key presses"""
        self.callback = callback
