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
        
      
        btn_take = Button(100, 350, 350, 200, "VÕTA JOOK", fonts.body, Colors.GREEN, "1")
        self.buttons.append(btn_take)
        
        btn_return = Button(574, 350, 350, 200, "TOO TAGASI", fonts.body, Colors.BLUE, "2")
        self.buttons.append(btn_return)
        
        btn_cancel = Button(412, 650, 200, 60, "TÜHISTA", fonts.body, Colors.RED, False)
        self.buttons.append(btn_cancel)

    def draw(self, screen):
        screen.fill(Colors.DARK_BG)
        
        # Render greeting on two lines
        line1_surf = self.fonts.header.render(self.name_line, True, Colors.TEXT_PRIMARY)
        line1_rect = line1_surf.get_rect(center=(512, 130))
        screen.blit(line1_surf, line1_rect)
        
        line2_surf = self.fonts.body.render(self.question_line, True, Colors.TEXT_PRIMARY)
        line2_rect = line2_surf.get_rect(center=(512, 200))
        screen.blit(line2_surf, line2_rect)
        
        for btn in self.buttons:
            btn.draw(screen)
        
        debug_surf = self.fonts.small.render(self.__class__.__name__, True, Colors.YELLOW)
        screen.blit(debug_surf, debug_surf.get_rect(topright=(1014, 10)))

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

        # Create a confirm button (placeholder for future functionality)
        self.buttons = []
        btn = Button(412, 650, 200, 60, "Kinnita", fonts.body, Colors.GREEN, True)
        self.buttons.append(btn)

    def draw(self, screen):
        screen.fill(Colors.BACKGROUND)

        # Title
        title_surf = self.fonts.header.render("Väljastatud joogid", True, Colors.TEXT_PRIMARY)
        title_rect = title_surf.get_rect(center=(512, 50))
        screen.blit(title_surf, title_rect)

        # List items
        start_y = 150
        line_h = 38
        if not self.items:
            empty_surf = self.fonts.body.render("Ühtegi toodet ei leitud", True, Colors.GREY)
            screen.blit(empty_surf, (100, start_y))
        else:
            x_name = 100
            x_count = 850
            for i, (name, count) in enumerate(self.items.items()):
                y = start_y + i * line_h
                # Limit drawing to screen height
                if y > 600:
                    more_surf = self.fonts.small.render("... rohkem tooteid", True, Colors.GREY)
                    screen.blit(more_surf, (100, y))
                    break
                name_surf = self.fonts.body.render(str(name), True, Colors.TEXT_PRIMARY)
                count_surf = self.fonts.body.render(f"x{count}", True, Colors.TEXT_PRIMARY)
                screen.blit(name_surf, (x_name, y))
                screen.blit(count_surf, (x_count, y))

        # Draw buttons
        for btn in self.buttons:
            btn.draw(screen)
            
        debug_surf = self.fonts.small.render(self.__class__.__name__, True, Colors.YELLOW)
        screen.blit(debug_surf, debug_surf.get_rect(topright=(1014, 10)))

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
        btn = Button(412, 650, 200, 60, "Jätka", fonts.body, Colors.GREEN, True)
        self.buttons.append(btn)
    
    def draw(self, screen):
        screen.fill(Colors.BACKGROUND)
        
        # Title
        title_surf = self.fonts.header.render("Tagastamist ootavad joogid:", True, Colors.YELLOW)
        title_rect = title_surf.get_rect(center=(512, 50))
        screen.blit(title_surf, title_rect)
        
        # List items
        start_y = 150
        line_h = 50
        
        if not self.drink_counts:
            empty_surf = self.fonts.body.render("Ühtegi toodet ei leitud", True, Colors.GREY)
            screen.blit(empty_surf, (100, start_y))
        else:
            for i, (drink_name, count) in enumerate(self.drink_counts.items()):
                y = start_y + i * line_h
                # Limit drawing to screen height
                if y > 600:
                    more_surf = self.fonts.small.render("... rohkem tooteid", True, Colors.GREY)
                    screen.blit(more_surf, (100, y))
                    break
                
                # Format: "Drink Name 6X" (show count with X)
                if count > 1:
                    display_text = f"{drink_name} {count}X"
                else:
                    display_text = drink_name
                
                drink_surf = self.fonts.body.render(display_text, True, Colors.TEXT_PRIMARY)
                screen.blit(drink_surf, (100, y))
        
        # Draw buttons
        for btn in self.buttons:
            btn.draw(screen)
            
        debug_surf = self.fonts.small.render(self.__class__.__name__, True, Colors.YELLOW)
        screen.blit(debug_surf, debug_surf.get_rect(topright=(1014, 10)))
    
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
        btn_continue = Button(412, 550, 200, 80, "Jätka", fonts.body, Colors.GREEN, True)
        self.buttons = [btn_continue]
    
    def draw(self, screen):
        screen.fill(Colors.DARK_BG)
        
        # Success message - split into two lines
        line1 = f"Kasutaja {self.nimi}"
        line2 = f" on edukalt registreeritud."
        
        line1_surf = self.fonts.header.render(line1, True, Colors.GREEN)
        line1_rect = line1_surf.get_rect(center=(512, 200))
        screen.blit(line1_surf, line1_rect)
        
        line2_surf = self.fonts.header.render(line2, True, Colors.GREEN)
        line2_rect = line2_surf.get_rect(center=(512, 260))
        screen.blit(line2_surf, line2_rect)
        
        # Draw continue button
        for btn in self.buttons:
            btn.draw(screen)
            
        debug_surf = self.fonts.small.render(self.__class__.__name__, True, Colors.YELLOW)
        screen.blit(debug_surf, debug_surf.get_rect(topright=(1014, 10)))
    
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
        
        # Buttons
     
        self.btn_drink = Button(262, 300, 500, 150, "Login sisse, tahan juua", fonts.body, Colors.GREEN, "START_LOGIN")
        
        self.btn_kontohaldus = Button(750, 650, 220, 60, "KONTOHALDUS", fonts.small, Colors.BLUE, "GOTO_OPTIONS")
        
        # Options menu buttons
        self.btn_login_settings = Button(200, 350, 300, 100, "Logi sisse seadetesse", fonts.small, Colors.BLUE, "LOGIN_SEADED")
        self.btn_new_card = Button(524, 350, 300, 100, "Kaotasin kaardi", fonts.small, Colors.GREEN, "KAOTATUD_KAART")
        self.btn_new_account = Button(362, 480, 300, 80, "Loo uus kasutaja", fonts.small, Colors.BLUE, "UUS_KONTO")
        
        self.btn_back = Button(412, 650, 200, 60, "Tagasi", fonts.body, Colors.GREY, "BACK")

    def draw(self, screen):
        screen.fill(Colors.DARK_BG)
        rect = screen.get_rect()
        
        if self.state == "default":
            line1 = self.fonts.header.render("Tere tulemast, külaline!", True, Colors.TEXT_PRIMARY)
            
            screen.blit(line1, line1.get_rect(center=(rect.centerx, rect.centery - 200)))
            
            self.btn_drink.draw(screen)
            self.btn_kontohaldus.draw(screen)
            
            
        elif self.state == "viipa":
            line = self.fonts.header.render("Viipa kaarti logimiseks", True, Colors.TEXT_PRIMARY)
            screen.blit(line, line.get_rect(center=(rect.centerx, rect.centery)))
            self.btn_back.draw(screen)
            
        elif self.state == "options":
            line = self.fonts.header.render("Vali toiming", True, Colors.TEXT_PRIMARY)
            screen.blit(line, line.get_rect(center=(rect.centerx, 100)))
            
            self.btn_login_settings.draw(screen)
            self.btn_new_card.draw(screen)
            self.btn_new_account.draw(screen)
            self.btn_back.draw(screen)
            
        debug_surf = self.fonts.small.render(self.__class__.__name__, True, Colors.YELLOW)
        screen.blit(debug_surf, debug_surf.get_rect(topright=(1014, 10)))

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
                logging.info("drawer DEFAULT uploaded tagasi")
                return "tagasi"
        
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
                logging.info("drawer DEFAULT uploaded tagasi")
                return "tagasi"
                
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
        
        line1 = self.fonts.header.render(self.line1_text, True, Colors.TEXT_PRIMARY)
        line2 = self.fonts.body.render(self.line2_text, True, Colors.TEXT_PRIMARY)
        
        rect = screen.get_rect()
        screen.blit(line1, line1.get_rect(center=(rect.centerx, rect.centery - 40)))
        screen.blit(line2, line2.get_rect(center=(rect.centerx, rect.centery + 40)))
        
        debug_surf = self.fonts.small.render(self.__class__.__name__, True, Colors.YELLOW)
        screen.blit(debug_surf, debug_surf.get_rect(topright=(1014, 10)))
    
    def handle_input(self, event):
        # No interaction on door screen
        return None

#kuvab ükskõik mida samal ajal kui uks on avatud
class REKLAAM:
    def __init__(self, payload_data, fonts):
        self.fonts = fonts
        
    def draw(self, screen):
        screen.fill(Colors.BACKGROUND)
        line1 = self.fonts.header.render("UKS AVATUD, TEGUTSE", True, Colors.TEXT_PRIMARY)
        rect = screen.get_rect()
        screen.blit(line1, line1.get_rect(center=(rect.centerx, rect.centery - 40)))
        
        debug_surf = self.fonts.small.render(self.__class__.__name__, True, Colors.YELLOW)
        screen.blit(debug_surf, debug_surf.get_rect(topright=(1014, 10)))
        
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
        btn_yes = Button(150, 450, 250, 100, "JAH", fonts.header, Colors.GREEN, "yes")
        btn_no = Button(624, 450, 250, 100, "EI", fonts.header, Colors.RED, "no")
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
        start_x = 382
        start_y = 250
        btn_width = 80
        btn_height = 80
        spacing = 10
        
        # Buttons 1-9
        labels = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        for i, label in enumerate(labels):
            row = i // 3
            col = i % 3
            x = start_x + col * (btn_width + spacing)
            y = start_y + row * (btn_height + spacing)
            btn = Button(x, y, btn_width, btn_height, label, self.fonts.body, Colors.DK_BLUE, label)
            self.pinpad_buttons.append(btn)
        
        # Bottom row: Clear, 0, Enter
        row = 3
        
        # Clear button
        btn_clear = Button(start_x, start_y + row * (btn_height + spacing), btn_width, btn_height, 
                          "C", self.fonts.body, Colors.RED, "clear")
        self.pinpad_buttons.append(btn_clear)
        
        # 0 button
        btn_zero = Button(start_x + (btn_width + spacing), start_y + row * (btn_height + spacing), 
                         btn_width, btn_height, "0", self.fonts.body, Colors.BLUE, "0")
        self.pinpad_buttons.append(btn_zero)
        
        # Enter button
        btn_enter = Button(start_x + 2 * (btn_width + spacing), start_y + row * (btn_height + spacing), 
                          btn_width, btn_height, "E", self.fonts.body, Colors.GREEN, "enter")
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
        rect = frame.get_rect(center=(512, 384))
        screen.fill((0, 0, 0))
        screen.blit(frame, rect)

    def draw(self, screen):
        screen.fill(Colors.DARK_BG)
        
        if self.stage == "question":
            self._draw_question_stage(screen)
        elif self.stage == "pinpad":
            self._draw_pinpad_stage(screen)
        elif self.stage == "easter_egg":
            self._draw_easter_egg(screen)
            
        debug_surf = self.fonts.small.render(self.__class__.__name__, True, Colors.YELLOW)
        screen.blit(debug_surf, debug_surf.get_rect(topright=(1014, 10)))
    
    def _draw_question_stage(self, screen):
        """Draw the Yes/No question screen"""
        # Title
        title_surf = self.fonts.header.render("Kiipkaardile ei vasta kasutajat!", True, Colors.TEXT_PRIMARY)
        title_rect = title_surf.get_rect(center=(512, 100))
        screen.blit(title_surf, title_rect)
        
        # Additional text line
        subtitle_surf = self.fonts.body.render("Kas soovid registreerida?", True, Colors.GREY)
        subtitle_rect = subtitle_surf.get_rect(center=(512, 180))
        screen.blit(subtitle_surf, subtitle_rect)
        
        # Draw buttons
        for btn in self.buttons:
            btn.draw(screen)
    
    def _draw_pinpad_stage(self, screen):
        """Draw the PIN pad entry screen"""
        # Title
        title_surf = self.fonts.header.render("Sisesta PIN-kood", True, Colors.TEXT_PRIMARY)
        title_rect = title_surf.get_rect(center=(512, 100))
        screen.blit(title_surf, title_rect)
        
        # Display entered PIN with asterisks
        pin_display = self.pincode if self.pincode else "_ _ _ _"
        pin_surf = self.fonts.body.render(pin_display, True, Colors.TEXT_PRIMARY)
        pin_rect = pin_surf.get_rect(center=(512, 180))
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
            btn = Button(412, 650, 200, 60, "Jätka", fonts.body, Colors.GREEN, True)
            self.buttons.append(btn)
        
        # Wrap text to fit screen width (900px safe area)
        self.lines = self._wrap_text(self.text, self.fonts.body, 900)

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
        screen.fill(Colors.DARK_BG)
        
        # Draw text lines centered
        start_y = 200
        line_h = 40
        for i, line in enumerate(self.lines):
            surf = self.fonts.body.render(line, True, Colors.TEXT_PRIMARY)
            rect = surf.get_rect(center=(512, start_y + i * line_h))
            screen.blit(surf, rect)
        
        for btn in self.buttons:
            btn.draw(screen)
            
        debug_surf = self.fonts.small.render(self.__class__.__name__, True, Colors.YELLOW)
        screen.blit(debug_surf, debug_surf.get_rect(topright=(1014, 10)))

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
        btn = Button(412, 650, 200, 60, "Jätka", fonts.body, Colors.GREEN, True)
        self.buttons.append(btn)

    def draw(self, screen):
        screen.fill(Colors.BACKGROUND)

        # Title
        title_surf = self.fonts.header.render("Tagastasid:", True, Colors.TEXT_PRIMARY)
        title_rect = title_surf.get_rect(center=(512, 50))
        screen.blit(title_surf, title_rect)

        # List items
        start_y = 150
        line_h = 38
        if not self.items:
            empty_surf = self.fonts.body.render("Ei tuvastatud tagastusi", True, Colors.GREY)
            screen.blit(empty_surf, (100, start_y))
        else:
            x_name = 100
            x_count = 850
            for i, (name, count) in enumerate(self.items.items()):
                y = start_y + i * line_h
                # Limit drawing to screen height
                if y > 600:
                    more_surf = self.fonts.small.render("... rohkem tooteid", True, Colors.GREY)
                    screen.blit(more_surf, (100, y))
                    break
                name_surf = self.fonts.body.render(str(name), True, Colors.TEXT_PRIMARY)
                count_surf = self.fonts.body.render(f"{count}x", True, Colors.TEXT_PRIMARY)
                screen.blit(name_surf, (x_name, y))
                screen.blit(count_surf, (x_count, y))

        # Draw buttons
        for btn in self.buttons:
            btn.draw(screen)
            
        debug_surf = self.fonts.small.render(self.__class__.__name__, True, Colors.YELLOW)
        screen.blit(debug_surf, debug_surf.get_rect(topright=(1014, 10)))

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
        self.dates_scroll_index = 0
        
        # --- Buttons for MAIN state ---
        self.btn_new_card = Button(200, 350, 300, 100, "Vaheta kiipkaarti", fonts.body, Colors.BLUE, "UUS_KAART")
        self.btn_balance = Button(524, 350, 300, 100, "Vaata konto seisu", fonts.body, Colors.GREEN, "SHOW_BALANCE")
        self.btn_main_back = Button(412, 650, 200, 60, "Tagasi", fonts.body, Colors.RED, True)
        
        # --- Buttons for BALANCE state ---
        self.btn_dates = Button(750, 650, 200, 60, "Kuupäevad", fonts.small, Colors.BLUE, "SHOW_DATES")
        self.btn_balance_back = Button(100, 650, 200, 60, "Tagasi", fonts.body, Colors.GREY, "BACK_TO_MAIN")
        
        # --- Buttons for DATES state ---
        self.btn_dates_back = Button(412, 650, 200, 60, "Tagasi", fonts.body, Colors.GREY, "BACK_TO_BALANCE")
        
        # --- Scroll Buttons ---
        self.btn_scroll_up = Button(850, 150, 100, 80, "ÜLES", fonts.small, Colors.BLUE, "SCROLL_UP")
        self.btn_scroll_down = Button(850, 500, 100, 80, "ALLA", fonts.small, Colors.BLUE, "SCROLL_DOWN")

    def draw(self, screen):
        screen.fill(Colors.DARK_BG)
        rect = screen.get_rect()
        
        if self.state == "main":
            # Title
            title = self.fonts.header.render(f"Konto: {self.nimi}", True, Colors.TEXT_PRIMARY)
            screen.blit(title, title.get_rect(center=(rect.centerx, 100)))
            
            self.btn_new_card.draw(screen)
            self.btn_balance.draw(screen)
            self.btn_main_back.draw(screen)
            
        elif self.state == "balance":
            title = self.fonts.header.render("Sinu jookide seis", True, Colors.TEXT_PRIMARY)
            screen.blit(title, title.get_rect(center=(rect.centerx, 50)))
            
            # Group drinks
            counts = {}
            for item in self.unreturned_drinks:
                name = item[0]
                counts[name] = counts.get(name, 0) + 1
            
            start_y = 120
            if not counts:
                msg = self.fonts.body.render("Võlgnevusi pole!", True, Colors.GREEN)
                screen.blit(msg, msg.get_rect(center=(rect.centerx, start_y)))
            else:
                for i, (name, count) in enumerate(counts.items()):
                    y = start_y + i * 40
                    if y > 600: break
                    row_text = f"{name}: {count} tk"
                    surf = self.fonts.body.render(row_text, True, Colors.TEXT_PRIMARY)
                    screen.blit(surf, (100, y))
            
            self.btn_dates.draw(screen)
            self.btn_balance_back.draw(screen)
            
        elif self.state == "dates":
            title = self.fonts.header.render("Võtmise ajad", True, Colors.TEXT_PRIMARY)
            screen.blit(title, title.get_rect(center=(rect.centerx, 50)))
            
            start_y = 100
            line_height = 30
            max_y = 600
            
            if not self.unreturned_drinks:
                msg = self.fonts.body.render("Võlgnevusi pole!", True, Colors.GREEN)
                screen.blit(msg, msg.get_rect(center=(rect.centerx, start_y)))
            else:
                visible_items = self.unreturned_drinks[self.dates_scroll_index:]
                for i, item in enumerate(visible_items):
                    # item: (name, barcode, date)
                    name = item[0]
                    date_str = str(item[2])
                    y = start_y + i * line_height
                    if y > max_y: break
                    
                    row_text = f"{name} - {date_str}"
                    surf = self.fonts.small.render(row_text, True, Colors.TEXT_PRIMARY)
                    screen.blit(surf, (50, y))
                
                if self.dates_scroll_index > 0:
                    self.btn_scroll_up.draw(screen)
                
                items_per_page = (max_y - start_y) // line_height
                if self.dates_scroll_index + items_per_page < len(self.unreturned_drinks):
                    self.btn_scroll_down.draw(screen)
            
            self.btn_dates_back.draw(screen)
            
        debug_surf = self.fonts.small.render(self.__class__.__name__, True, Colors.YELLOW)
        screen.blit(debug_surf, debug_surf.get_rect(topright=(1014, 10)))

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
            
            res = self.btn_scroll_up.check_input(event)
            if res == "SCROLL_UP":
                self.dates_scroll_index = max(0, self.dates_scroll_index - 5)
                return None
                
            res = self.btn_scroll_down.check_input(event)
            if res == "SCROLL_DOWN":
                if self.dates_scroll_index + 16 < len(self.unreturned_drinks):
                    self.dates_scroll_index += 5
                return None
        
        return None

class UUS_KAART:
    def __init__(self, payload, fonts):
        self.fonts = fonts
        
    def draw(self, screen):
        screen.fill(Colors.DARK_BG)
        
        line1 = "Viipa oma uut kaarti"
        line2 = "registreerimiseks."
        
        surf1 = self.fonts.header.render(line1, True, Colors.TEXT_PRIMARY)
        rect1 = surf1.get_rect(center=(512, 300))
        screen.blit(surf1, rect1)
        
        surf2 = self.fonts.header.render(line2, True, Colors.TEXT_PRIMARY)
        rect2 = surf2.get_rect(center=(512, 370))
        screen.blit(surf2, rect2)
        
        debug_surf = self.fonts.small.render(self.__class__.__name__, True, Colors.YELLOW)
        screen.blit(debug_surf, debug_surf.get_rect(topright=(1014, 10)))

    def handle_input(self, event):
        return None

class KAOTATUD_KAART:
    def __init__(self, payload, fonts):
        self.fonts = fonts
        self.pincode = ""
        self.pinpad_buttons = []
        self._create_pinpad()
        
        self.btn_cancel = Button(100, 650, 200, 60, "Tühista", fonts.body, Colors.RED, "CANCEL")
        
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
        rect = frame.get_rect(center=(512, 384))
        screen.fill((0, 0, 0))
        screen.blit(frame, rect)

    def _create_pinpad(self):
        self.pinpad_buttons = []
        start_x = 382
        start_y = 250
        btn_width = 80
        btn_height = 80
        spacing = 10
        
        # Buttons 1-9
        labels = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        for i, label in enumerate(labels):
            row = i // 3
            col = i % 3
            x = start_x + col * (btn_width + spacing)
            y = start_y + row * (btn_height + spacing)
            btn = Button(x, y, btn_width, btn_height, label, self.fonts.body, Colors.DK_BLUE, label)
            self.pinpad_buttons.append(btn)
        
        # Bottom row: Clear, 0, Enter
        row = 3
        
        btn_clear = Button(start_x, start_y + row * (btn_height + spacing), btn_width, btn_height, 
                          "C", self.fonts.body, Colors.RED, "clear")
        self.pinpad_buttons.append(btn_clear)
        
        btn_zero = Button(start_x + (btn_width + spacing), start_y + row * (btn_height + spacing), 
                         btn_width, btn_height, "0", self.fonts.body, Colors.BLUE, "0")
        self.pinpad_buttons.append(btn_zero)
        
        btn_enter = Button(start_x + 2 * (btn_width + spacing), start_y + row * (btn_height + spacing), 
                          btn_width, btn_height, "E", self.fonts.body, Colors.GREEN, "enter")
        self.pinpad_buttons.append(btn_enter)

    def draw(self, screen):
        if self.show_easter_egg:
            self._draw_easter_egg(screen)
            return

        screen.fill(Colors.DARK_BG)
        
        line1 = "Sisesta pinnkood uue kaardi"
        line2 = "registreerimiseks"
        
        surf1 = self.fonts.header.render(line1, True, Colors.TEXT_PRIMARY)
        rect1 = surf1.get_rect(center=(512, 100))
        screen.blit(surf1, rect1)
        
        surf2 = self.fonts.header.render(line2, True, Colors.TEXT_PRIMARY)
        rect2 = surf2.get_rect(center=(512, 150))
        screen.blit(surf2, rect2)
        
        pin_display = self.pincode if self.pincode else "_ _ _ _"
        pin_surf = self.fonts.body.render(pin_display, True, Colors.TEXT_PRIMARY)
        pin_rect = pin_surf.get_rect(center=(512, 200))
        screen.blit(pin_surf, pin_rect)
        
        for btn in self.pinpad_buttons:
            btn.draw(screen)
            
        self.btn_cancel.draw(screen)
        
        debug_surf = self.fonts.small.render(self.__class__.__name__, True, Colors.YELLOW)
        screen.blit(debug_surf, debug_surf.get_rect(topright=(1014, 10)))

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
        btn_yes = Button(150, 500, 250, 100, "JAH", fonts.header, Colors.GREEN, True)
        btn_no = Button(624, 500, 250, 100, "EI", fonts.header, Colors.RED, False)
        
        self.buttons.append(btn_yes)
        self.buttons.append(btn_no)

    def draw(self, screen):
        screen.fill(Colors.DARK_BG)
        
        line1 = "Pinnkoodile vastavat kasutajat"
        line2 = "pole registreeritud."
        line3 = "Kas soovid registreerida?"
        
        surf1 = self.fonts.header.render(line1, True, Colors.TEXT_PRIMARY)
        rect1 = surf1.get_rect(center=(512, 150))
        screen.blit(surf1, rect1)
        
        surf2 = self.fonts.header.render(line2, True, Colors.TEXT_PRIMARY)
        rect2 = surf2.get_rect(center=(512, 210))
        screen.blit(surf2, rect2)
        
        surf3 = self.fonts.header.render(line3, True, Colors.TEXT_PRIMARY)
        rect3 = surf3.get_rect(center=(512, 300))
        screen.blit(surf3, rect3)
        
        for btn in self.buttons:
            btn.draw(screen)
            
        debug_surf = self.fonts.small.render(self.__class__.__name__, True, Colors.YELLOW)
        screen.blit(debug_surf, debug_surf.get_rect(topright=(1014, 10)))

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
        
        self.btn_cancel = Button(100, 650, 200, 60, "Tühista", fonts.body, Colors.RED, "CANCEL")
        
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
        rect = frame.get_rect(center=(512, 384))
        screen.fill((0, 0, 0))
        screen.blit(frame, rect)

    def _create_pinpad(self):
        self.pinpad_buttons = []
        start_x = 382
        start_y = 250
        btn_width = 80
        btn_height = 80
        spacing = 10
        
        # Buttons 1-9
        labels = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        for i, label in enumerate(labels):
            row = i // 3
            col = i % 3
            x = start_x + col * (btn_width + spacing)
            y = start_y + row * (btn_height + spacing)
            btn = Button(x, y, btn_width, btn_height, label, self.fonts.body, Colors.DK_BLUE, label)
            self.pinpad_buttons.append(btn)
        
        # Bottom row: Clear, 0, Enter
        row = 3
        
        btn_clear = Button(start_x, start_y + row * (btn_height + spacing), btn_width, btn_height, 
                          "C", self.fonts.body, Colors.RED, "clear")
        self.pinpad_buttons.append(btn_clear)
        
        btn_zero = Button(start_x + (btn_width + spacing), start_y + row * (btn_height + spacing), 
                         btn_width, btn_height, "0", self.fonts.body, Colors.BLUE, "0")
        self.pinpad_buttons.append(btn_zero)
        
        btn_enter = Button(start_x + 2 * (btn_width + spacing), start_y + row * (btn_height + spacing), 
                          btn_width, btn_height, "E", self.fonts.body, Colors.GREEN, "enter")
        self.pinpad_buttons.append(btn_enter)

    def draw(self, screen):
        if self.show_easter_egg:
            self._draw_easter_egg(screen)
            return

        screen.fill(Colors.DARK_BG)
        
        line1 = "Kasutaja registreerimiseks"
        line2 = "sisesta pinnkood!"
        
        surf1 = self.fonts.header.render(line1, True, Colors.TEXT_PRIMARY)
        rect1 = surf1.get_rect(center=(512, 100))
        screen.blit(surf1, rect1)
        
        surf2 = self.fonts.header.render(line2, True, Colors.TEXT_PRIMARY)
        rect2 = surf2.get_rect(center=(512, 150))
        screen.blit(surf2, rect2)
        
        pin_display = self.pincode if self.pincode else "_ _ _ _"
        pin_surf = self.fonts.body.render(pin_display, True, Colors.TEXT_PRIMARY)
        pin_rect = pin_surf.get_rect(center=(512, 200))
        screen.blit(pin_surf, pin_rect)
        
        for btn in self.pinpad_buttons:
            btn.draw(screen)
            
        self.btn_cancel.draw(screen)
        
        debug_surf = self.fonts.small.render(self.__class__.__name__, True, Colors.YELLOW)
        screen.blit(debug_surf, debug_surf.get_rect(topright=(1014, 10)))

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
        title_surf = self.fonts.header.render("Hetkel skaneeritud:", True, Colors.TEXT_PRIMARY)
        title_rect = title_surf.get_rect(center=(512, 50))
        screen.blit(title_surf, title_rect)
        
        # List items
        start_y = 150
        line_h = 38
        if not self.items:
            empty_surf = self.fonts.body.render("Skaneeri tooteid...", True, Colors.GREY)
            screen.blit(empty_surf, (100, start_y))
        else:
            x_name = 100
            x_count = 850
            for i, (name, count) in enumerate(self.items.items()):
                y = start_y + i * line_h
                if y > 700: break
                name_surf = self.fonts.body.render(str(name), True, Colors.TEXT_PRIMARY)
                count_surf = self.fonts.body.render(f"x{count}", True, Colors.TEXT_PRIMARY)
                screen.blit(name_surf, (x_name, y))
                screen.blit(count_surf, (x_count, y))
                
        debug_surf = self.fonts.small.render(self.__class__.__name__, True, Colors.YELLOW)
        screen.blit(debug_surf, debug_surf.get_rect(topright=(1014, 10)))

    def handle_input(self, event):
        return None

class CART_REVIEW:
    def __init__(self, payload_data, fonts):
        self.fonts = fonts
        # payload_data: {"Drink Name": count, ...}
        self.items = payload_data if isinstance(payload_data, dict) else {}
        self.buttons = []
        self._create_ui()

    def _create_ui(self):
        self.buttons = []
        start_y = 150
        line_h = 50
        
        # Confirm button
        btn_confirm = Button(412, 680, 200, 60, "Kinnita", self.fonts.body, Colors.GREEN, "CONFIRM")
        self.buttons.append(btn_confirm)

        # Item rows
        for i, (name, count) in enumerate(self.items.items()):
            y = start_y + i * line_h
            if y > 650: break 
            
            # Minus button
            btn_minus = Button(600, y, 40, 40, "-", self.fonts.body, Colors.RED, f"MINUS_{name}")
            self.buttons.append(btn_minus)
            
            # Plus button
            btn_plus = Button(750, y, 40, 40, "+", self.fonts.body, Colors.GREEN, f"PLUS_{name}")
            self.buttons.append(btn_plus)

    def draw(self, screen):
        screen.fill(Colors.BACKGROUND)
        
        title_surf = self.fonts.header.render("Kontrolli koguseid", True, Colors.TEXT_PRIMARY)
        title_rect = title_surf.get_rect(center=(512, 50))
        screen.blit(title_surf, title_rect)
        
        start_y = 150
        line_h = 50
        
        for i, (name, count) in enumerate(self.items.items()):
            y = start_y + i * line_h
            if y > 650: break
            
            name_surf = self.fonts.body.render(str(name), True, Colors.TEXT_PRIMARY)
            screen.blit(name_surf, (100, y + 5)) 
            
            count_surf = self.fonts.body.render(str(count), True, Colors.TEXT_PRIMARY)
            screen.blit(count_surf, (670, y + 5))

        for btn in self.buttons:
            btn.draw(screen)
            
        debug_surf = self.fonts.small.render(self.__class__.__name__, True, Colors.YELLOW)
        screen.blit(debug_surf, debug_surf.get_rect(topright=(1014, 10)))

    def handle_input(self, event):
        for btn in self.buttons:
            res = btn.check_input(event)
            if res == "CONFIRM":
                return self.items 
            
            if res and isinstance(res, str):
                if res.startswith("MINUS_"):
                    name = res[6:]
                    if name in self.items:
                        self.items[name] -= 1
                        if self.items[name] <= 0:
                            del self.items[name]
                        self._create_ui() 
                    return None
                
                if res.startswith("PLUS_"):
                    name = res[5:]
                    if name in self.items:
                        self.items[name] += 1
                        self._create_ui()
                    return None
        return None

def run_touchscreen(command_q, reply_q):
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    #pygame.display.set_caption("Sinine_kapp")
    
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

            elif command == "CART_REVIEW":
                logging.info("CART_REVIEW command received")
                current_screen_object = CART_REVIEW(payload, fonts)

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
