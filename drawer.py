import time

try:
    import pygame
except Exception:
    pygame = None

"""
DRAWER.PY - GUI Management

This module handles all visual output for the Sinine-kapp kiosk.

Key Architecture:
-----------------
• gui_handler(): Central controller running in a separate process. DO NOT call directly.
• Individual screen functions (Default_screen, Valiku_vaade, etc.) are called by gui_handler.
• main.py communicates with gui_handler via multiprocessing.Queue (commands & replies).

Adding a New Screen:
--------------------
1. Create a draw_my_screen(screen, data) function that renders your screen.
2. Add a case in gui_handler's event loop to handle "show_my_screen" commands.
3. From main.py, send: cmd_queue.put({"cmd": "show_my_screen", "data": {...}})
4. When user interacts, gui_handler sends a reply back via reply_queue.

DO NOT:
- Block inside screen functions (no long sleeps, no infinite loops).
- Create pygame surfaces outside gui_handler (processes can't share GUI objects).
- Call pygame directly from main.py.
"""


def Default_screen(stop_event=None, display_time_ms=None):
    """
    Show a pygame welcome window.
    - If `stop_event` (a multiprocessing.Event or threading.Event) is provided,
      the window stays open until the event is set.
    - Otherwise, if `display_time_ms` is provided, show for that duration (ms).
    If pygame is not available, falls back to printing a message.
    """
    if not pygame:
        print("---Praegu on kuvatud default ekraan\n Viipa nfc kaarti---")
        return

    try:
        pygame.init()
        screen = pygame.display.set_mode((640, 240))
        pygame.display.set_caption("Sinine-kapp - Welcome")

        # Colors
        BG = (30, 30, 60)
        TEXT = (240, 240, 240)

        # Font (use default if SysFont not available)
        try:
            font_large = pygame.font.SysFont(None, 48)
            font_small = pygame.font.SysFont(None, 28)
        except Exception:
            font_large = pygame.font.Font(None, 48)
            font_small = pygame.font.Font(None, 28)

        title_surf = font_large.render("Welcome to the kiosk", True, TEXT)
        instr_surf = font_small.render("Feel free to scan your NFC card.", True, TEXT)

        title_rect = title_surf.get_rect(center=(320, 80))
        instr_rect = instr_surf.get_rect(center=(320, 140))

        start = pygame.time.get_ticks()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Stop if stop_event is set
            if stop_event is not None:
                try:
                    if stop_event.is_set():
                        running = False
                except Exception:
                    # If the passed stop_event is not usable, ignore
                    pass

            # Or stop after display_time_ms if provided
            if display_time_ms is not None and (pygame.time.get_ticks() - start) >= display_time_ms:
                running = False

            screen.fill(BG)
            screen.blit(title_surf, title_rect)
            screen.blit(instr_surf, instr_rect)
            pygame.display.flip()
            pygame.time.delay(30)

    except Exception as e:
        print("---Praegu on kuvatud default ekraan\n Viipa nfc kaarti---")
        print(f"(drawer.Default_screen) pygame error: {e}")
    finally:
        try:
            pygame.quit()
        except Exception:
            pass
   


# KUI kasutaja on sisse logitud siis kuvab valikut (VÕTAN JOOGI või TAGASTAN)
#Funktsioon returnib väärtuse vastavaöt kasutaja inputile 
def Valiku_vaade(nimi):
    time.sleep(4)
    print(f"---Kuvan valikuvaate, kasutaja valib kas võtab või tagastab jooki--- \n Tere {nimi}")
    valik = input("--OOtab puuteekraanil valikut. Valik 1 võtan 2 tagastan→: ")
    time.sleep(3)
    return valik
    

#Väike vaheekraan enne ukse avamist. Ütleb et valisid joogi väljastuse, Avan sulle ukse)
def Võtmine():
    time.sleep(2)
    print(f"---Kuvatakse vaheekraan--- valisid väljastuse \n Avan ukse")

#kuvab ükskõik mida samal ajal kui uks on avatud
def Reklaam():
    print("---SAMAL ajal kui uks lahti kuvab drawer mingit suva reklaami, gifi või mida iganes")
    time.sleep(2)


#Kuvab ekraanil kokkuvõtte sellest mis tooted kasutaja võttis
def Võetud(drink_counts):
    for drink_name, count in drink_counts.items():
         # Prindime iga joogi ja selle koguse
        print(f"EKRAAN KUVAB võtsid --- {drink_name}: {count} tk---")
    
        print("------------------------")

#Kuvab tagastatud toodete kokkuvõtte
def Tagastatud(drink_counts):
    for drink_name, count in drink_counts.items():
         # Prindime iga joogi ja selle koguse
        print(f"---EKRAAN KUVAB Tagastasid --- {drink_name}: {count} tk---")
    
        print("------------------------")


## EKRAAN MIS KÜSIB KAS SOOVID REGADA kasutaja saab valida kas jah või ei. returnib y/n
def Regamise_küsimine():
    
    print("---Ekraan kuvab\" Kaart pole regatud ühegi kasutajaga, kas soovid registreerida\" ")
    vastus = input("---puuteekraani input (y/n)  ---")
    if vastus == "y":
        pinkood = input("---EKRAAN kUVAB-- registreerimisesk sisesta oma pinkood id(1111) ")
        print("---Ekraan kuvab Kontrollin kas pinkood on nimekirjas")
        time.sleep(2)
        return vastus, pinkood
    else:
        return vastus, None
    


##ekraan mis kuvab kasutaja regatud (HETKEL ILMA INPUTI JA RETURNITA)
def Kasutaja_regatud():
    print("---Ekraan kuvab kasutaja regatud")
    print("---ekraan kuvabSuunan tagasi avaekraanileõ")

#EKRaan mida kuvada kui pinn on vale
def Vale_pinnkood():
    print("---Ekraan kuvab :pinnkoodi ei ole nimekirjas Tagasi algusse")

def Tagastamine():
    print(f"--- kuvatakse vaheekraan. Valisid joogi tagastamise")