# src/assets/asset_manager.py
"""
Asset manager for loading and caching images and other resources.
Ensures assets are loaded once and reused for better performance.
"""
import pygame
from pathlib import Path
from typing import Optional, Tuple, Dict

import config


class AssetManager:
    """
    Singleton asset manager for loading and caching game assets.
    Provides centralized access to images, with automatic caching and conversion.
    """
    _instance: Optional['AssetManager'] = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not AssetManager._initialized:
            self._images: Dict[str, pygame.Surface] = {}
            self._base_path = Path(__file__).parent.parent.parent / config.ASSETS_DIR
            AssetManager._initialized = True
    
    def load_image(self, filename: str, 
                   scale: Optional[Tuple[int, int]] = None,
                   convert_alpha: bool = True) -> Optional[pygame.Surface]:
        """
        Load an image from the assets directory and cache it.
        
        Args:
            filename: Name of the image file
            scale: Optional (width, height) tuple to scale the image
            convert_alpha: Whether to convert the surface with alpha channel
            
        Returns:
            Pygame surface, or None if loading failed
        """
        # Create cache key based on filename and scale
        cache_key = f"{filename}_{scale}" if scale else filename
        
        # Return cached version if available
        if cache_key in self._images:
            return self._images[cache_key]
        
        # Load the image
        img_path = self._base_path / filename
        try:
            if not img_path.exists():
                print(f"Warning: Image not found: {img_path}")
                return None
            
            img = pygame.image.load(str(img_path))
            
            # Scale if requested
            if scale:
                img = pygame.transform.scale(img, scale)
            
            # Convert for better performance
            if convert_alpha:
                img = img.convert_alpha()
            else:
                img = img.convert()
            
            # Cache and return
            self._images[cache_key] = img
            return img
            
        except Exception as e:
            print(f"Error loading image {filename}: {e}")
            return None
    
    def get_sneaky_image(self, scale: Tuple[int, int] = (120, 120)) -> Optional[pygame.Surface]:
        """
        Get the Sneaky character image with optional scaling.
        Convenience method for the mascot image.
        
        Args:
            scale: (width, height) tuple for scaling
            
        Returns:
            Pygame surface of Sneaky, or None if not found
        """
        return self.load_image(config.SNEAKY_IMAGE, scale=scale)
    
    def clear_cache(self):
        """Clear all cached images (useful for memory management or testing)"""
        self._images.clear()
    
    def preload_assets(self):
        """
        Preload commonly used assets at startup.
        Call this during application initialization for better performance.
        """
        # Preload Sneaky at common sizes
        self.get_sneaky_image(scale=(120, 120))
        self.get_sneaky_image(scale=(180, 180))
        
        print(f"Asset Manager: Preloaded {len(self._images)} assets")


# Global asset manager instance
_asset_manager = AssetManager()


def get_asset_manager() -> AssetManager:
    """
    Get the global asset manager instance.
    
    Returns:
        The singleton AssetManager instance
        
    Example:
        assets = get_asset_manager()
        sneaky = assets.get_sneaky_image(scale=(150, 150))
    """
    return _asset_manager
