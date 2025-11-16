#!/usr/bin/env python3
"""
Generate screenshots showing the character sprite in different states
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import pygame
pygame.init()

import config
from ui.character_sprite import get_character_manager, CharacterState
from ui.theme import draw_gradient_background, BG_GRADIENT_TOP, BG_GRADIENT_BOTTOM, get_font, TEXT_PRIMARY, PRIMARY
from assets import get_asset_manager

# Initialize pygame with visible display
screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
pygame.display.set_caption("Character Sprite Test")

# Load assets and initialize character
assets = get_asset_manager()
assets.preload_assets()

character_mgr = get_character_manager()
character_mgr.initialize(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
character = character_mgr.get_character()

# Create output directory for screenshots
output_dir = Path(__file__).parent / "screenshots"
output_dir.mkdir(exist_ok=True)

# Font for labels
font = get_font(32, bold=True)
label_font = get_font(24)

def draw_test_screen(state_name, state_label):
    """Draw a test screen with character in a specific state"""
    # Draw background
    draw_gradient_background(screen, BG_GRADIENT_TOP, BG_GRADIENT_BOTTOM)
    
    # Draw title
    title = font.render("Character Sprite System", True, TEXT_PRIMARY)
    title_rect = title.get_rect(centerx=config.SCREEN_WIDTH // 2, top=50)
    screen.blit(title, title_rect)
    
    # Draw state label
    state_text = label_font.render(f"State: {state_label}", True, PRIMARY)
    state_rect = state_text.get_rect(centerx=config.SCREEN_WIDTH // 2, top=120)
    screen.blit(state_text, state_rect)
    
    # Draw info text
    info_lines = [
        "The character appears in the bottom-right corner",
        "with a subtle bobbing animation.",
        "",
        "It changes expressions based on user actions:",
        "- Waving: Entering main menu",
        "- Confused: Waiting for card scan",
        "- Happy: Successful authentication",
        "- Sad: Access denied / errors",
        "- Surprised: Card not registered",
    ]
    
    y_pos = 200
    for line in info_lines:
        if line:
            text = label_font.render(line, True, TEXT_PRIMARY)
        else:
            y_pos += 10
            continue
        text_rect = text.get_rect(centerx=config.SCREEN_WIDTH // 2, top=y_pos)
        screen.blit(text, text_rect)
        y_pos += 35
    
    # Draw character
    character.draw(screen)
    
    pygame.display.flip()

# Generate screenshots for each state
states = [
    (CharacterState.NEUTRAL, "Neutral"),
    (CharacterState.WAVING, "Waving (Main Menu)"),
    (CharacterState.CONFUSED, "Confused (Waiting)"),
    (CharacterState.HAPPY, "Happy (Success)"),
    (CharacterState.SAD, "Sad (Error)"),
    (CharacterState.SURPRISED, "Surprised (Not Found)"),
]

print("Generating character state screenshots...")
for i, (state, label) in enumerate(states):
    character.set_state(state)
    
    # Update animation a few times to get different bob positions
    for _ in range(10):
        character.update(0.016)  # ~60fps
    
    draw_test_screen(state, label)
    
    # Save screenshot
    filename = output_dir / f"character_state_{i+1}_{state}.png"
    pygame.image.save(screen, str(filename))
    print(f"  ✓ Saved: {filename.name}")

print(f"\n✓ Generated {len(states)} screenshots in {output_dir}")

# Exit cleanly
pygame.quit()
print("Done!")
