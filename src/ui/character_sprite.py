# src/ui/character_sprite.py
"""
Character sprite component with state-based expressions.
Displays a character icon that reacts to user actions.
"""
import pygame
from typing import Tuple, Optional
from assets import get_asset_manager
import config


class CharacterState:
    """Character expression states"""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    SURPRISED = "surprised"
    CONFUSED = "confused"
    WAVING = "waving"


class CharacterSprite:
    """
    Character sprite that displays different expressions based on state.
    Positioned in the bottom-right corner of the screen with animations.
    """
    
    def __init__(self, width: int, height: int, size: Tuple[int, int] = (120, 120)):
        """
        Initialize character sprite.
        
        Args:
            width: Screen width
            height: Screen height
            size: Size of the character sprite (width, height)
        """
        self.screen_width = width
        self.screen_height = height
        self.size = size
        self.state = CharacterState.NEUTRAL
        self.assets = get_asset_manager()
        
        # Animation state
        self.bob_offset = 0.0
        self.bob_direction = 1
        self.bob_speed = 30.0  # pixels per second
        self.bob_range = 5  # pixels to bob up and down
        
        # Position - bottom-right corner with padding
        from ui.theme import PADDING_SM
        self.padding = PADDING_SM
        self.x = width - size[0] - self.padding
        self.y = height - size[1] - self.padding
        
        # Load or create placeholder images for each state
        self._images = {}
        self._load_images()
    
    def _load_images(self):
        """Load character images for each state. Create placeholders if not found."""
        # Try to load existing sneaky image as base
        base_image = self.assets.get_sneaky_image(scale=self.size)
        
        if base_image is None:
            # Create a simple placeholder circle
            base_image = self._create_placeholder(self.size, (100, 200, 255))  # Blue
        
        # For now, use color-coded placeholders for different states
        # These can be replaced with actual character expression images later
        self._images[CharacterState.NEUTRAL] = base_image
        self._images[CharacterState.HAPPY] = self._create_placeholder(self.size, (50, 255, 100))  # Green
        self._images[CharacterState.SAD] = self._create_placeholder(self.size, (150, 150, 200))  # Blue-gray
        self._images[CharacterState.SURPRISED] = self._create_placeholder(self.size, (255, 200, 50))  # Orange
        self._images[CharacterState.CONFUSED] = self._create_placeholder(self.size, (200, 150, 255))  # Purple
        self._images[CharacterState.WAVING] = self._create_placeholder(self.size, (255, 150, 150))  # Pink
    
    def _create_placeholder(self, size: Tuple[int, int], color: Tuple[int, int, int]) -> pygame.Surface:
        """
        Create a colored placeholder surface for a character state.
        
        Args:
            size: Size of the placeholder (width, height)
            color: RGB color for the placeholder
            
        Returns:
            Pygame surface with placeholder
        """
        surface = pygame.Surface(size, pygame.SRCALPHA)
        # Draw a circle as placeholder
        center = (size[0] // 2, size[1] // 2)
        radius = min(size[0], size[1]) // 2 - 5
        pygame.draw.circle(surface, color, center, radius)
        # Add a lighter inner circle for dimension
        pygame.draw.circle(surface, tuple(min(c + 50, 255) for c in color), center, radius - 10)
        return surface
    
    def set_state(self, state: str):
        """
        Set the character's expression state.
        
        Args:
            state: One of the CharacterState constants
        """
        if state in [CharacterState.NEUTRAL, CharacterState.HAPPY, CharacterState.SAD,
                     CharacterState.SURPRISED, CharacterState.CONFUSED, CharacterState.WAVING]:
            self.state = state
            # Reset bob animation when state changes
            self.bob_offset = 0.0
    
    def set_happy(self):
        """Convenience method to set happy state"""
        self.set_state(CharacterState.HAPPY)
    
    def set_sad(self):
        """Convenience method to set sad state"""
        self.set_state(CharacterState.SAD)
    
    def set_surprised(self):
        """Convenience method to set surprised state"""
        self.set_state(CharacterState.SURPRISED)
    
    def set_confused(self):
        """Convenience method to set confused state"""
        self.set_state(CharacterState.CONFUSED)
    
    def set_waving(self):
        """Convenience method to set waving state"""
        self.set_state(CharacterState.WAVING)
    
    def set_neutral(self):
        """Convenience method to set neutral state"""
        self.set_state(CharacterState.NEUTRAL)
    
    def update(self, dt: float):
        """
        Update animation state.
        
        Args:
            dt: Delta time in seconds
        """
        # Simple bobbing animation
        self.bob_offset += self.bob_direction * self.bob_speed * dt
        
        # Reverse direction at limits
        if self.bob_offset > self.bob_range:
            self.bob_offset = self.bob_range
            self.bob_direction = -1
        elif self.bob_offset < -self.bob_range:
            self.bob_offset = -self.bob_range
            self.bob_direction = 1
    
    def draw(self, surface: pygame.Surface):
        """
        Draw the character on the surface.
        
        Args:
            surface: Pygame surface to draw on
        """
        # Get current image for state
        image = self._images.get(self.state, self._images[CharacterState.NEUTRAL])
        
        # Apply bobbing animation
        draw_y = int(self.y + self.bob_offset)
        
        # Draw the character
        surface.blit(image, (self.x, draw_y))
    
    def get_rect(self) -> pygame.Rect:
        """
        Get the character's bounding rectangle.
        
        Returns:
            Pygame Rect for the character's position
        """
        return pygame.Rect(self.x, self.y, self.size[0], self.size[1])


class CharacterManager:
    """
    Global character manager singleton to maintain character state across screens.
    Provides centralized character state management.
    """
    _instance: Optional['CharacterManager'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.character: Optional[CharacterSprite] = None
            self._initialized = True
    
    def initialize(self, width: int, height: int, size: Tuple[int, int] = (120, 120)):
        """
        Initialize the character sprite.
        
        Args:
            width: Screen width
            height: Screen height
            size: Character size (width, height)
        """
        self.character = CharacterSprite(width, height, size)
    
    def get_character(self) -> Optional[CharacterSprite]:
        """Get the character sprite instance"""
        return self.character
    
    def set_happy(self):
        """Set character to happy state"""
        if self.character:
            self.character.set_happy()
    
    def set_sad(self):
        """Set character to sad state"""
        if self.character:
            self.character.set_sad()
    
    def set_surprised(self):
        """Set character to surprised state"""
        if self.character:
            self.character.set_surprised()
    
    def set_confused(self):
        """Set character to confused state"""
        if self.character:
            self.character.set_confused()
    
    def set_waving(self):
        """Set character to waving state"""
        if self.character:
            self.character.set_waving()
    
    def set_neutral(self):
        """Set character to neutral state"""
        if self.character:
            self.character.set_neutral()


# Global character manager instance
_character_manager = CharacterManager()


def get_character_manager() -> CharacterManager:
    """
    Get the global character manager instance.
    
    Returns:
        The singleton CharacterManager instance
    """
    return _character_manager
