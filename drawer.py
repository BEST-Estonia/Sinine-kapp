"""Ekraani juhib funktsioon koodi lõpus run_touchscreen(). Funktsioon ootab kuni main.py lisab järjekorda käsu ja andmed. 
Selle põhjal otsustab run_touchscreen() mis ekraani kuvada. mida ekraanile kuvada, kui status pole quueue kontrollimise vahepeal 
muutunnud siis ekraan jääb samaks kuni järgmise käsuni. Iga erineva state(default, regamisekraan, jne on abifunktsioonid kus on täpsemalt 
kirjeldatud mis ekraanil toimub). Kood saab lisada adnmeid quesse RESPONSE mida main.py saab lugeda.
"""

import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1" #peatab pygame printimast tervitust konsooli
import pygame
import time
import logging
import queue
from PIL import Image, ImageSequence
from ui_components import Button
from styles import FontManager, Colors


class VALIKUVAADE:
    def __init__(self, nimi, fonts):
        
        self.buttons = []
        self.fonts = fonts
        
        self.name_line = f"Tere {nimi}"
        self.question_line = "Tahad jooki võtta või tagasi tuua?"
        
        # Vertical layout with larger buttons
        btn_take = Button(140, 900, 800, 200, "VÕTA JOOK", fonts.title, Colors.SUCCESS, "1")
        self.buttons.append(btn_take)
        
        btn_return = Button(140, 1150, 800, 200, "TOO TAGASI", fonts.title, Colors.PRIMARY, "2")
        self.buttons.append(btn_return)
        
        btn_cancel = Button(290, 1700, 500, 120, "TÜHISTA", fonts.body, Colors.DANGER, False)
        self.buttons.append(btn_cancel)

    def draw(self, screen):
        screen.fill(Colors.BACKGROUND)
        
        # Render greeting on two lines
        line1_surf = self.fonts.huge.render(self.name_line, True, Colors.TEXT_PRIMARY)
        line1_rect = line1_surf.get_rect(center=(540, 300))
        screen.blit(line1_surf, line1_rect)
        
        line2_surf = self.fonts.body.render(self.question_line, True, Colors.TEXT_SECONDARY)
        line2_rect = line2_surf.get_rect(center=(540, 600))
        screen.blit(line2_surf, line2_rect)
        
        for btn in self.buttons:
            btn.draw(screen)
        
        debug_surf = self.fonts.tiny.render(self.__class__.__name__, True, Colors.TEXT_SECONDARY)
        screen.blit(debug_surf, debug_surf.get_rect(topright=(1070, 10)))

    def handle_input(self, event):
        for btn in self.buttons:
            res = btn.check_input(event)
            if res is not None: return res
        return None

class VÄLJASTATUD_JOOGID:
    def __init__(self, payload_data, fonts):
        self.fonts = fonts
        # payload_data is expected to be a dict: {"Drink Name": count, ...}
        self.items = payload_data if isinstance(payload_data, dict) else {}

        # Create a confirm button
        self.buttons = []
        btn = Button(140, 1700, 800, 150, "Kinnita", fonts.title, Colors.SUCCESS, True)
        self.buttons.append(btn)

    def draw(self, screen):
        screen.fill(Colors.BACKGROUND)

        # Title
        title_surf = self.fonts.huge.render("Väljastatud joogid", True, Colors.TEXT_PRIMARY)
        title_rect = title_surf.get_rect(center=(540, 250))
        screen.blit(title_surf, title_rect)

        # List items
        start_y = 500
        line_h = 80
        if not self.items:
            empty_surf = self.fonts.body.render("Ühtegi toodet ei leitud", True, Colors.TEXT_SECONDARY)
            empty_rect = empty_surf.get_rect(center=(540, start_y))
            screen.blit(empty_surf, empty_rect)
        else:
            x_name = 140
            x_count = 880
            for i, (name, count) in enumerate(self.items.items()):
                y = start_y + i * line_h
                # Limit drawing to screen height
                if y > 1400:
                    more_surf = self.fonts.body.render("... rohkem tooteid", True, Colors.TEXT_SECONDARY)
                    screen.blit(more_surf, (140, y))
                    break
                name_surf = self.fonts.body.render(str(name), True, Colors.TEXT_PRIMARY)
                count_surf = self.fonts.body.render(f"x{count}", True, Colors.TEXT_PRIMARY)
                screen.blit(name_surf, (x_name, y))
                screen.blit(count_surf, (x_count, y))

        # Draw buttons
        for btn in self.buttons:
            btn.draw(screen)
            
        debug_surf = self.fonts.tiny.render(self.__class__.__name__, True, Colors.WARNING)
        screen.blit(debug_surf, debug_surf.get_rect(topright=(1070, 10)))

    def handle_input(self, event):
        # Let buttons process hover/clicks
        for btn in self.buttons:
            result = btn.check_input(event)
            if result:
                return result
        return None

class UKSE_AVAMINE_TAGASTAMINE:
    def __init__(self, payload_data, fonts):
        """
        Kuvatakse mis jooke kasutaja peab tagastama.
        payload_data is a list of tuples: [(productname, barcode, date_taken), ...]
        Groups drinks by product name and counts them.
        """
        self.fonts = fonts
        self.drink_counts = {}  # Will store {"drink_name": count}
        
        # Process the payload - group by product name and count
        if isinstance(payload_data, list):
            for product_name, barcode, date_taken in payload_data:
                if product_name in self.drink_counts:
                    self.drink_counts[product_name] += 1
                else:
                    self.drink_counts[product_name] = 1
        
        # Create continue button
        self.buttons = []
        btn = Button(140, 1700, 800, 150, "Jätka", fonts.title, Colors.SUCCESS, True)
        self.buttons.append(btn)
    
    def draw(self, screen):
        screen.fill(Colors.BACKGROUND)
        
        # Title
        title_surf = self.fonts.huge.render("Tagastamist ootavad joogid", True, Colors.WARNING)
        title_rect = title_surf.get_rect(center=(540, 250))
        screen.blit(title_surf, title_rect)
        
        # List items
        start_y = 500
        line_h = 80
        
        if not self.drink_counts:
            empty_surf = self.fonts.body.render("Ühtegi toodet ei leitud", True, Colors.TEXT_SECONDARY)
            empty_rect = empty_surf.get_rect(center=(540, start_y))
            screen.blit(empty_surf, empty_rect)
        else:
            for i, (drink_name, count) in enumerate(self.drink_counts.items()):
                y = start_y + i * line_h
                # Limit drawing to screen height
                if y > 1400:
                    more_surf = self.fonts.body.render("... rohkem tooteid", True, Colors.TEXT_SECONDARY)
                    screen.blit(more_surf, (140, y))
                    break
                
                # Format: "Drink Name 6X" (show count with X)
                if count > 1:
                    display_text = f"{drink_name} {count}X"
                else:
                    display_text = drink_name
                
                drink_surf = self.fonts.body.render(display_text, True, Colors.TEXT_PRIMARY)
                screen.blit(drink_surf, (140, y))
        
        # Draw buttons
        for btn in self.buttons:
            btn.draw(screen)
            
        debug_surf = self.fonts.tiny.render(self.__class__.__name__, True, Colors.WARNING)
        screen.blit(debug_surf, debug_surf.get_rect(topright=(1070, 10)))
    
    def handle_input(self, event):
        # Let buttons process hover/clicks
        for btn in self.buttons:
            result = btn.check_input(event)
            if result:
                return result
        return None

class KASUTAJA_REGISTREERITUD:
    def __init__(self, nimi, fonts):
        """
        Kinitiab et (nimi) on edukalt registreeritud. ja retruneb True kui kasutaja vajutab jätka nuppu
        """
        self.nimi = nimi
        self.fonts = fonts
        
        # Create continue button
        btn_continue = Button(140, 1700, 800, 150, "Jätka", fonts.title, Colors.SUCCESS, True)
        self.buttons = [btn_continue]
    
    def draw(self, screen):
        screen.fill(Colors.BACKGROUND)
        
        # Success message - split into two lines
        line1 = f"Kasutaja {self.nimi}"
        line2 = f" on edukalt registreeritud."
        
        line1_surf = self.fonts.huge.render(line1, True, Colors.SUCCESS)
        line1_rect = line1_surf.get_rect(center=(540, 700))
        screen.blit(line1_surf, line1_rect)
        
        line2_surf = self.fonts.header.render(line2, True, Colors.SUCCESS)
        line2_rect = line2_surf.get_rect(center=(540, 900))
        screen.blit(line2_surf, line2_rect)
        
        # Draw continue button
        for btn in self.buttons:
            btn.draw(screen)
            
        debug_surf = self.fonts.tiny.render(self.__class__.__name__, True, Colors.WARNING)
        screen.blit(debug_surf, debug_surf.get_rect(topright=(1070, 10)))
    
    def handle_input(self, event):
        for btn in self.buttons:
            result = btn.check_input(event)
            if result:
                return True  # Return True when button pressed
        return None

class DEFAULT_SCREEN:
    def __init__(self, fonts):
        self.fonts = fonts
        self.state = "default" # default, viipa, options
        
        # Buttons adjusted for 1080x1920 vertical screen
        # Main action button - large and centered
        self.btn_drink = Button(140, 800, 800, 200, "Login sisse, tahan juua", fonts.title, Colors.SUCCESS, "START_LOGIN")
        
        # Settings button at bottom
        self.btn_kontohaldus = Button(140, 1750, 800, 120, "KONTOHALDUS", fonts.body, Colors.PRIMARY, "GOTO_OPTIONS")
        
        # Options menu buttons - stacked vertically
        self.btn_login_settings = Button(140, 700, 800, 150, "Logi sisse seadetesse", fonts.body, Colors.PRIMARY, "LOGIN_SEADED")
        self.btn_new_card = Button(140, 900, 800, 150, "Kaotasin kaardi", fonts.body, Colors.WARNING, "KAOTATUD_KAART")
        self.btn_new_account = Button(140, 1100, 800, 150, "Loo uus kasutaja", fonts.body, Colors.INFO, "UUS_KONTO")
        
        self.btn_back = Button(290, 1700, 500, 120, "Tagasi", fonts.body, Colors.LIGHT_GREY, "BACK", text_color=Colors.TEXT_PRIMARY)

    def draw(self, screen):
        screen.fill(Colors.BACKGROUND)
        rect = screen.get_rect()
        
        if self.state == "default":
            # Welcome header at top
            line1 = self.fonts.huge.render("Tere tulemast!", True, Colors.TEXT_PRIMARY)
            line2 = self.fonts.header.render("Sinine Kapp", True, Colors.PRIMARY)
            
            screen.blit(line1, line1.get_rect(center=(rect.centerx, 300)))
            screen.blit(line2, line2.get_rect(center=(rect.centerx, 450)))
            
            self.btn_drink.draw(screen)
            self.btn_kontohaldus.draw(screen)
            
            # Footer info
            info_text = self.fonts.small.render("Puuduta ekraani alustamiseks", True, Colors.TEXT_SECONDARY)
            screen.blit(info_text, info_text.get_rect(center=(rect.centerx, 1600)))
            
        elif self.state == "viipa":
            # Large clear instruction
            line = self.fonts.header.render("Viipa kaarti", True, Colors.TEXT_PRIMARY)
            line2 = self.fonts.title.render("logimiseks", True, Colors.TEXT_PRIMARY)
            screen.blit(line, line.get_rect(center=(rect.centerx, 800)))
            screen.blit(line2, line2.get_rect(center=(rect.centerx, 920)))
            
            # Visual indicator - large card icon area
            card_rect = pygame.Rect(340, 1000, 400, 300)
            pygame.draw.rect(screen, Colors.CARD_BG, card_rect, border_radius=30)
            pygame.draw.rect(screen, Colors.PRIMARY, card_rect, 5, border_radius=30)
            
            icon_text = self.fonts.huge.render("💳", True, Colors.PRIMARY)
            screen.blit(icon_text, icon_text.get_rect(center=card_rect.center))
            
            self.btn_back.draw(screen)
            
        elif self.state == "options":
            # Options menu header
            line = self.fonts.huge.render("Kontohaldus", True, Colors.TEXT_PRIMARY)
            screen.blit(line, line.get_rect(center=(rect.centerx, 300)))
            
            line2 = self.fonts.body.render("Vali toiming", True, Colors.TEXT_SECONDARY)
            screen.blit(line2, line2.get_rect(center=(rect.centerx, 500)))
            
            self.btn_login_settings.draw(screen)
            self.btn_new_card.draw(screen)
            self.btn_new_account.draw(screen)
            self.btn_back.draw(screen)
            
        # Debug info in corner
        debug_surf = self.fonts.tiny.render(self.__class__.__name__, True, Colors.TEXT_SECONDARY)
        screen.blit(debug_surf, debug_surf.get_rect(topright=(1070, 10)))

    def handle_input(self, event):
        if self.state == "default":
            res = self.btn_drink.check_input(event)
            if res == "START_LOGIN":
                self.state = "viipa"
                logging.info("SAADAN LOGI_SISSE KÄSU")
                return "LOGI_SISSE"

                
            res = self.btn_kontohaldus.check_input(event)
            if res == "GOTO_OPTIONS":
                self.state = "options"
                return None
                


        elif self.state == "viipa":
            res = self.btn_back.check_input(event)
            if res == "BACK":
                self.state = "default"
                return None
        
        elif self.state == "options":
            res = self.btn_login_settings.check_input(event)
            if res == "LOGIN_SEADED":
                self.state = "viipa"
                return "LOGIN_SEADED"
            
            res = self.btn_new_card.check_input(event)
            if res == "KAOTATUD_KAART":
                return "KAOTATUD_KAART"
            
            res = self.btn_new_account.check_input(event)
            if res == "UUS_KONTO":
                return "UUS_KONTO"
            
            res = self.btn_new_card.check_input(event)
            if res == "UUS_KAART":
                return "UUS_KAART"
                
            res = self.btn_back.check_input(event)
            if res == "BACK":
                self.state = "default"
                return None
                
        return None

class UKSE_AVAMINE_VÕTMINE:
    def __init__(self, data, fonts):
        self.data = data
        self.fonts = fonts
        logging.info(f"UKSEAVAJA JOOKIDE VÕTMINE")
        self.line1_text = "Uks avaneb!"
        self.line2_text = "Võta oma joogid ja sulge uks"

    def draw(self, screen):
        
        screen.fill(Colors.BACKGROUND)
        
        line1 = self.fonts.huge.render(self.line1_text, True, Colors.SUCCESS)
        line2 = self.fonts.header.render(self.line2_text, True, Colors.TEXT_PRIMARY)
        
        screen.blit(line1, line1.get_rect(center=(540, 800)))
        screen.blit(line2, line2.get_rect(center=(540, 1000)))
        
        debug_surf = self.fonts.tiny.render(self.__class__.__name__, True, Colors.WARNING)
        screen.blit(debug_surf, debug_surf.get_rect(topright=(1070, 10)))
    
    def handle_input(self, event):
        # No interaction on door screen
        return None

#kuvab ükskõik mida samal ajal kui uks on avatud
class REKLAAM:
    def __init__(self, payload_data, fonts):
        self.fonts = fonts
        
    def draw(self, screen):
        screen.fill(Colors.BACKGROUND)
        line1 = self.fonts.huge.render("UKS AVATUD", True, Colors.WARNING)
        line2 = self.fonts.header.render("TEGUTSE", True, Colors.TEXT_PRIMARY)
        
        screen.blit(line1, line1.get_rect(center=(540, 800)))
        screen.blit(line2, line2.get_rect(center=(540, 1000)))
        
        debug_surf = self.fonts.tiny.render(self.__class__.__name__, True, Colors.WARNING)
        screen.blit(debug_surf, debug_surf.get_rect(topright=(1070, 10)))
        
    def handle_input(self, event):
        # No interaction on reklaam screen
        return None
  
class REGISTREERIMINE:
    """
    Two-stage registration:
    1. Ask "Do you want to register?" with Yes/No buttons
    2. If Yes, show PIN pad to enter registration code
    """
    
    def __init__(self, fonts):
        """
        Args:
            fonts: FontManager object with .header, .body, .small
        """
        self.fonts = fonts
        self.stage = "question"  # "question" or "pinpad"
        self.pincode = ""
        self.gif_frames = []
        self.easter_egg_start = 0
        
        # Create Yes/No buttons for first stage
        self.buttons = []
        btn_yes = Button(140, 1100, 380, 200, "JAH", fonts.huge, Colors.SUCCESS, "yes")
        btn_no = Button(560, 1100, 380, 200, "EI", fonts.huge, Colors.DANGER, "no")
        self.buttons.append(btn_yes)
        self.buttons.append(btn_no)
        
        # Create PIN pad buttons (0-9, Clear, Enter)
        self.pinpad_buttons = []
        self._create_pinpad()
    
    def _create_pinpad(self):
        """Create a 3x4 keypad layout with 0-9, Clear, Enter buttons"""
        # PIN pad layout:
        # 1 2 3
        # 4 5 6
        # 7 8 9
        # C 0 E (Clear, 0, Enter)
        
        self.pinpad_buttons = []
        start_x = 240
        start_y = 700
        btn_width = 180
        btn_height = 180
        spacing = 20
        
        # Buttons 1-9
        labels = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        for i, label in enumerate(labels):
            row = i // 3
            col = i % 3
            x = start_x + col * (btn_width + spacing)
            y = start_y + row * (btn_height + spacing)
            btn = Button(x, y, btn_width, btn_height, label, self.fonts.header, Colors.PRIMARY, label)
            self.pinpad_buttons.append(btn)
        
        # Bottom row: Clear, 0, Enter
        row = 3
        
        # Clear button
        btn_clear = Button(start_x, start_y + row * (btn_height + spacing), btn_width, btn_height, 
                          "C", self.fonts.header, Colors.DANGER, "clear")
        self.pinpad_buttons.append(btn_clear)
        
        # 0 button
        btn_zero = Button(start_x + (btn_width + spacing), start_y + row * (btn_height + spacing), 
                         btn_width, btn_height, "0", self.fonts.header, Colors.PRIMARY, "0")
        self.pinpad_buttons.append(btn_zero)
        
        # Enter button
        btn_enter = Button(start_x + 2 * (btn_width + spacing), start_y + row * (btn_height + spacing), 
                          btn_width, btn_height, "E", self.fonts.header, Colors.SUCCESS, "enter")
        self.pinpad_buttons.append(btn_enter)
    
    def _load_gif(self):
        if not self.gif_frames:
            try:
                if os.path.exists("67GIF.gif"):
                    pil_image = Image.open("67GIF.gif")
                    for frame in ImageSequence.Iterator(pil_image):
                        frame = frame.convert('RGBA')
                        mode = frame.mode
                        size = frame.size
                        data = frame.tobytes()
                        image = pygame.image.fromstring(data, size, mode)
                        self.gif_frames.append(image)
            except Exception as e:
                logging.error(f"Failed to load easter egg gif: {e}")

    def _draw_easter_egg(self, screen):
        if not self.gif_frames:
            self.stage = "pinpad"
            self.pincode = ""
            return

        now = time.time()
        if now - self.easter_egg_start > 3:
            self.stage = "pinpad"
            self.pincode = ""
            return

        idx = int((now - self.easter_egg_start) * 10) % len(self.gif_frames)
        frame = self.gif_frames[idx]
        rect = frame.get_rect(center=(540, 960))
        screen.fill((0, 0, 0))
        screen.blit(frame, rect)

    def draw(self, screen):
        screen.fill(Colors.BACKGROUND)
        
        if self.stage == "question":
            self._draw_question_stage(screen)
        elif self.stage == "pinpad":
            self._draw_pinpad_stage(screen)
        elif self.stage == "easter_egg":
            self._draw_easter_egg(screen)
            
        debug_surf = self.fonts.tiny.render(self.__class__.__name__, True, Colors.WARNING)
        screen.blit(debug_surf, debug_surf.get_rect(topright=(1070, 10)))
    
    def _draw_question_stage(self, screen):
        """Draw the Yes/No question screen"""
        # Title
        title_surf = self.fonts.huge.render("Kiipkaardile ei vasta kasutajat!", True, Colors.TEXT_PRIMARY)
        title_rect = title_surf.get_rect(center=(540, 400))
        screen.blit(title_surf, title_rect)
        
        # Additional text line
        subtitle_surf = self.fonts.header.render("Kas soovid registreerida?", True, Colors.TEXT_SECONDARY)
        subtitle_rect = subtitle_surf.get_rect(center=(540, 700))
        screen.blit(subtitle_surf, subtitle_rect)
        
        # Draw buttons
        for btn in self.buttons:
            btn.draw(screen)
    
    def _draw_pinpad_stage(self, screen):
        """Draw the PIN pad entry screen"""
        # Title
        title_surf = self.fonts.huge.render("Sisesta PIN-kood", True, Colors.TEXT_PRIMARY)
        title_rect = title_surf.get_rect(center=(540, 300))
        screen.blit(title_surf, title_rect)
        
        # Display entered PIN with asterisks
        pin_display = self.pincode if self.pincode else "_ _ _ _"
        pin_surf = self.fonts.header.render(pin_display, True, Colors.TEXT_PRIMARY)
        pin_rect = pin_surf.get_rect(center=(540, 500))
        screen.blit(pin_surf, pin_rect)
        
        # Draw PIN pad buttons
        for btn in self.pinpad_buttons:
            btn.draw(screen)
    
    def handle_input(self, event):
        """
        Handle user input. Returns:
        - None if still waiting
        - (True, pincode) if user confirms PIN
        - (False, None) if user cancels
        """
        if self.stage == "question":
            for btn in self.buttons:
                res = btn.check_input(event)
                if res == "yes":
                    self.stage = "pinpad"
                    self.pincode = ""
                    return None
                elif res == "no":
                    return (False, None)
        
        elif self.stage == "pinpad":
            for btn in self.pinpad_buttons:
                res = btn.check_input(event)
                
                if res == "clear":
                    self.pincode = self.pincode[:-1] if self.pincode else ""
                    return None
                
                elif res == "enter":
                    if self.pincode == "67":
                        self._load_gif()
                        if self.gif_frames:
                            self.stage = "easter_egg"
                            self.easter_egg_start = time.time()
                            return None

                    if self.pincode:
                        return (True, self.pincode)
                    return None
                
                elif res and res.isdigit():
                    self.pincode += res
                    return None
        
        return None

class MESSAGE:
    def __init__(self, payload, fonts):
        self.fonts = fonts
        
        if isinstance(payload, tuple):
            self.text = str(payload[0]) if payload[0] else ""
            show_button = payload[1]
        else:
            self.text = str(payload) if payload else ""
            show_button = True
        
        self.buttons = []
        if show_button:
            # Button returns True (boolean) which will be put in reply_queue
            btn = Button(140, 1700, 800, 150, "Jätka", fonts.title, Colors.SUCCESS, True)
            self.buttons.append(btn)
        
        # Wrap text to fit screen width (800px safe area)
        self.lines = self._wrap_text(self.text, self.fonts.body, 800)

    def _wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            w, h = font.size(test_line)
            if w < max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        return lines

    def draw(self, screen):
        screen.fill(Colors.BACKGROUND)
        
        # Draw text lines centered
        start_y = 600
        line_h = 80
        for i, line in enumerate(self.lines):
            surf = self.fonts.body.render(line, True, Colors.TEXT_PRIMARY)
            rect = surf.get_rect(center=(540, start_y + i * line_h))
            screen.blit(surf, rect)
        
        for btn in self.buttons:
            btn.draw(screen)
            
        debug_surf = self.fonts.tiny.render(self.__class__.__name__, True, Colors.WARNING)
        screen.blit(debug_surf, debug_surf.get_rect(topright=(1070, 10)))

    def handle_input(self, event):
        for btn in self.buttons:
            res = btn.check_input(event)
            if res: return res
        return None

class TAGASTATUD_JOOGID:
    def __init__(self, payload_data, fonts):
        self.fonts = fonts
        # payload_data is expected to be a dict: {"Drink Name": count, ...}
        self.items = payload_data if isinstance(payload_data, dict) else {}

        # Create a continue button
        self.buttons = []
        btn = Button(140, 1700, 800, 150, "Jätka", fonts.title, Colors.SUCCESS, True)
        self.buttons.append(btn)

    def draw(self, screen):
        screen.fill(Colors.BACKGROUND)

        # Title
        title_surf = self.fonts.huge.render("Tagastasid:", True, Colors.TEXT_PRIMARY)
        title_rect = title_surf.get_rect(center=(540, 250))
        screen.blit(title_surf, title_rect)

        # List items
        start_y = 500
        line_h = 80
        if not self.items:
            empty_surf = self.fonts.body.render("Ei tuvastatud tagastusi", True, Colors.TEXT_SECONDARY)
            empty_rect = empty_surf.get_rect(center=(540, start_y))
            screen.blit(empty_surf, empty_rect)
        else:
            x_name = 140
            x_count = 880
            for i, (name, count) in enumerate(self.items.items()):
                y = start_y + i * line_h
                # Limit drawing to screen height
                if y > 1400:
                    more_surf = self.fonts.body.render("... rohkem tooteid", True, Colors.TEXT_SECONDARY)
                    screen.blit(more_surf, (140, y))
                    break
                name_surf = self.fonts.body.render(str(name), True, Colors.TEXT_PRIMARY)
                count_surf = self.fonts.body.render(f"{count}x", True, Colors.TEXT_PRIMARY)
                screen.blit(name_surf, (x_name, y))
                screen.blit(count_surf, (x_count, y))

        # Draw buttons
        for btn in self.buttons:
            btn.draw(screen)
            
        debug_surf = self.fonts.tiny.render(self.__class__.__name__, True, Colors.WARNING)
        screen.blit(debug_surf, debug_surf.get_rect(topright=(1070, 10)))

    def handle_input(self, event):
        # Let buttons process hover/clicks
        for btn in self.buttons:
            result = btn.check_input(event)
            if result:
                return result
        return None

class KONTOHALDUS:
    def __init__(self, payload, fonts):
        self.fonts = fonts
        # payload structure: (nimi, unreturned_drinks_list)
        self.nimi = payload[0] if payload else "Tundmatu"
        self.unreturned_drinks = payload[1] if payload and len(payload) > 1 else []
        
        self.state = "main" # main, balance, dates
        
        # --- Buttons for MAIN state ---
        self.btn_new_card = Button(140, 900, 800, 200, "Vaheta kiipkaarti", fonts.title, Colors.PRIMARY, "UUS_KAART")
        self.btn_balance = Button(140, 1150, 800, 200, "Vaata konto seisu", fonts.title, Colors.SUCCESS, "SHOW_BALANCE")
        self.btn_main_back = Button(290, 1700, 500, 120, "Tagasi", fonts.body, Colors.DANGER, True)
        
        # --- Buttons for BALANCE state ---
        self.btn_dates = Button(590, 1700, 350, 120, "Kuupäevad", fonts.body, Colors.PRIMARY, "SHOW_DATES")
        self.btn_balance_back = Button(140, 1700, 350, 120, "Tagasi", fonts.body, Colors.TEXT_SECONDARY, "BACK_TO_MAIN")
        
        # --- Buttons for DATES state ---
        self.btn_dates_back = Button(290, 1700, 500, 120, "Tagasi", fonts.body, Colors.TEXT_SECONDARY, "BACK_TO_BALANCE")

    def draw(self, screen):
        screen.fill(Colors.BACKGROUND)
        
        if self.state == "main":
            # Title
            title = self.fonts.huge.render(f"Konto: {self.nimi}", True, Colors.TEXT_PRIMARY)
            screen.blit(title, title.get_rect(center=(540, 300)))
            
            self.btn_new_card.draw(screen)
            self.btn_balance.draw(screen)
            self.btn_main_back.draw(screen)
            
        elif self.state == "balance":
            title = self.fonts.huge.render("Sinu jookide seis", True, Colors.TEXT_PRIMARY)
            screen.blit(title, title.get_rect(center=(540, 250)))
            
            # Group drinks
            counts = {}
            for item in self.unreturned_drinks:
                name = item[0]
                counts[name] = counts.get(name, 0) + 1
            
            start_y = 500
            if not counts:
                msg = self.fonts.header.render("Võlgnevusi pole!", True, Colors.SUCCESS)
                screen.blit(msg, msg.get_rect(center=(540, start_y)))
            else:
                for i, (name, count) in enumerate(counts.items()):
                    y = start_y + i * 80
                    if y > 1400: break
                    row_text = f"{name}: {count} tk"
                    surf = self.fonts.body.render(row_text, True, Colors.TEXT_PRIMARY)
                    screen.blit(surf, (140, y))
            
            self.btn_dates.draw(screen)
            self.btn_balance_back.draw(screen)
            
        elif self.state == "dates":
            title = self.fonts.huge.render("Võtmise ajad", True, Colors.TEXT_PRIMARY)
            screen.blit(title, title.get_rect(center=(540, 250)))
            
            start_y = 500
            if not self.unreturned_drinks:
                msg = self.fonts.header.render("Võlgnevusi pole!", True, Colors.SUCCESS)
                screen.blit(msg, msg.get_rect(center=(540, start_y)))
            else:
                for i, item in enumerate(self.unreturned_drinks):
                    # item: (name, barcode, date)
                    name = item[0]
                    date_str = str(item[2])
                    y = start_y + i * 60
                    if y > 1400: break
                    
                    row_text = f"{name} - {date_str}"
                    surf = self.fonts.small.render(row_text, True, Colors.TEXT_PRIMARY)
                    screen.blit(surf, (140, y))
            
            self.btn_dates_back.draw(screen)
            
        debug_surf = self.fonts.tiny.render(self.__class__.__name__, True, Colors.WARNING)
        screen.blit(debug_surf, debug_surf.get_rect(topright=(1070, 10)))

    def handle_input(self, event):
        if self.state == "main":
            res = self.btn_new_card.check_input(event)
            if res == "UUS_KAART": return "UUS_KAART"
            
            res = self.btn_balance.check_input(event)
            if res == "SHOW_BALANCE":
                self.state = "balance"
                return None
                
            res = self.btn_main_back.check_input(event)
            if res is True: return True
            
        elif self.state == "balance":
            res = self.btn_dates.check_input(event)
            if res == "SHOW_DATES":
                self.state = "dates"
                return None
            
            res = self.btn_balance_back.check_input(event)
            if res == "BACK_TO_MAIN":
                self.state = "main"
                return None
                
        elif self.state == "dates":
            res = self.btn_dates_back.check_input(event)
            if res == "BACK_TO_BALANCE":
                self.state = "balance"
                return None
        
        return None

class UUS_KAART:
    def __init__(self, payload, fonts):
        self.fonts = fonts
        
    def draw(self, screen):
        screen.fill(Colors.BACKGROUND)
        
        line1 = "Viipa oma uut kaarti"
        line2 = "registreerimiseks."
        
        surf1 = self.fonts.huge.render(line1, True, Colors.TEXT_PRIMARY)
        rect1 = surf1.get_rect(center=(540, 800))
        screen.blit(surf1, rect1)
        
        surf2 = self.fonts.header.render(line2, True, Colors.TEXT_SECONDARY)
        rect2 = surf2.get_rect(center=(540, 1000))
        screen.blit(surf2, rect2)
        
        debug_surf = self.fonts.tiny.render(self.__class__.__name__, True, Colors.WARNING)
        screen.blit(debug_surf, debug_surf.get_rect(topright=(1070, 10)))

    def handle_input(self, event):
        return None

class KAOTATUD_KAART:
    def __init__(self, payload, fonts):
        self.fonts = fonts
        self.pincode = ""
        self.pinpad_buttons = []
        self._create_pinpad()
        
        self.btn_cancel = Button(290, 1700, 500, 120, "Tühista", fonts.body, Colors.DANGER, "CANCEL")
        
        self.gif_frames = []
        self.easter_egg_start = 0
        self.show_easter_egg = False

    def _load_gif(self):
        if not self.gif_frames:
            try:
                if os.path.exists("67GIF.gif"):
                    pil_image = Image.open("67GIF.gif")
                    for frame in ImageSequence.Iterator(pil_image):
                        frame = frame.convert('RGBA')
                        mode = frame.mode
                        size = frame.size
                        data = frame.tobytes()
                        image = pygame.image.fromstring(data, size, mode)
                        self.gif_frames.append(image)
            except Exception as e:
                logging.error(f"Failed to load easter egg gif: {e}")

    def _draw_easter_egg(self, screen):
        if not self.gif_frames:
            self.show_easter_egg = False
            self.pincode = ""
            return

        now = time.time()
        if now - self.easter_egg_start > 3:
            self.show_easter_egg = False
            self.pincode = ""
            return

        idx = int((now - self.easter_egg_start) * 10) % len(self.gif_frames)
        frame = self.gif_frames[idx]
        rect = frame.get_rect(center=(540, 960))
        screen.fill((0, 0, 0))
        screen.blit(frame, rect)

    def _create_pinpad(self):
        self.pinpad_buttons = []
        start_x = 240
        start_y = 700
        btn_width = 180
        btn_height = 180
        spacing = 20
        
        # Buttons 1-9
        labels = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        for i, label in enumerate(labels):
            row = i // 3
            col = i % 3
            x = start_x + col * (btn_width + spacing)
            y = start_y + row * (btn_height + spacing)
            btn = Button(x, y, btn_width, btn_height, label, self.fonts.header, Colors.PRIMARY, label)
            self.pinpad_buttons.append(btn)
        
        # Bottom row: Clear, 0, Enter
        row = 3
        
        btn_clear = Button(start_x, start_y + row * (btn_height + spacing), btn_width, btn_height, 
                          "C", self.fonts.header, Colors.DANGER, "clear")
        self.pinpad_buttons.append(btn_clear)
        
        btn_zero = Button(start_x + (btn_width + spacing), start_y + row * (btn_height + spacing), 
                         btn_width, btn_height, "0", self.fonts.header, Colors.PRIMARY, "0")
        self.pinpad_buttons.append(btn_zero)
        
        btn_enter = Button(start_x + 2 * (btn_width + spacing), start_y + row * (btn_height + spacing), 
                          btn_width, btn_height, "E", self.fonts.header, Colors.SUCCESS, "enter")
        self.pinpad_buttons.append(btn_enter)

    def draw(self, screen):
        if self.show_easter_egg:
            self._draw_easter_egg(screen)
            return

        screen.fill(Colors.BACKGROUND)
        
        line1 = "Sisesta pinnkood uue kaardi"
        line2 = "registreerimiseks"
        
        surf1 = self.fonts.huge.render(line1, True, Colors.TEXT_PRIMARY)
        rect1 = surf1.get_rect(center=(540, 250))
        screen.blit(surf1, rect1)
        
        surf2 = self.fonts.header.render(line2, True, Colors.TEXT_SECONDARY)
        rect2 = surf2.get_rect(center=(540, 400))
        screen.blit(surf2, rect2)
        
        pin_display = self.pincode if self.pincode else "_ _ _ _"
        pin_surf = self.fonts.header.render(pin_display, True, Colors.TEXT_PRIMARY)
        pin_rect = pin_surf.get_rect(center=(540, 550))
        screen.blit(pin_surf, pin_rect)
        
        for btn in self.pinpad_buttons:
            btn.draw(screen)
            
        self.btn_cancel.draw(screen)
        
        debug_surf = self.fonts.tiny.render(self.__class__.__name__, True, Colors.WARNING)
        screen.blit(debug_surf, debug_surf.get_rect(topright=(1070, 10)))

    def handle_input(self, event):
        res = self.btn_cancel.check_input(event)
        if res == "CANCEL":
            return "CANCEL"

        for btn in self.pinpad_buttons:
            res = btn.check_input(event)
            
            if res == "clear":
                self.pincode = self.pincode[:-1] if self.pincode else ""
                return None
            
            elif res == "enter":
                if self.pincode == "67":
                    self._load_gif()
                    if self.gif_frames:
                        self.show_easter_egg = True
                        self.easter_egg_start = time.time()
                        return None

                if self.pincode:
                    return self.pincode
                return None
            
            elif res and res.isdigit():
                self.pincode += res
                return None
        
        return None

class REGISTREERI_PINNKOODI_ALUSEL: #Regamine kui kasutaja sisetsas pini mida pole regatud
    def __init__(self, payload, fonts):
        self.fonts = fonts
        self.buttons = []
        
        # Buttons return boolean values directly
        btn_yes = Button(140, 1100, 380, 200, "JAH", fonts.huge, Colors.SUCCESS, True)
        btn_no = Button(560, 1100, 380, 200, "EI", fonts.huge, Colors.DANGER, False)
        
        self.buttons.append(btn_yes)
        self.buttons.append(btn_no)

    def draw(self, screen):
        screen.fill(Colors.BACKGROUND)
        
        line1 = "Pinnkoodile vastavat kasutajat"
        line2 = "pole registreeritud."
        line3 = "Kas soovid registreerida?"
        
        surf1 = self.fonts.huge.render(line1, True, Colors.TEXT_PRIMARY)
        rect1 = surf1.get_rect(center=(540, 400))
        screen.blit(surf1, rect1)
        
        surf2 = self.fonts.huge.render(line2, True, Colors.TEXT_PRIMARY)
        rect2 = surf2.get_rect(center=(540, 550))
        screen.blit(surf2, rect2)
        
        surf3 = self.fonts.header.render(line3, True, Colors.TEXT_SECONDARY)
        rect3 = surf3.get_rect(center=(540, 800))
        screen.blit(surf3, rect3)
        
        for btn in self.buttons:
            btn.draw(screen)
            
        debug_surf = self.fonts.tiny.render(self.__class__.__name__, True, Colors.WARNING)
        screen.blit(debug_surf, debug_surf.get_rect(topright=(1070, 10)))

    def handle_input(self, event):
        for btn in self.buttons:
            res = btn.check_input(event)
            if res is not None:
                return res
        return None

class UUE_KONTO_REGAMINE_PINNKOODIGA:
    def __init__(self, payload, fonts):
        self.fonts = fonts
        self.pincode = ""
        self.pinpad_buttons = []
        self._create_pinpad()
        
        self.btn_cancel = Button(290, 1700, 500, 120, "Tühista", fonts.body, Colors.DANGER, "CANCEL")
        
        self.gif_frames = []
        self.easter_egg_start = 0
        self.show_easter_egg = False

    def _load_gif(self):
        if not self.gif_frames:
            try:
                if os.path.exists("67GIF.gif"):
                    pil_image = Image.open("67GIF.gif")
                    for frame in ImageSequence.Iterator(pil_image):
                        frame = frame.convert('RGBA')
                        mode = frame.mode
                        size = frame.size
                        data = frame.tobytes()
                        image = pygame.image.fromstring(data, size, mode)
                        self.gif_frames.append(image)
            except Exception as e:
                logging.error(f"Failed to load easter egg gif: {e}")

    def _draw_easter_egg(self, screen):
        if not self.gif_frames:
            self.show_easter_egg = False
            self.pincode = ""
            return

        now = time.time()
        if now - self.easter_egg_start > 3:
            self.show_easter_egg = False
            self.pincode = ""
            return

        idx = int((now - self.easter_egg_start) * 10) % len(self.gif_frames)
        frame = self.gif_frames[idx]
        rect = frame.get_rect(center=(540, 960))
        screen.fill((0, 0, 0))
        screen.blit(frame, rect)

    def _create_pinpad(self):
        self.pinpad_buttons = []
        start_x = 240
        start_y = 700
        btn_width = 180
        btn_height = 180
        spacing = 20
        
        # Buttons 1-9
        labels = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        for i, label in enumerate(labels):
            row = i // 3
            col = i % 3
            x = start_x + col * (btn_width + spacing)
            y = start_y + row * (btn_height + spacing)
            btn = Button(x, y, btn_width, btn_height, label, self.fonts.header, Colors.PRIMARY, label)
            self.pinpad_buttons.append(btn)
        
        # Bottom row: Clear, 0, Enter
        row = 3
        
        btn_clear = Button(start_x, start_y + row * (btn_height + spacing), btn_width, btn_height, 
                          "C", self.fonts.header, Colors.DANGER, "clear")
        self.pinpad_buttons.append(btn_clear)
        
        btn_zero = Button(start_x + (btn_width + spacing), start_y + row * (btn_height + spacing), 
                         btn_width, btn_height, "0", self.fonts.header, Colors.PRIMARY, "0")
        self.pinpad_buttons.append(btn_zero)
        
        btn_enter = Button(start_x + 2 * (btn_width + spacing), start_y + row * (btn_height + spacing), 
                          btn_width, btn_height, "E", self.fonts.header, Colors.SUCCESS, "enter")
        self.pinpad_buttons.append(btn_enter)

    def draw(self, screen):
        if self.show_easter_egg:
            self._draw_easter_egg(screen)
            return

        screen.fill(Colors.BACKGROUND)
        
        line1 = "Kasutaja registreerimiseks"
        line2 = "sisesta pinnkood!"
        
        surf1 = self.fonts.huge.render(line1, True, Colors.TEXT_PRIMARY)
        rect1 = surf1.get_rect(center=(540, 250))
        screen.blit(surf1, rect1)
        
        surf2 = self.fonts.header.render(line2, True, Colors.TEXT_SECONDARY)
        rect2 = surf2.get_rect(center=(540, 400))
        screen.blit(surf2, rect2)
        
        pin_display = self.pincode if self.pincode else "_ _ _ _"
        pin_surf = self.fonts.header.render(pin_display, True, Colors.TEXT_PRIMARY)
        pin_rect = pin_surf.get_rect(center=(540, 550))
        screen.blit(pin_surf, pin_rect)
        
        for btn in self.pinpad_buttons:
            btn.draw(screen)
            
        self.btn_cancel.draw(screen)
        
        debug_surf = self.fonts.tiny.render(self.__class__.__name__, True, Colors.WARNING)
        screen.blit(debug_surf, debug_surf.get_rect(topright=(1070, 10)))

    def handle_input(self, event):
        res = self.btn_cancel.check_input(event)
        if res == "CANCEL":
            return "CANCEL"

        for btn in self.pinpad_buttons:
            res = btn.check_input(event)
            
            if res == "clear":
                self.pincode = self.pincode[:-1] if self.pincode else ""
                return None
            
            elif res == "enter":
                if self.pincode == "67":
                    self._load_gif()
                    if self.gif_frames:
                        self.show_easter_egg = True
                        self.easter_egg_start = time.time()
                        return None

                if self.pincode:
                    return self.pincode
                return None
            
            elif res and res.isdigit():
                self.pincode += res
                return None
        
        return None

class LIVE_CART:
    def __init__(self, payload_data, fonts):
        self.fonts = fonts
        # payload_data is expected to be a dict: {"Drink Name": count, ...}
        self.items = payload_data if isinstance(payload_data, dict) else {}
        self.buttons = []

    def draw(self, screen):
        screen.fill(Colors.BACKGROUND)
        
        # Title
        title_surf = self.fonts.huge.render("Hetkel skaneeritud:", True, Colors.TEXT_PRIMARY)
        title_rect = title_surf.get_rect(center=(540, 250))
        screen.blit(title_surf, title_rect)
        
        # List items
        start_y = 500
        line_h = 80
        if not self.items:
            empty_surf = self.fonts.header.render("Skaneeri tooteid...", True, Colors.TEXT_SECONDARY)
            empty_rect = empty_surf.get_rect(center=(540, start_y))
            screen.blit(empty_surf, empty_rect)
        else:
            x_name = 140
            x_count = 880
            for i, (name, count) in enumerate(self.items.items()):
                y = start_y + i * line_h
                if y > 1500: break
                name_surf = self.fonts.body.render(str(name), True, Colors.TEXT_PRIMARY)
                count_surf = self.fonts.body.render(f"x{count}", True, Colors.TEXT_PRIMARY)
                screen.blit(name_surf, (x_name, y))
                screen.blit(count_surf, (x_count, y))
                
        debug_surf = self.fonts.tiny.render(self.__class__.__name__, True, Colors.WARNING)
        screen.blit(debug_surf, debug_surf.get_rect(topright=(1070, 10)))

    def handle_input(self, event):
        return None

def run_touchscreen(command_q, reply_q):
    pygame.init()
    # Vertical screen for kiosk: 1080x1920 (portrait mode)
    screen = pygame.display.set_mode((1080, 1920))
    # Uncomment the line below for fullscreen on actual hardware:
    # screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Sinine Kapp - Smart Beverage Cabinet")
    
    # 1. INITIALIZE STYLE MANAGER
    # Laeb fondid 
    fonts = FontManager() 

    current_screen_object = None 
    current_screen_object = DEFAULT_SCREEN(fonts)
    running = True

    while running:
        try:
            command, payload = command_q.get_nowait()
            logging.info(f"Router received: {command} with payload: {payload}")

            if command == "DEFAULT":
                current_screen_object = None
                current_screen_object = DEFAULT_SCREEN(fonts)
                
            elif command == "VALIKUVAADE":
                current_screen_object = VALIKUVAADE(payload, fonts)

            elif command == "VÄLJASTATUD_JOOGID":
                current_screen_object = VÄLJASTATUD_JOOGID(payload, fonts)
            
            elif command == "REKLAAM":
                logging.info("REKLAAM command received - switching to REKLAAM screen")
                current_screen_object = REKLAAM(payload, fonts)

            elif command == "UKSE_AVAMINE_VÕTMINE":
                logging.info(f"UKSE_AVAMINE_VÕTMINE command received with payload: {payload}")
                current_screen_object = UKSE_AVAMINE_VÕTMINE(payload, fonts)

            elif command == "UKSE_AVAMINE_TAGASTAMINE":
                logging.info(f"UKSE_AVAMINE_TAGASTAMINE command received with payload: {payload}")
                current_screen_object = UKSE_AVAMINE_TAGASTAMINE(payload, fonts)

            elif command == "REGISTREERIMINE":
                logging.info("REGISTREERIMINE command received - switching to REGISTREERIMINE screen")
                current_screen_object = REGISTREERIMINE(fonts)

            elif command == "KASUTAJA_REGISTREERITUD":
                logging.info("KASUTAJA_REGISTREERITUD command received - switching to KASUTAJA_REGISTREERITUD screen")
                current_screen_object = KASUTAJA_REGISTREERITUD(payload, fonts)
            
            elif command == "TAGASTATUD_JOOGID":
                logging.info("TAGASTATUD_JOOGID command received - switching to TAGASTATUD_JOOGID screen")
                current_screen_object = TAGASTATUD_JOOGID(payload, fonts)
            
            elif command == "KONTOHALDUS":
                logging.info("KONTOHALDUS command received")
                current_screen_object = KONTOHALDUS(payload, fonts)

            elif command == "UUS_KAART":
                logging.info("UUS_KAART command received")
                current_screen_object = UUS_KAART(payload, fonts)

            elif command == "KAOTATUD_KAART":
                logging.info("KAOTATUD_KAART command received")
                current_screen_object = KAOTATUD_KAART(payload, fonts)

            elif command == "REGISTREERI_PINNKOODI_ALUSEL":
                logging.info("REGISTREERI_PINNKOODI_ALUSEL command received")
                current_screen_object = REGISTREERI_PINNKOODI_ALUSEL(payload, fonts)

            elif command == "UUE_KONTO_REGAMINE_PINNKOODIGA":
                logging.info("UUE_KONTO_REGAMINE_PINNKOODIGA command received")
                current_screen_object = UUE_KONTO_REGAMINE_PINNKOODIGA(payload, fonts)

            elif command == "MESSAGE":
                logging.info("MESSAGE command received - switching to MESSAGE screen")
                current_screen_object = MESSAGE(payload, fonts)
                
            elif command == "LIVE_CART":
                logging.info("LIVE_CART command received")
                current_screen_object = LIVE_CART(payload, fonts)

            elif command == "STOP":
                running = False

        except queue.Empty:
            pass 

        # ... Input Handling 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if current_screen_object:
                res = current_screen_object.handle_input(event)
                if res is not None: reply_q.put(res)

        # ... Drawing 
        if current_screen_object:
            current_screen_object.draw(screen)
        else:
            DEFAULT_SCREEN(screen, fonts)

        pygame.display.flip()

    pygame.quit()
