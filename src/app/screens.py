# src/app/screens.py
"""
Screen classes for the Pygame UI
Each screen represents a different view in the application
"""
import pygame
import time
from pathlib import Path

# Color constants
WHITE = (255, 255, 255)
LIGHT_BLUE = (220, 240, 255)
BLUE = (100, 150, 255)
DARK_BLUE = (50, 100, 200)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
GREEN = (50, 200, 100)
RED = (255, 80, 80)
TEXT_COLOR = (20, 20, 20)


class Button:
    """Reusable button widget"""
    
    def __init__(self, rect, text, color=GRAY, text_color=TEXT_COLOR):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.hover_color = tuple(min(c + 30, 255) for c in color)
        self.is_hovered = False
    
    def draw(self, surface, font):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, DARK_GRAY, self.rect, width=2, border_radius=10)
        
        # Draw text
        txt = font.render(self.text, True, self.text_color)
        txt_rect = txt.get_rect(center=self.rect.center)
        surface.blit(txt, txt_rect)
    
    def contains(self, pos):
        return self.rect.collidepoint(pos)
    
    def handle_mouse_motion(self, pos):
        self.is_hovered = self.contains(pos)


class BaseScreen:
    """Base class for all screens"""
    
    def __init__(self, ui_manager):
        self.ui = ui_manager
        self.buttons = []
    
    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            for btn in self.buttons:
                if btn.contains(pos):
                    return self.on_button_click(btn)
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
    """Main menu screen with 4 option buttons"""
    
    def __init__(self, ui_manager):
        super().__init__(ui_manager)
        
        # Load character image
        self.character_img = None
        try:
            img_path = Path(__file__).parent.parent.parent / "assets" / "character.png"
            if img_path.exists():
                self.character_img = pygame.image.load(str(img_path))
                self.character_img = pygame.transform.scale(self.character_img, (180, 180))
        except Exception as e:
            print(f"Could not load character image: {e}")
        
        # Create buttons
        padding = 20
        top_y = 200
        btn_w = (self.ui.width - padding * 3) // 2
        btn_h = 100
        
        self.buttons = [
            Button((padding, top_y, btn_w, btn_h), "Open doors", BLUE),
            Button((padding * 2 + btn_w, top_y, btn_w, btn_h), "Return drink", BLUE),
            Button((padding, top_y + btn_h + padding, btn_w, btn_h), "Admin", BLUE),
            Button((padding * 2 + btn_w, top_y + btn_h + padding, btn_w, btn_h), "Stock/Inventory", BLUE),
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
        surface.fill(WHITE)
        
        # Draw character section
        char_x = 20
        char_y = 10
        
        if self.character_img:
            surface.blit(self.character_img, (char_x, char_y))
            text_x = char_x + 200
        else:
            text_x = char_x
        
        # Draw message
        msg = self.ui.large_font.render("Please pick an option:", True, TEXT_COLOR)
        surface.blit(msg, (text_x, char_y + 80))
        
        # Draw buttons
        for btn in self.buttons:
            btn.draw(surface, self.ui.font)


class CardScanScreen(BaseScreen):
    """Screen for scanning RFID cards with user verification"""
    
    def __init__(self, ui_manager, title, on_success_action):
        super().__init__(ui_manager)
        self.title = title
        self.on_success_action = on_success_action
        self.status = "Please scan your card..."
        self.user_info = None
        self.scanning = False
        
        # Back button
        back_btn = Button((20, self.ui.height - 80, 150, 60), "← Back", GRAY)
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
        surface.fill(WHITE)
        
        # Draw title
        title_txt = self.ui.large_font.render(self.title, True, TEXT_COLOR)
        title_rect = title_txt.get_rect(centerx=self.ui.width // 2, top=40)
        surface.blit(title_txt, title_rect)
        
        # Draw status
        status_color = GREEN if self.user_info else TEXT_COLOR
        if "denied" in self.status.lower():
            status_color = RED
            
        status_txt = self.ui.font.render(self.status, True, status_color)
        status_rect = status_txt.get_rect(center=(self.ui.width // 2, self.ui.height // 2))
        surface.blit(status_txt, status_rect)
        
        # Draw user info if available
        if self.user_info:
            info_txt = self.ui.font.render(
                f"Card: {self.user_info['rfid_number']}", 
                True, TEXT_COLOR
            )
            info_rect = info_txt.get_rect(center=(self.ui.width // 2, self.ui.height // 2 + 50))
            surface.blit(info_txt, info_rect)
        
        # Draw buttons
        for btn in self.buttons:
            btn.draw(surface, self.ui.font)


class OpenDoorsScreen(BaseScreen):
    """Screen for opening doors after successful card scan"""
    
    def __init__(self, ui_manager, user_info):
        super().__init__(ui_manager)
        self.user_info = user_info
        self.status = "Door unlocked! Please take your item."
        
        # Back button
        back_btn = Button((20, self.ui.height - 80, 150, 60), "← Back", GRAY)
        self.buttons.append(back_btn)
        
        # Simulate reading scales
        self.weight_top = self.ui.scale_top.read_weight()
        self.weight_bottom = self.ui.scale_bottom.read_weight()
    
    def on_button_click(self, button):
        if button.text == "← Back":
            return "main"
        return None
    
    def draw(self, surface):
        surface.fill(LIGHT_BLUE)
        
        # Draw title
        title = self.ui.large_font.render("Door Access", True, TEXT_COLOR)
        title_rect = title.get_rect(centerx=self.ui.width // 2, top=40)
        surface.blit(title, title_rect)
        
        # Draw user name
        name_txt = self.ui.font.render(f"User: {self.user_info['name']}", True, TEXT_COLOR)
        name_rect = name_txt.get_rect(centerx=self.ui.width // 2, top=120)
        surface.blit(name_txt, name_rect)
        
        # Draw status
        status_txt = self.ui.font.render(self.status, True, GREEN)
        status_rect = status_txt.get_rect(center=(self.ui.width // 2, 200))
        surface.blit(status_txt, status_rect)
        
        # Draw weight info
        weight_info = f"Top shelf: {self.weight_top}kg  |  Bottom shelf: {self.weight_bottom}kg"
        weight_txt = self.ui.font.render(weight_info, True, TEXT_COLOR)
        weight_rect = weight_txt.get_rect(center=(self.ui.width // 2, 270))
        surface.blit(weight_txt, weight_rect)
        
        # Draw buttons
        for btn in self.buttons:
            btn.draw(surface, self.ui.font)


class ReturnDrinkScreen(BaseScreen):
    """Screen for returning drinks after successful card scan"""
    
    def __init__(self, ui_manager, user_info):
        super().__init__(ui_manager)
        self.user_info = user_info
        self.status = "Please scan the QR code on the drink..."
        self.qr_scanned = False
        self.qr_code = None
        
        # Back button
        back_btn = Button((20, self.ui.height - 80, 150, 60), "← Back", GRAY)
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
        surface.fill(LIGHT_BLUE)
        
        # Draw title
        title = self.ui.large_font.render("Return Drink", True, TEXT_COLOR)
        title_rect = title.get_rect(centerx=self.ui.width // 2, top=40)
        surface.blit(title, title_rect)
        
        # Draw user name
        name_txt = self.ui.font.render(f"User: {self.user_info['name']}", True, TEXT_COLOR)
        name_rect = name_txt.get_rect(centerx=self.ui.width // 2, top=120)
        surface.blit(name_txt, name_rect)
        
        # Draw status
        status_color = GREEN if self.qr_scanned else TEXT_COLOR
        status_txt = self.ui.font.render(self.status, True, status_color)
        status_rect = status_txt.get_rect(center=(self.ui.width // 2, 220))
        surface.blit(status_txt, status_rect)
        
        # Draw buttons
        for btn in self.buttons:
            btn.draw(surface, self.ui.font)


class AdminScreen(BaseScreen):
    """Admin panel screen after successful card scan"""
    
    def __init__(self, ui_manager, user_info):
        super().__init__(ui_manager)
        self.user_info = user_info
        
        # Get all users
        self.users = self.ui.db.get_all_users()
        
        # Back button
        back_btn = Button((20, self.ui.height - 80, 150, 60), "← Back", GRAY)
        self.buttons.append(back_btn)
    
    def on_button_click(self, button):
        if button.text == "← Back":
            return "main"
        return None
    
    def draw(self, surface):
        surface.fill(LIGHT_BLUE)
        
        # Draw title
        title = self.ui.large_font.render("Admin Panel", True, TEXT_COLOR)
        title_rect = title.get_rect(centerx=self.ui.width // 2, top=40)
        surface.blit(title, title_rect)
        
        # Draw admin info
        admin_txt = self.ui.font.render(f"Admin: {self.user_info['name']}", True, TEXT_COLOR)
        admin_rect = admin_txt.get_rect(centerx=self.ui.width // 2, top=100)
        surface.blit(admin_txt, admin_rect)
        
        # Draw registered users
        users_title = self.ui.font.render("Registered Users:", True, TEXT_COLOR)
        surface.blit(users_title, (50, 160))
        
        y_offset = 200
        for user in self.users:
            user_txt = self.ui.font.render(
                f"Card {user['rfid_number']}: {user['name']}", 
                True, TEXT_COLOR
            )
            surface.blit(user_txt, (70, y_offset))
            y_offset += 35
            
            if y_offset > self.ui.height - 120:
                break
        
        # Draw buttons
        for btn in self.buttons:
            btn.draw(surface, self.ui.font)


class StockInventoryScreen(BaseScreen):
    """Stock/Inventory screen - doesn't require card scan"""
    
    def __init__(self, ui_manager):
        super().__init__(ui_manager)
        
        # Mock inventory data
        self.inventory = [
            {"item": "Coca Cola", "quantity": 12},
            {"item": "Sprite", "quantity": 8},
            {"item": "Orange Juice", "quantity": 5},
            {"item": "Water", "quantity": 20},
            {"item": "Energy Drink", "quantity": 3},
        ]
        
        # Back button
        back_btn = Button((20, self.ui.height - 80, 150, 60), "← Back", GRAY)
        self.buttons.append(back_btn)
    
    def on_button_click(self, button):
        if button.text == "← Back":
            return "main"
        return None
    
    def draw(self, surface):
        surface.fill(LIGHT_BLUE)
        
        # Draw title
        title = self.ui.large_font.render("Stock & Inventory", True, TEXT_COLOR)
        title_rect = title.get_rect(centerx=self.ui.width // 2, top=40)
        surface.blit(title, title_rect)
        
        # Draw inventory list
        y_offset = 120
        for item in self.inventory:
            # Item name
            item_txt = self.ui.font.render(
                f"{item['item']}: {item['quantity']} units", 
                True, TEXT_COLOR
            )
            surface.blit(item_txt, (50, y_offset))
            
            # Draw quantity bar
            bar_width = 200
            bar_height = 20
            bar_x = 400
            bar_y = y_offset + 5
            
            # Background bar
            pygame.draw.rect(surface, GRAY, (bar_x, bar_y, bar_width, bar_height), border_radius=5)
            
            # Fill bar based on quantity (max 20)
            fill_width = min(item['quantity'] / 20.0, 1.0) * bar_width
            color = GREEN if item['quantity'] > 5 else RED
            pygame.draw.rect(surface, color, (bar_x, bar_y, fill_width, bar_height), border_radius=5)
            
            y_offset += 50
        
        # Draw buttons
        for btn in self.buttons:
            btn.draw(surface, self.ui.font)
