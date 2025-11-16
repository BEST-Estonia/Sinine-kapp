# src/app/screens.py
"""
Screen classes for the Pygame UI
Each screen represents a different view in the application
"""
import pygame
import time
from pathlib import Path


def draw_gradient_background(surface, color_top, color_bottom):
    """Draw a vertical gradient background"""
    height = surface.get_height()
    for y in range(height):
        ratio = y / height
        r = int(color_top[0] * (1 - ratio) + color_bottom[0] * ratio)
        g = int(color_top[1] * (1 - ratio) + color_bottom[1] * ratio)
        b = int(color_top[2] * (1 - ratio) + color_bottom[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (surface.get_width(), y))


# Color constants - Updated color palette
WHITE = (255, 255, 255)
LIGHT_BLUE = (220, 240, 255)
GRADIENT_TOP = (173, 216, 230)  # Light blue
GRADIENT_BOTTOM = (255, 255, 255)  # White
TEAL = (32, 178, 170)  # Primary button color (teal/cyan)
TEAL_DARK = (25, 140, 135)  # Darker teal for pressed/shadow
SECONDARY = (255, 107, 107)  # Secondary button color (soft red/orange)
SECONDARY_DARK = (200, 85, 85)  # Darker secondary for pressed
GRAY = (200, 200, 200)
DARK_GRAY = (60, 60, 60)
GREEN = (50, 200, 100)
RED = (255, 80, 80)
TEXT_COLOR = (30, 30, 30)
SHADOW_COLOR = (0, 0, 0, 60)  # Semi-transparent black for shadows


class Button:
    """Reusable button widget with enhanced visual design"""
    
    def __init__(self, rect, text, color=TEAL, text_color=TEXT_COLOR, shadow=True):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.shadow = shadow
        # Slightly darker color for hover effect
        self.hover_color = tuple(max(c - 20, 0) for c in color)
        self.is_hovered = False
        self.is_pressed = False
    
    def draw(self, surface, font):
        # Determine colors
        if self.is_pressed:
            color = tuple(max(c - 40, 0) for c in self.color)
            offset = 2
        elif self.is_hovered:
            color = self.hover_color
            offset = 0
        else:
            color = self.color
            offset = 0
        
        # Draw shadow
        if self.shadow:
            shadow_rect = self.rect.copy()
            shadow_rect.x += 4
            shadow_rect.y += 4
            # Create a surface for shadow with alpha
            shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surf, (0, 0, 0, 60), shadow_surf.get_rect(), border_radius=15)
            surface.blit(shadow_surf, shadow_rect.topleft)
        
        # Draw main button with gradient effect
        button_rect = self.rect.copy()
        button_rect.y += offset
        
        # Draw button background
        pygame.draw.rect(surface, color, button_rect, border_radius=15)
        
        # Draw subtle top-to-bottom gradient on button
        gradient_surf = pygame.Surface((button_rect.width, button_rect.height), pygame.SRCALPHA)
        for y in range(button_rect.height):
            alpha = int(30 * (1 - y / button_rect.height))  # Fade from 30 to 0
            pygame.draw.line(gradient_surf, (255, 255, 255, alpha), (0, y), (button_rect.width, y))
        surface.blit(gradient_surf, button_rect.topleft)
        
        # Draw border
        border_color = tuple(max(c - 30, 0) for c in color)
        pygame.draw.rect(surface, border_color, button_rect, width=3, border_radius=15)
        
        # Draw text
        txt = font.render(self.text, True, self.text_color)
        txt_rect = txt.get_rect(center=(button_rect.centerx, button_rect.centery))
        surface.blit(txt, txt_rect)
    
    def contains(self, pos):
        return self.rect.collidepoint(pos)
    
    def handle_mouse_motion(self, pos):
        self.is_hovered = self.contains(pos)
    
    def set_pressed(self, pressed):
        self.is_pressed = pressed


class BaseScreen:
    """Base class for all screens"""
    
    def __init__(self, ui_manager):
        self.ui = ui_manager
        self.buttons = []
        self.pressed_button = None
    
    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            for btn in self.buttons:
                if btn.contains(pos):
                    btn.set_pressed(True)
                    self.pressed_button = btn
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.pressed_button:
                self.pressed_button.set_pressed(False)
                pos = event.pos
                if self.pressed_button.contains(pos):
                    result = self.on_button_click(self.pressed_button)
                    self.pressed_button = None
                    return result
                self.pressed_button = None
        elif event.type == pygame.MOUSEMOTION:
            pos = event.pos
            for btn in self.buttons:
                btn.handle_mouse_motion(pos)
        return None
    
    def on_button_click(self, button):
        """Override in subclasses"""
        return None
    
    def update(self):
        """Update screen state"""
        pass
    
    def draw(self, surface):
        """Draw the screen"""
        pass


class MainScreen(BaseScreen):
    """Main menu screen with 4 option buttons in portrait layout"""
    
    def __init__(self, ui_manager):
        super().__init__(ui_manager)
        
        # Load character image
        self.character_img = None
        try:
            img_path = Path(__file__).parent.parent.parent / "assets" / "character.png"
            if img_path.exists():
                self.character_img = pygame.image.load(str(img_path))
                # Scale character to fit portrait layout
                self.character_img = pygame.transform.scale(self.character_img, (150, 150))
        except Exception as e:
            print(f"Could not load character image: {e}")
        
        # Portrait layout - vertically stacked buttons
        padding = 20
        btn_w = self.ui.width - (padding * 2)
        btn_h = 80
        start_y = 380  # Start buttons below character and speech bubble
        spacing = 15
        
        self.buttons = [
            Button((padding, start_y, btn_w, btn_h), "Open doors", TEAL, WHITE),
            Button((padding, start_y + btn_h + spacing, btn_w, btn_h), "Return drink", TEAL, WHITE),
            Button((padding, start_y + (btn_h + spacing) * 2, btn_w, btn_h), "Admin", TEAL, WHITE),
            Button((padding, start_y + (btn_h + spacing) * 3, btn_w, btn_h), "Stock/Inventory", TEAL, WHITE),
        ]
        
        self.button_actions = [
            "open_doors",
            "return_drink", 
            "admin",
            "stock_inventory"
        ]
    
    def on_button_click(self, button):
        idx = self.buttons.index(button)
        return self.button_actions[idx]
    
    def draw(self, surface):
        # Draw gradient background
        draw_gradient_background(surface, GRADIENT_TOP, GRADIENT_BOTTOM)
        
        # Draw character at top center
        char_y = 40
        char_x = (self.ui.width - 150) // 2  # Center the 150px character
        
        if self.character_img:
            surface.blit(self.character_img, (char_x, char_y))
        
        # Draw speech bubble with message
        bubble_y = char_y + 160
        bubble_padding = 20
        bubble_text = "Please pick an option"
        
        # Create speech bubble
        bubble_rect = pygame.Rect(
            bubble_padding, 
            bubble_y, 
            self.ui.width - bubble_padding * 2, 
            100
        )
        
        # Draw bubble shadow
        shadow_rect = bubble_rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 40), shadow_surf.get_rect(), border_radius=20)
        surface.blit(shadow_surf, shadow_rect.topleft)
        
        # Draw bubble background
        pygame.draw.rect(surface, WHITE, bubble_rect, border_radius=20)
        pygame.draw.rect(surface, TEAL, bubble_rect, width=3, border_radius=20)
        
        # Draw bubble pointer (triangle pointing to character)
        pointer_points = [
            (self.ui.width // 2 - 15, bubble_y),
            (self.ui.width // 2 + 15, bubble_y),
            (self.ui.width // 2, bubble_y - 20)
        ]
        pygame.draw.polygon(surface, WHITE, pointer_points)
        pygame.draw.lines(surface, TEAL, False, [pointer_points[0], pointer_points[2], pointer_points[1]], 3)
        
        # Draw text in bubble
        msg = self.ui.large_font.render(bubble_text, True, TEXT_COLOR)
        msg_rect = msg.get_rect(center=bubble_rect.center)
        surface.blit(msg, msg_rect)
        
        # Draw buttons
        for btn in self.buttons:
            btn.draw(surface, self.ui.button_font)


class CardScanScreen(BaseScreen):
    """Screen for scanning RFID cards with user verification"""
    
    def __init__(self, ui_manager, title, on_success_action):
        super().__init__(ui_manager)
        self.title = title
        self.on_success_action = on_success_action
        self.status = "Please scan your card..."
        self.user_info = None
        self.scanning = False
        
        # Load character image (smaller, corner placement)
        self.character_img = None
        try:
            img_path = Path(__file__).parent.parent.parent / "assets" / "character.png"
            if img_path.exists():
                self.character_img = pygame.image.load(str(img_path))
                self.character_img = pygame.transform.scale(self.character_img, (80, 80))
        except Exception as e:
            print(f"Could not load character image: {e}")
        
        # Back button with secondary color
        back_btn = Button(
            (20, self.ui.height - 100, 180, 70), 
            "← Back", 
            SECONDARY, 
            WHITE
        )
        self.buttons.append(back_btn)
    
    def on_button_click(self, button):
        if button.text == "← Back":
            return "main"
        return None
    
    def scan_card(self):
        """Initiate card scanning"""
        if not self.scanning:
            self.scanning = True
            self.status = "Waiting for RFID card..."
            
            # Read RFID (this will prompt in console for mock)
            uid = self.ui.rfid.read()
            
            if not uid:
                self.status = "Card scan cancelled"
                self.scanning = False
                return
            
            # Check database
            user = self.ui.db.get_user_by_rfid(uid)
            
            if user:
                self.user_info = user
                self.status = f"Welcome, {user['name']}!"
                # Wait a moment then proceed
                pygame.time.wait(1000)
                return self.on_success_action
            else:
                self.status = f"Access denied! Card {uid} not registered."
                self.user_info = None
            
            self.scanning = False
        return None
    
    def update(self):
        """Auto-scan when screen is shown"""
        if not self.scanning and not self.user_info:
            result = self.scan_card()
            if result:
                return result
        return None
    
    def draw(self, surface):
        # Draw gradient background
        draw_gradient_background(surface, GRADIENT_TOP, GRADIENT_BOTTOM)
        
        # Draw character in top-right corner
        if self.character_img:
            char_x = self.ui.width - 100
            char_y = 20
            surface.blit(self.character_img, (char_x, char_y))
        
        # Draw title
        title_txt = self.ui.large_font.render(self.title, True, TEXT_COLOR)
        title_rect = title_txt.get_rect(centerx=self.ui.width // 2, top=50)
        surface.blit(title_txt, title_rect)
        
        # Draw card icon/box in center
        card_box = pygame.Rect(
            self.ui.width // 2 - 120,
            250,
            240,
            160
        )
        pygame.draw.rect(surface, WHITE, card_box, border_radius=15)
        pygame.draw.rect(surface, TEAL, card_box, width=4, border_radius=15)
        
        # Draw "RFID" text in card box
        rfid_txt = self.ui.large_font.render("RFID", True, TEAL)
        rfid_rect = rfid_txt.get_rect(center=card_box.center)
        surface.blit(rfid_txt, rfid_rect)
        
        # Draw status below card box
        status_color = GREEN if self.user_info else TEXT_COLOR
        if "denied" in self.status.lower():
            status_color = RED
            
        status_txt = self.ui.status_font.render(self.status, True, status_color)
        status_rect = status_txt.get_rect(center=(self.ui.width // 2, 480))
        surface.blit(status_txt, status_rect)
        
        # Draw user info if available
        if self.user_info:
            info_txt = self.ui.font.render(
                f"Card: {self.user_info['rfid_number']}", 
                True, TEXT_COLOR
            )
            info_rect = info_txt.get_rect(center=(self.ui.width // 2, 540))
            surface.blit(info_txt, info_rect)
        
        # Draw buttons
        for btn in self.buttons:
            btn.draw(surface, self.ui.button_font)


class OpenDoorsScreen(BaseScreen):
    """Screen for opening doors after successful card scan"""
    
    def __init__(self, ui_manager, user_info):
        super().__init__(ui_manager)
        self.user_info = user_info
        self.status = "Door unlocked! Please take your item."
        
        # Load character image (smaller, corner placement)
        self.character_img = None
        try:
            img_path = Path(__file__).parent.parent.parent / "assets" / "character.png"
            if img_path.exists():
                self.character_img = pygame.image.load(str(img_path))
                self.character_img = pygame.transform.scale(self.character_img, (80, 80))
        except Exception as e:
            print(f"Could not load character image: {e}")
        
        # Back button
        back_btn = Button(
            (20, self.ui.height - 100, 180, 70), 
            "← Back", 
            SECONDARY, 
            WHITE
        )
        self.buttons.append(back_btn)
        
        # Simulate reading scales
        self.weight_top = self.ui.scale_top.read_weight()
        self.weight_bottom = self.ui.scale_bottom.read_weight()
    
    def on_button_click(self, button):
        if button.text == "← Back":
            return "main"
        return None
    
    def draw(self, surface):
        # Draw gradient background
        draw_gradient_background(surface, GRADIENT_TOP, GRADIENT_BOTTOM)
        
        # Draw character in top-right corner
        if self.character_img:
            char_x = self.ui.width - 100
            char_y = 20
            surface.blit(self.character_img, (char_x, char_y))
        
        # Draw title
        title = self.ui.large_font.render("Door Access", True, TEXT_COLOR)
        title_rect = title.get_rect(centerx=self.ui.width // 2, top=50)
        surface.blit(title, title_rect)
        
        # Draw user name
        name_txt = self.ui.font.render(f"User: {self.user_info['name']}", True, TEXT_COLOR)
        name_rect = name_txt.get_rect(centerx=self.ui.width // 2, top=130)
        surface.blit(name_txt, name_rect)
        
        # Draw status in a nice box
        status_box = pygame.Rect(40, 220, self.ui.width - 80, 120)
        pygame.draw.rect(surface, WHITE, status_box, border_radius=15)
        pygame.draw.rect(surface, GREEN, status_box, width=4, border_radius=15)
        
        status_txt = self.ui.status_font.render(self.status, True, GREEN)
        status_rect = status_txt.get_rect(center=status_box.center)
        surface.blit(status_txt, status_rect)
        
        # Draw weight info boxes
        y_offset = 380
        box_height = 100
        
        # Top shelf box
        top_box = pygame.Rect(40, y_offset, self.ui.width - 80, box_height)
        pygame.draw.rect(surface, WHITE, top_box, border_radius=12)
        pygame.draw.rect(surface, TEAL, top_box, width=3, border_radius=12)
        
        top_label = self.ui.font.render("Top Shelf", True, TEXT_COLOR)
        top_weight = self.ui.large_font.render(f"{self.weight_top} kg", True, TEAL)
        surface.blit(top_label, (top_box.x + 20, top_box.y + 15))
        surface.blit(top_weight, (top_box.x + 20, top_box.y + 50))
        
        # Bottom shelf box
        bottom_box = pygame.Rect(40, y_offset + box_height + 20, self.ui.width - 80, box_height)
        pygame.draw.rect(surface, WHITE, bottom_box, border_radius=12)
        pygame.draw.rect(surface, TEAL, bottom_box, width=3, border_radius=12)
        
        bottom_label = self.ui.font.render("Bottom Shelf", True, TEXT_COLOR)
        bottom_weight = self.ui.large_font.render(f"{self.weight_bottom} kg", True, TEAL)
        surface.blit(bottom_label, (bottom_box.x + 20, bottom_box.y + 15))
        surface.blit(bottom_weight, (bottom_box.x + 20, bottom_box.y + 50))
        
        # Draw buttons
        for btn in self.buttons:
            btn.draw(surface, self.ui.button_font)


class ReturnDrinkScreen(BaseScreen):
    """Screen for returning drinks after successful card scan"""
    
    def __init__(self, ui_manager, user_info):
        super().__init__(ui_manager)
        self.user_info = user_info
        self.status = "Please scan the QR code on the drink..."
        self.qr_scanned = False
        self.qr_code = None
        
        # Load character image (smaller, corner placement)
        self.character_img = None
        try:
            img_path = Path(__file__).parent.parent.parent / "assets" / "character.png"
            if img_path.exists():
                self.character_img = pygame.image.load(str(img_path))
                self.character_img = pygame.transform.scale(self.character_img, (80, 80))
        except Exception as e:
            print(f"Could not load character image: {e}")
        
        # Back button
        back_btn = Button(
            (20, self.ui.height - 100, 180, 70), 
            "← Back", 
            SECONDARY, 
            WHITE
        )
        self.buttons.append(back_btn)
    
    def on_button_click(self, button):
        if button.text == "← Back":
            return "main"
        return None
    
    def update(self):
        if not self.qr_scanned:
            # Scan QR code
            code = self.ui.qr.scan()
            if code:
                self.qr_code = code
                self.qr_scanned = True
                self.status = f"Return registered! QR: {code}"
            else:
                self.status = "QR scan cancelled"
        return None
    
    def draw(self, surface):
        # Draw gradient background
        draw_gradient_background(surface, GRADIENT_TOP, GRADIENT_BOTTOM)
        
        # Draw character in top-right corner
        if self.character_img:
            char_x = self.ui.width - 100
            char_y = 20
            surface.blit(self.character_img, (char_x, char_y))
        
        # Draw title
        title = self.ui.large_font.render("Return Drink", True, TEXT_COLOR)
        title_rect = title.get_rect(centerx=self.ui.width // 2, top=50)
        surface.blit(title, title_rect)
        
        # Draw user name
        name_txt = self.ui.font.render(f"User: {self.user_info['name']}", True, TEXT_COLOR)
        name_rect = name_txt.get_rect(centerx=self.ui.width // 2, top=130)
        surface.blit(name_txt, name_rect)
        
        # Draw QR code box in center
        qr_box = pygame.Rect(
            self.ui.width // 2 - 120,
            250,
            240,
            240
        )
        pygame.draw.rect(surface, WHITE, qr_box, border_radius=15)
        color = GREEN if self.qr_scanned else TEAL
        pygame.draw.rect(surface, color, qr_box, width=4, border_radius=15)
        
        # Draw "QR" text in box
        qr_txt = self.ui.large_font.render("QR", True, color)
        qr_rect = qr_txt.get_rect(center=qr_box.center)
        surface.blit(qr_txt, qr_rect)
        
        # Draw status below QR box
        status_color = GREEN if self.qr_scanned else TEXT_COLOR
        status_txt = self.ui.status_font.render(self.status, True, status_color)
        status_rect = status_txt.get_rect(center=(self.ui.width // 2, 550))
        surface.blit(status_txt, status_rect)
        
        # Draw buttons
        for btn in self.buttons:
            btn.draw(surface, self.ui.button_font)


class AdminScreen(BaseScreen):
    """Admin panel screen after successful card scan"""
    
    def __init__(self, ui_manager, user_info):
        super().__init__(ui_manager)
        self.user_info = user_info
        
        # Load character image (smaller, corner placement)
        self.character_img = None
        try:
            img_path = Path(__file__).parent.parent.parent / "assets" / "character.png"
            if img_path.exists():
                self.character_img = pygame.image.load(str(img_path))
                self.character_img = pygame.transform.scale(self.character_img, (80, 80))
        except Exception as e:
            print(f"Could not load character image: {e}")
        
        # Get all users
        self.users = self.ui.db.get_all_users()
        
        # Back button
        back_btn = Button(
            (20, self.ui.height - 100, 180, 70), 
            "← Back", 
            SECONDARY, 
            WHITE
        )
        self.buttons.append(back_btn)
    
    def on_button_click(self, button):
        if button.text == "← Back":
            return "main"
        return None
    
    def draw(self, surface):
        # Draw gradient background
        draw_gradient_background(surface, GRADIENT_TOP, GRADIENT_BOTTOM)
        
        # Draw character in top-right corner
        if self.character_img:
            char_x = self.ui.width - 100
            char_y = 20
            surface.blit(self.character_img, (char_x, char_y))
        
        # Draw title
        title = self.ui.large_font.render("Admin Panel", True, TEXT_COLOR)
        title_rect = title.get_rect(centerx=self.ui.width // 2, top=50)
        surface.blit(title, title_rect)
        
        # Draw admin info
        admin_txt = self.ui.font.render(f"Admin: {self.user_info['name']}", True, TEXT_COLOR)
        admin_rect = admin_txt.get_rect(centerx=self.ui.width // 2, top=120)
        surface.blit(admin_txt, admin_rect)
        
        # Draw registered users in a nice list
        list_y = 200
        users_title = self.ui.large_font.render("Registered Users", True, TEAL)
        surface.blit(users_title, (40, list_y))
        
        y_offset = list_y + 60
        for user in self.users:
            # Create a box for each user
            user_box = pygame.Rect(30, y_offset, self.ui.width - 60, 60)
            pygame.draw.rect(surface, WHITE, user_box, border_radius=10)
            pygame.draw.rect(surface, TEAL, user_box, width=2, border_radius=10)
            
            # Draw user info
            user_txt = self.ui.font.render(
                f"Card {user['rfid_number']}: {user['name']}", 
                True, TEXT_COLOR
            )
            surface.blit(user_txt, (user_box.x + 15, user_box.y + 15))
            
            y_offset += 70
            
            if y_offset > self.ui.height - 130:
                break
        
        # Draw buttons
        for btn in self.buttons:
            btn.draw(surface, self.ui.button_font)


class StockInventoryScreen(BaseScreen):
    """Stock/Inventory screen - doesn't require card scan"""
    
    def __init__(self, ui_manager):
        super().__init__(ui_manager)
        
        # Load character image (smaller, corner placement)
        self.character_img = None
        try:
            img_path = Path(__file__).parent.parent.parent / "assets" / "character.png"
            if img_path.exists():
                self.character_img = pygame.image.load(str(img_path))
                self.character_img = pygame.transform.scale(self.character_img, (80, 80))
        except Exception as e:
            print(f"Could not load character image: {e}")
        
        # Mock inventory data
        self.inventory = [
            {"item": "Coca Cola", "quantity": 12},
            {"item": "Sprite", "quantity": 8},
            {"item": "Orange Juice", "quantity": 5},
            {"item": "Water", "quantity": 20},
            {"item": "Energy Drink", "quantity": 3},
        ]
        
        # Back button
        back_btn = Button(
            (20, self.ui.height - 100, 180, 70), 
            "← Back", 
            SECONDARY, 
            WHITE
        )
        self.buttons.append(back_btn)
    
    def on_button_click(self, button):
        if button.text == "← Back":
            return "main"
        return None
    
    def draw(self, surface):
        # Draw gradient background
        draw_gradient_background(surface, GRADIENT_TOP, GRADIENT_BOTTOM)
        
        # Draw character in top-right corner
        if self.character_img:
            char_x = self.ui.width - 100
            char_y = 20
            surface.blit(self.character_img, (char_x, char_y))
        
        # Draw title
        title = self.ui.large_font.render("Stock & Inventory", True, TEXT_COLOR)
        title_rect = title.get_rect(centerx=self.ui.width // 2, top=50)
        surface.blit(title, title_rect)
        
        # Draw inventory list
        y_offset = 150
        for item in self.inventory:
            # Create box for each item
            item_box = pygame.Rect(30, y_offset, self.ui.width - 60, 90)
            pygame.draw.rect(surface, WHITE, item_box, border_radius=12)
            pygame.draw.rect(surface, TEAL, item_box, width=3, border_radius=12)
            
            # Item name
            item_txt = self.ui.font.render(item['item'], True, TEXT_COLOR)
            surface.blit(item_txt, (item_box.x + 15, item_box.y + 15))
            
            # Quantity text
            qty_txt = self.ui.font.render(f"{item['quantity']} units", True, TEXT_COLOR)
            surface.blit(qty_txt, (item_box.x + 15, item_box.y + 50))
            
            # Draw quantity bar
            bar_width = 140
            bar_height = 25
            bar_x = item_box.right - bar_width - 15
            bar_y = item_box.y + 33
            
            # Background bar
            pygame.draw.rect(surface, GRAY, (bar_x, bar_y, bar_width, bar_height), border_radius=8)
            
            # Fill bar based on quantity (max 20)
            fill_width = min(item['quantity'] / 20.0, 1.0) * bar_width
            color = GREEN if item['quantity'] > 5 else RED
            if fill_width > 0:
                pygame.draw.rect(surface, color, (bar_x, bar_y, fill_width, bar_height), border_radius=8)
            
            y_offset += 100
        
        # Draw buttons
        for btn in self.buttons:
            btn.draw(surface, self.ui.button_font)
