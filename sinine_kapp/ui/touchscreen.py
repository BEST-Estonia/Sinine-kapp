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
from ..paths import ASSETS_DIR
from .components import (
    BaseScreen,
    Button,
    draw_count_list,
    get_event_pos,
    is_press_event,
    render_centered,
    render_at,
    wrap_text,
)
from .styles import FontManager, Colors


APP_EXIT = "__APP_EXIT__"
GIF_PATH = ASSETS_DIR / "67GIF.gif"
EXIT_GESTURE_WINDOW_SECONDS = 4
EXIT_GESTURE_TAP_COUNT = 5
EXIT_GESTURE_SIZE = 120
INPUT_DEBUG_ENABLED = False
TOUCH_VISUALIZER_ENABLED = True


def _configure_display_environment():
    """
    Make pygame prefer the Pi's local desktop session when started from SSH.
    This keeps local launches working while giving remote shells a sane default.
    """
    if not os.environ.get("DISPLAY"):
        os.environ["DISPLAY"] = ":0"

    if not os.environ.get("XAUTHORITY"):
        os.environ["XAUTHORITY"] = os.path.expanduser("~/.Xauthority")

    if not os.environ.get("XDG_RUNTIME_DIR"):
        os.environ["XDG_RUNTIME_DIR"] = f"/run/user/{os.getuid()}"

    logging.info(
        "Touchscreen display env: DISPLAY=%s XAUTHORITY=%s XDG_RUNTIME_DIR=%s",
        os.environ.get("DISPLAY"),
        os.environ.get("XAUTHORITY"),
        os.environ.get("XDG_RUNTIME_DIR"),
    )


class VALIKUVAADE(BaseScreen):
    def __init__(self, nimi, fonts):
        super().__init__(fonts)
        self.background = Colors.DARK_BG
        
        self.name_line = f"Tere {nimi}"
        self.question_line = "Tahad jooki võtta või tagasi tuua?"
        
      
        btn_take = Button(100, 350, 350, 200, "VÕTA JOOK", fonts.body, Colors.GREEN, "1")
        self.buttons.append(btn_take)
        
        btn_return = Button(574, 350, 350, 200, "TOO TAGASI", fonts.body, Colors.BLUE, "2")
        self.buttons.append(btn_return)
        
        btn_cancel = Button(412, 650, 200, 60, "TÜHISTA", fonts.body, Colors.RED, False)
        self.buttons.append(btn_cancel)

    def draw(self, screen):
        self.fill(screen)
        
        render_centered(screen, self.fonts.header, self.name_line, (512, 130))
        render_centered(screen, self.fonts.body, self.question_line, (512, 200))
        self.draw_buttons(screen)
        self.draw_debug_name(screen)

class VÄLJASTATUD_JOOGID(BaseScreen):
    def __init__(self, payload_data, fonts):
        super().__init__(fonts)
        # payload_data is expected to be a dict: {"Drink Name": count, ...}
        self.items = payload_data if isinstance(payload_data, dict) else {}

        # Create a confirm button (placeholder for future functionality)
        btn = Button(412, 650, 200, 60, "Kinnita", fonts.body, Colors.GREEN, True)
        self.buttons.append(btn)

    def draw(self, screen):
        self.fill(screen)
        render_centered(screen, self.fonts.header, "Väljastatud joogid", (512, 50))
        draw_count_list(screen, self.fonts, self.items, empty_text="Ühtegi toodet ei leitud")
        self.draw_buttons(screen)
        self.draw_debug_name(screen)

class UKSE_AVAMINE_TAGASTAMINE(BaseScreen):
    def __init__(self, payload_data, fonts):
        """
        Kuvatakse mis jooke kasutaja peab tagastama.
        payload_data is a list of tuples: [(productname, barcode, date_taken), ...]
        Groups drinks by product name and counts them.
        """
        super().__init__(fonts)
        self.drink_counts = {}  # Will store {"drink_name": count}

        # Accept both list and tuple payloads (different DB drivers may return either).
        rows = payload_data if isinstance(payload_data, (list, tuple)) else []
        if payload_data is not None and not isinstance(payload_data, (list, tuple)):
            logging.warning(
                f"UKSE_AVAMINE_TAGASTAMINE: unexpected payload type {type(payload_data).__name__}"
            )

        # Process payload: group by product name and count.
        for row in rows:
            if not isinstance(row, (list, tuple)) or len(row) < 1:
                continue

            product_name = row[0]
            if product_name in self.drink_counts:
                self.drink_counts[product_name] += 1
            else:
                self.drink_counts[product_name] = 1
        
        # Create continue button
        btn = Button(412, 650, 200, 60, "Jätka", fonts.body, Colors.GREEN, True)
        self.buttons.append(btn)
    
    def draw(self, screen):
        self.fill(screen)
        render_centered(screen, self.fonts.header, "Tagastamist ootavad joogid:", (512, 50), Colors.YELLOW)

        if not self.drink_counts:
            render_at(screen, self.fonts.body, "Ühtegi toodet ei leitud", (100, 150), Colors.GREY)
        else:
            for i, (drink_name, count) in enumerate(self.drink_counts.items()):
                y = 150 + i * 50
                if y > 600:
                    render_at(screen, self.fonts.small, "... rohkem tooteid", (100, y), Colors.GREY)
                    break

                display_text = f"{drink_name} {count}X" if count > 1 else drink_name
                render_at(screen, self.fonts.body, display_text, (100, y))

        self.draw_buttons(screen)
        self.draw_debug_name(screen)

class KASUTAJA_REGISTREERITUD(BaseScreen):
    def __init__(self, nimi, fonts):
        """
        Kinitiab et (nimi) on edukalt registreeritud. ja retruneb True kui kasutaja vajutab jätka nuppu
        """
        super().__init__(fonts)
        self.background = Colors.DARK_BG
        self.nimi = nimi
        
        # Create continue button
        btn_continue = Button(412, 550, 200, 80, "Jätka", fonts.body, Colors.GREEN, True)
        self.buttons = [btn_continue]
    
    def draw(self, screen):
        self.fill(screen)
        render_centered(screen, self.fonts.header, f"Kasutaja {self.nimi}", (512, 200), Colors.GREEN)
        render_centered(screen, self.fonts.header, " on edukalt registreeritud.", (512, 260), Colors.GREEN)
        self.draw_buttons(screen)
        self.draw_debug_name(screen)

class DEFAULT_SCREEN:
    def __init__(self, fonts):
        self.fonts = fonts
        self.state = "default" # default, viipa, options
        
        # Buttons
     
        self.btn_drink = Button(262, 300, 500, 150, "Joogi väljastus/tagastus", fonts.body, Colors.GREEN, "START_LOGIN")
        
        self.btn_kontohaldus = Button(650, 650, 300, 80, "KONTOHALDUS", fonts.small, Colors.BLUE, "GOTO_OPTIONS")
        
        self.btn_ADMIN = Button(20, 650, 240, 80, "ADMIN", fonts.small, Colors.RED, "GOTO_ADMIN")

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
            self.btn_ADMIN.draw(screen)
            
            
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

            res = self.btn_ADMIN.check_input(event)
            if res == "GOTO_ADMIN":
                return "ADMIN"

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
                if GIF_PATH.exists():
                    pil_image = Image.open(GIF_PATH)
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

class MESSAGE(BaseScreen):
    def __init__(self, payload, fonts):
        super().__init__(fonts)
        self.background = Colors.DARK_BG
        
        if isinstance(payload, tuple):
            self.text = str(payload[0]) if payload[0] else ""
            show_button = payload[1]
            button_text = str(payload[2]) if len(payload) > 2 and payload[2] else "Jätka"
        else:
            self.text = str(payload) if payload else ""
            show_button = True
            button_text = "Jätka"
        
        if show_button:
            # Button returns True (boolean) which will be put in reply_queue
            btn = Button(412, 650, 200, 60, button_text, fonts.body, Colors.GREEN, True)
            self.buttons.append(btn)
        
        # Wrap text to fit screen width (900px safe area)
        self.lines = wrap_text(self.text, self.fonts.body, 900)

    def draw(self, screen):
        self.fill(screen)
        
        # Draw text lines centered
        start_y = 200
        line_h = 40
        for i, line in enumerate(self.lines):
            render_centered(screen, self.fonts.body, line, (512, start_y + i * line_h))
        
        self.draw_buttons(screen)
        self.draw_debug_name(screen)

class TAGASTATUD_JOOGID(BaseScreen):
    def __init__(self, payload_data, fonts):
        super().__init__(fonts)
        # payload_data is expected to be a dict: {"Drink Name": count, ...}
        self.items = payload_data if isinstance(payload_data, dict) else {}

        # Create a continue button
        btn = Button(412, 650, 200, 60, "Jätka", fonts.body, Colors.GREEN, True)
        self.buttons.append(btn)

    def draw(self, screen):
        self.fill(screen)
        render_centered(screen, self.fonts.header, "Tagastasid:", (512, 50))
        draw_count_list(
            screen,
            self.fonts,
            self.items,
            empty_text="Ei tuvastatud tagastusi",
            count_prefix='',
            count_suffix='x',
        )
        self.draw_buttons(screen)
        self.draw_debug_name(screen)

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
                if GIF_PATH.exists():
                    pil_image = Image.open(GIF_PATH)
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
                if GIF_PATH.exists():
                    pil_image = Image.open(GIF_PATH)
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

class LIVE_CART(BaseScreen):
    def __init__(self, payload_data, fonts):
        super().__init__(fonts)
        # payload_data is expected to be a dict: {"Drink Name": count, ...}
        self.items = payload_data if isinstance(payload_data, dict) else {}

    def draw(self, screen):
        self.fill(screen)
        render_centered(screen, self.fonts.header, "Hetkel skaneeritud:", (512, 50))
        draw_count_list(
            screen,
            self.fonts,
            self.items,
            empty_text="Skaneeri tooteid...",
            max_y=700,
        )
        self.draw_debug_name(screen)

class CART_REVIEW(BaseScreen):
    def __init__(self, payload_data, fonts):
        super().__init__(fonts)
        # payload_data: {"Drink Name": count, ...}
        self.items = payload_data if isinstance(payload_data, dict) else {}
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
        self.fill(screen)
        render_centered(screen, self.fonts.header, "Kontrolli koguseid", (512, 50))
        
        start_y = 150
        line_h = 50
        
        for i, (name, count) in enumerate(self.items.items()):
            y = start_y + i * line_h
            if y > 650: break
            
            render_at(screen, self.fonts.body, name, (100, y + 5))
            render_at(screen, self.fonts.body, count, (670, y + 5))

        self.draw_buttons(screen)
        self.draw_debug_name(screen)

    def handle_input(self, event):
        for btn in self.buttons:
            res = btn.check_input(event)
            if res == "CONFIRM":
                return self.items 
            
            if res and isinstance(res, str):
                if res.startswith("MINUS_"):
                    name = res[6:]
                    if name in self.items:
                        if self.items[name] > 0:
                            self.items[name] -= 1
                        self._create_ui() 
                    return None
                
                if res.startswith("PLUS_"):
                    name = res[5:]
                    if name in self.items:
                        self.items[name] += 1
                        self._create_ui()
                    return None
        return None

class REMOVE_PRODUCT_LIST:
    def __init__(self, products, fonts):
        self.fonts = fonts
        self.products = products # list of (id, name, barcode)
        self.scroll_index = 0
        self.selected_id = None
        
        self.btn_up = Button(850, 150, 100, 80, "ÜLES", fonts.small, Colors.BLUE, "SCROLL_UP")
        self.btn_down = Button(850, 500, 100, 80, "ALLA", fonts.small, Colors.BLUE, "SCROLL_DOWN")
        self.btn_delete = Button(312, 650, 200, 60, "KUSTUTA", fonts.body, Colors.RED, "DELETE")
        self.btn_back = Button(50, 650, 200, 60, "TAGASI", fonts.body, Colors.GREY, "BACK")
        
        self.buttons = [self.btn_up, self.btn_down, self.btn_delete, self.btn_back]

    def draw(self, screen):
        screen.fill(Colors.DARK_BG)
        title = self.fonts.header.render("Vali toode eemaldamiseks", True, Colors.TEXT_PRIMARY)
        screen.blit(title, title.get_rect(center=(512, 50)))
        
        start_y = 120
        line_h = 50
        max_y = 600
        
        visible_products = self.products[self.scroll_index:]
        
        for i, prod in enumerate(visible_products):
            pid, name, barcode = prod
            y = start_y + i * line_h
            if y > max_y: break
            
            # Highlight selected
            color = Colors.GREEN if pid == self.selected_id else Colors.TEXT_PRIMARY
            
            text = f"{name} ({barcode})"
            surf = self.fonts.body.render(text, True, color)
            screen.blit(surf, (100, y))

        for btn in self.buttons:
            # Only draw delete if selected
            if btn == self.btn_delete and self.selected_id is None:
                continue
            btn.draw(screen)
            
    def handle_input(self, event):
        if is_press_event(event):
            pos = get_event_pos(event)
            if pos is None:
                return None
            mx, my = pos
            if 100 <= mx <= 800 and 120 <= my <= 600:
                idx = (my - 120) // 50
                real_idx = self.scroll_index + idx
                if 0 <= real_idx < len(self.products):
                    self.selected_id = self.products[real_idx][0]
        
        for btn in self.buttons:
            if btn == self.btn_delete and self.selected_id is None: continue
            res = btn.check_input(event)
            if res == "DELETE": return ("DELETE_PRODUCT", self.selected_id)
            if res == "SCROLL_UP": self.scroll_index = max(0, self.scroll_index - 5)
            elif res == "SCROLL_DOWN": 
                if self.scroll_index + 5 < len(self.products): self.scroll_index += 5
            elif res: return res
        return None

class ADMIN:
    def __init__(self, fonts):
        self.fonts = fonts
        self.state = "main" # main, products
        self.input_text = ""
        self.keyboard_buttons = []
        
        # Main state buttons
        self.btn_products = Button(312, 300, 400, 100, "Lisa/Eemalda toode", fonts.body, Colors.BLUE, "GOTO_PRODUCTS")
        self.btn_debtors = Button(312, 450, 400, 100, "Võlglased", fonts.body, Colors.BLUE, "SHOW_DEBTORS")
        self.btn_back = Button(412, 650, 200, 60, "Tagasi", fonts.body, Colors.GREY, "BACK")
        
        # Products state buttons
        self.btn_add = Button(312, 300, 400, 100, "Lisa", fonts.body, Colors.GREEN, "ADD_PRODUCT")
        self.btn_remove = Button(312, 450, 400, 100, "Eemalda", fonts.body, Colors.RED, "REMOVE_PRODUCT")
        self.btn_back_products = Button(50, 650, 200, 60, "Tagasi", fonts.body, Colors.GREY, "BACK_TO_MAIN")
        
        self._create_keyboard()

    def _create_keyboard(self):
        self.keyboard_buttons = []
        # Layout
        rows = [
            "1234567890",
            "QWERTYUIOP",
            "ASDFGHJKL",
            "ZXCVBNM"
        ]
        
        start_y = 250
        key_size = 60
        spacing = 10
        
        # Letters
        for r, row_keys in enumerate(rows):
            row_width = len(row_keys) * (key_size + spacing) - spacing
            start_x = (1024 - row_width) // 2
            
            for c, char in enumerate(row_keys):
                x = start_x + c * (key_size + spacing)
                y = start_y + r * (key_size + spacing)
                btn = Button(x, y, key_size, key_size, char, self.fonts.body, Colors.DK_BLUE, f"KEY_{char}")
                self.keyboard_buttons.append(btn)
        
        # Special keys
        y_special = start_y + 4 * (key_size + spacing)
        
        # Space
        btn_space = Button(202, y_special, 400, key_size, "SPACE", self.fonts.body, Colors.DK_BLUE, "KEY_SPACE")
        self.keyboard_buttons.append(btn_space)
        
        # Backspace
        btn_back = Button(612, y_special, 100, key_size, "<--", self.fonts.body, Colors.RED, "KEY_BACKSPACE")
        self.keyboard_buttons.append(btn_back)
        
        # Enter
        btn_enter = Button(722, y_special, 100, key_size, "OK", self.fonts.body, Colors.GREEN, "KEY_ENTER")
        self.keyboard_buttons.append(btn_enter)

    def draw(self, screen):
        screen.fill(Colors.DARK_BG)
        rect = screen.get_rect()
        
        if self.state == "main":
            title = self.fonts.header.render("Admin paneel", True, Colors.TEXT_PRIMARY)
            screen.blit(title, title.get_rect(center=(rect.centerx, 100)))
            
            self.btn_products.draw(screen)
            self.btn_debtors.draw(screen)
            self.btn_back.draw(screen)
            
        elif self.state == "products":
            title = self.fonts.header.render("Toodete haldus", True, Colors.TEXT_PRIMARY)
            screen.blit(title, title.get_rect(center=(rect.centerx, 100)))
            
            self.btn_add.draw(screen)
            self.btn_remove.draw(screen)
            self.btn_back_products.draw(screen)
            
        elif self.state == "enter_name":
            title = self.fonts.header.render("SISESTA toote nimi", True, Colors.TEXT_PRIMARY)
            screen.blit(title, title.get_rect(center=(rect.centerx, 80)))
            
            # Input box visualization
            pygame.draw.rect(screen, Colors.GREY, (212, 150, 600, 80), 2)
            text_surf = self.fonts.header.render(self.input_text, True, Colors.TEXT_PRIMARY)
            screen.blit(text_surf, text_surf.get_rect(center=(rect.centerx, 190)))
            
            for btn in self.keyboard_buttons:
                btn.draw(screen)
                
            # Cancel button for input mode
            self.btn_back_products.draw(screen)
            
        debug_surf = self.fonts.small.render(self.__class__.__name__, True, Colors.YELLOW)
        screen.blit(debug_surf, debug_surf.get_rect(topright=(1014, 10)))

    def handle_input(self, event):
        if self.state == "main":
            res = self.btn_products.check_input(event)
            if res == "GOTO_PRODUCTS":
                self.state = "products"
                return None
            
            res = self.btn_debtors.check_input(event)
            if res: return res
                
            res = self.btn_back.check_input(event)
            if res: return res
        
        elif self.state == "products":
            res = self.btn_add.check_input(event)
            if res == "ADD_PRODUCT":
                self.state = "enter_name"
                self.input_text = ""
                return None
                
            res = self.btn_remove.check_input(event)
            if res: return res
            
            res = self.btn_back_products.check_input(event)
            if res == "BACK_TO_MAIN":
                self.state = "main"
                return None
                
        elif self.state == "enter_name":
            res = self.btn_back_products.check_input(event)
            if res == "BACK_TO_MAIN":
                self.state = "products"
                return None
                
            for btn in self.keyboard_buttons:
                res = btn.check_input(event)
                if res:
                    if res.startswith("KEY_"):
                        key = res[4:]
                        if key == "SPACE":
                            self.input_text += " "
                        elif key == "BACKSPACE":
                            self.input_text = self.input_text[:-1]
                        elif key == "ENTER":
                            if self.input_text:
                                return ("PRODUCT_NAME", self.input_text)
                        else:
                            if len(self.input_text) < 20:
                                self.input_text += key
                    return None
        
        return None

def run_touchscreen(command_q, reply_q):
    _configure_display_environment()
    pygame.init()

    try:
        #screen = pygame.display.set_mode((1024, 768))
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    except pygame.error as exc:
        logging.exception("Failed to start touchscreen UI: %s", exc)
        raise

    #pygame.display.set_caption("Sinine_kapp")

    # 1. INITIALIZE STYLE MANAGER
    # Laeb fondid
    fonts = FontManager()

    current_screen_object = None
    current_screen_object = DEFAULT_SCREEN(fonts)
    running = True
    barcode_buffer = ""
    barcode_scanning_enabled = False  # Control whether barcode scanning is active
    exit_tap_times = []
    last_input_debug = None

    while running:
        try:
            command, payload = command_q.get_nowait()
            logging.info(f"Router received: {command} with payload: {payload}")

            if command == "ENABLE_BARCODE_SCANNING":
                barcode_scanning_enabled = True
                logging.info("Barcode scanning ENABLED")
                continue

            elif command == "DISABLE_BARCODE_SCANNING":
                barcode_scanning_enabled = False
                barcode_buffer = ""  # Clear any partial barcode when disabling
                logging.info("Barcode scanning DISABLED")
                continue

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
            
            elif command == "ADMIN":
                logging.info("ADMIN command received")
                current_screen_object = ADMIN(fonts)
            
            elif command == "REMOVE_PRODUCT_LIST":
                logging.info("REMOVE_PRODUCT_LIST command received")
                current_screen_object = REMOVE_PRODUCT_LIST(payload, fonts)

            elif command == "STOP":
                reply_q.put(APP_EXIT)
                running = False

        except queue.Empty:
            pass 

        # ... Input Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                reply_q.put(APP_EXIT)
                running = False

            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_q):
                logging.info("Developer exit shortcut pressed")
                reply_q.put(APP_EXIT)
                running = False

            if is_press_event(event):
                pos = get_event_pos(event)
                raw_debug = None
                if hasattr(event, "pos"):
                    raw_debug = event.pos
                elif hasattr(event, "x") and hasattr(event, "y"):
                    raw_debug = (round(event.x, 4), round(event.y, 4))
                last_input_debug = {
                    "type": pygame.event.event_name(event.type),
                    "touch": getattr(event, "touch", None),
                    "raw": raw_debug,
                    "mapped": pos,
                }
                if INPUT_DEBUG_ENABLED:
                    logging.info("INPUT DEBUG: %s", last_input_debug)
                if pos is None:
                    continue
                if pos[0] <= EXIT_GESTURE_SIZE and pos[1] <= EXIT_GESTURE_SIZE:
                    now = time.time()
                    exit_tap_times = [
                        tap_time
                        for tap_time in exit_tap_times
                        if now - tap_time <= EXIT_GESTURE_WINDOW_SECONDS
                    ]
                    exit_tap_times.append(now)

                    if len(exit_tap_times) >= EXIT_GESTURE_TAP_COUNT:
                        logging.info("Developer exit gesture detected")
                        reply_q.put(APP_EXIT)
                        running = False
                        continue
                else:
                    exit_tap_times.clear()

            # --- BARCODE SCANNER LOGIC ---
            if barcode_scanning_enabled and event.type == pygame.KEYDOWN:
                # On enter, send buffer and clear it
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    if len(barcode_buffer) > 2: # Ignore accidental enter presses
                        logging.info(f"DRAWER: Barcode captured, sending to queue: {barcode_buffer}")
                        reply_q.put(f"BARCODE:{barcode_buffer}")
                    barcode_buffer = ""
                # On backspace, remove last char
                elif event.key == pygame.K_BACKSPACE:
                    barcode_buffer = barcode_buffer[:-1]
                # Otherwise, add character to buffer
                else:
                    barcode_buffer += event.unicode
            # --- END OF BARCODE SCANNER LOGIC ---

            if current_screen_object:
                res = current_screen_object.handle_input(event)
                if res is not None: reply_q.put(res)

        # ... Drawing 
        if current_screen_object:
            current_screen_object.draw(screen)
        else:
            DEFAULT_SCREEN(screen, fonts)

        if INPUT_DEBUG_ENABLED and last_input_debug is not None:
            debug_text = (
                f"{last_input_debug['type']} touch={last_input_debug['touch']} "
                f"raw={last_input_debug['raw']} mapped={last_input_debug['mapped']}"
            )
            debug_surf = fonts.small.render(debug_text, True, Colors.RED)
            screen.blit(debug_surf, (20, 20))

        if TOUCH_VISUALIZER_ENABLED and last_input_debug is not None:
            mapped = last_input_debug["mapped"]
            if mapped is not None:
                pygame.draw.circle(screen, Colors.RED, mapped, 12, 3)

        pygame.display.flip()

    pygame.quit()
