

import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1" #peatab pygame printimast tervitust konsooli
import pygame
import time
import logging
import queue

try:
    import pygame
except Exception:
    pygame = None






def gui_handler(command_queue, reply_queue):
    """
    Peamine GUI kontroller. Koodi all toodud register igale drawer funktsioonile,
    kus kirjas kas funktsioon ootab replyd ei oota jne...
    Trackib timeoute, seisu, käsitleb erroreid, saadab vastuseid main.py-sse

   
    """
    try:
        pygame.init()
        screen = pygame.display.set_mode((640, 240))
        pygame.display.set_caption("Sinine-kapp")
        clock = pygame.time.Clock()
        
        # Colors and fonts (shared across all screens)
        BG = (30, 30, 60)
        fonts = {
            "large": pygame.font.SysFont(None, 48),
            "small": pygame.font.SysFont(None, 28)
        }
        
        # Current screen state
        active_screen = "show_default"
        screen_data = {}
        screen_state = {}  # Persistent state for active handler
        handler_start_time = None
        current_handler = None
        wait_reply = False
        reply_id = None
        
        running = True
        
        while running:
            # ===== STEP 1: Check for new command from main.py =====
            try:
                command = command_queue.get_nowait()
                
                if command.get("cmd") == "stop":
                    running = False
                    logging.info("GUI handler stopping")
                    break
                
                # Get screen from registry
                cmd_name = command.get("cmd")
                if cmd_name in screen_registry:
                    active_screen = cmd_name
                    screen_data = command.get("data", {})
                    screen_state = {}  # Reset state for new screen
                    current_handler = screen_registry[cmd_name]["handler"]
                    wait_reply = command.get("wait_reply", False)
                    reply_id = command.get("reply_id", None)
                    handler_start_time = time.time()
                    logging.info(f"Switched to screen: {cmd_name}")
                else:
                    logging.warning(f"Unknown command: {cmd_name}")
            
            except queue.Empty:
                pass  # No new command, continue with current screen
            
            # ===== STEP 3: Check for timeout on blocking screens =====
            if current_handler and wait_reply:
                registry_entry = screen_registry.get(active_screen, {})
                timeout = registry_entry.get("timeout", None)
                
                if timeout and handler_start_time:
                    elapsed = time.time() - handler_start_time
                    if elapsed > timeout:
                        logging.warning(f"Screen {active_screen} timeout")
                        # Send timeout error reply
                        if reply_id:
                            reply_queue.put({"reply_id": reply_id, "result": None, "error": "timeout"})
                        # Reset to default
                        active_screen = "show_default"
                        current_handler = screen_registry["show_default"]["handler"]
                        screen_data = {}
                        screen_state = {}
                        wait_reply = False
                        reply_id = None
            
            # ===== STEP 4: Call current screen handler =====
            screen.fill(BG)
            
            try:
                if current_handler:
                    result = current_handler(screen, screen_data, fonts, screen_state)
                    
                    # ===== STEP 5: Handle result if handler returned one =====
                    if result is not None:
                        logging.info(f"Screen {active_screen} returned result: {result}")
                        
                        # If wait_reply is True, send result via reply_queue
                        if wait_reply and reply_id:
                            reply_msg = {
                                "reply_id": reply_id,
                                "result": result.get("result"),
                                "data": result  # Include full result dict
                            }
                            reply_queue.put(reply_msg)
                            logging.info(f"Sent reply: {reply_msg}")
                        
                        # Reset to default screen
                        active_screen = "show_default"
                        current_handler = screen_registry["show_default"]["handler"]
                        screen_data = {}
                        screen_state = {}
                        wait_reply = False
                        reply_id = None
                        handler_start_time = None
            
            except Exception as e:
                logging.error(f"Handler error in {active_screen}: {e}")
                # Show error screen
                active_screen = "show_error"
                screen_data = {"message": f"Error: {str(e)[:30]}"}
                screen_state = {}
                current_handler = screen_registry["show_error"]["handler"]
                wait_reply = False
            
            # ===== STEP 6: Render and display =====
            pygame.display.flip()
            clock.tick(30)  # 30 FPS

    except Exception as e:
        logging.error(f"GUI handler fatal error: {e}")
    
    finally:
        try:
            pygame.quit()
        except Exception:
            pass

def default_screen(screen, data, fonts, state):
    """
    Welcome/default screen. Always running, always returns None.
    """
    try:
        BG = (30, 30, 60)
        TEXT = (240, 240, 240)
        
        title_surf = fonts["large"].render("Welcome to the kiosk", True, TEXT)
        instr_surf = fonts["small"].render("Feel free to scan your NFC card.", True, TEXT)
        
        title_rect = title_surf.get_rect(center=(320, 80))
        instr_rect = instr_surf.get_rect(center=(320, 140))
        
        screen.blit(title_surf, title_rect)
        screen.blit(instr_surf, instr_rect)
        
        return None  # Always waiting for NFC card, never returns a result
    
    except Exception as e:
        logging.error(f"draw_default_screen error: {e}")
        return None


# KUI kasutaja on sisse logitud siis kuvab valikut (VÕTAN JOOGI või TAGASTAN)
#Funktsioon returnib väärtuse vastavaöt kasutaja inputile 
def valiku_vaade(screen, data, fonts, state):
    """
    Choice screen: User picks VÕTAN (1) or TAGASTAN (2).
    Returns result immediately on click.
    
    data = {"name": "Jaan"}
    
    Returns {"result": "1"} or {"result": "2"} when clicked, None otherwise.
    """
    try:
        BG = (30, 30, 60)
        TEXT = (240, 240, 240)
        BUTTON_COLOR = (70, 120, 180)
        HOVER_COLOR = (100, 150, 210)
        
        # Drain pygame event queue
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
        
        name = data.get("name", "User")
        
        # Normal choice screen
        greeting = fonts["large"].render(f"Tere {name}", True, TEXT)
        greeting_rect = greeting.get_rect(center=(320, 40))
        screen.blit(greeting, greeting_rect)
        
        # Button positions
        button1_rect = pygame.Rect(50, 120, 200, 100)  # VÕTAN
        button2_rect = pygame.Rect(390, 120, 200, 100)  # TAGASTAN
        
        # Update hover states (based on mouse position)
        mouse_pos = pygame.mouse.get_pos()
        state["button1_hover"] = button1_rect.collidepoint(mouse_pos)
        state["button2_hover"] = button2_rect.collidepoint(mouse_pos)
        
        # Draw buttons
        color1 = HOVER_COLOR if state["button1_hover"] else BUTTON_COLOR
        color2 = HOVER_COLOR if state["button2_hover"] else BUTTON_COLOR
        
        pygame.draw.rect(screen, color1, button1_rect)
        pygame.draw.rect(screen, color2, button2_rect)
        
        # Button text
        btn1_text = fonts["small"].render("VÕTAN", True, TEXT)
        btn2_text = fonts["small"].render("TAGASTAN", True, TEXT)
        
        btn1_rect = btn1_text.get_rect(center=button1_rect.center)
        btn2_rect = btn2_text.get_rect(center=button2_rect.center)
        
        screen.blit(btn1_text, btn1_rect)
        screen.blit(btn2_text, btn2_rect)
        
        # Check for click and return immediately
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button1_rect.collidepoint(event.pos):
                    logging.info("User clicked VÕTAN")
                    return {"result": "1"}
                elif button2_rect.collidepoint(event.pos):
                    logging.info("User clicked TAGASTAN")
                    return {"result": "2"}
        
        return None  # No click yet
    
    except Exception as e:
        logging.error(f"draw_choice_screen error: {e}")
        return {"result": None, "error": str(e)}

def ukse_avamine(screen, data, fonts, state):
    """
    Door opening confirmation screen. Shows message based on action.
    
    data = {"action": "1"} (VÕTAN) or {"action": "2"} (TAGASTAN)
    
    Returns None (just displays, timing handled in main.py).
    """
    try:
        BG = (30, 30, 60)
        TEXT = (240, 240, 240)
        
        # Drain pygame event queue
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
        
        # Determine message based on action
        action = data.get("action", "1")
        if action == "1":  # VÕTAN
            line1 = "Valisid joogi väljastuse."
            line2 = "Uks avaneb."
            line3 = "Proosit!"
        else:  # TAGASTAN (action == "2")
            line1 = "Valisid joogi tagastamise."
            line2 = "Uks avaneb."
            line3 = ""
        
        # Render lines
        line1_surf = fonts["large"].render(line1, True, TEXT)
        line2_surf = fonts["large"].render(line2, True, TEXT)
        
        line1_rect = line1_surf.get_rect(center=(320, 60))
        line2_rect = line2_surf.get_rect(center=(320, 120))
        
        screen.blit(line1_surf, line1_rect)
        screen.blit(line2_surf, line2_rect)
        
        if line3:
            line3_surf = fonts["small"].render(line3, True, TEXT)
            line3_rect = line3_surf.get_rect(center=(320, 180))
            screen.blit(line3_surf, line3_rect)
        
        return None  # Just display, no result
    
    except Exception as e:
        logging.error(f"ukse_avamine error: {e}")
        return None

#kuvab ükskõik mida samal ajal kui uks on avatud
def Reklaam():
    print("---SAMAL ajal kui uks lahti kuvab drawer mingit suva reklaami, gifi või mida iganes")
    time.sleep(2)


#Kuvab ekraanil kokkuvõtte sellest mis tooted kasutaja võttis. drink count on sõnastiku formaadis
# Näiteks kui kasutaja võtab 2 saku kulda ja ühe coca cola siis sõnastik näeb välja →→→ {'Saku Kuld': 2, 'Coca-Cola': 1}
def Võetud(drink_counts):
    for drink_name, count in drink_counts.items():
         # Prindime iga joogi ja selle koguse
        print(f"EKRAAN KUVAB võtsid --- {drink_name}: {count} tk---")
    
        print("------------------------")

#Kuvab tagastatud toodete kokkuvõtte sarnaselt välja võetud toodetele sõnastiku alusel. Vaata Võetud() funktsiooni kommentaare
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




#Siin märkida iga vaate parameetrid. Nimi peab matchima sellega mida main functionis cmd: välja kutsub.
"""Handler valib milline drawer funkstioon kasutusse läheb
wait_reply. kas funktsioon ootab kasutaja sisendit või ei
timeout. kui aksutaja ei vasta mingi aja jooksul siis kood teeb midagi mis ettenähtud"""
screen_registry = {
    "kuva_valikuvaade": {
        "handler": valiku_vaade,
        "wait_reply": True,
        "timeout": 30
    },
    "kuva_default_screen": {
        "handler": default_screen,
        "wait_reply": False,
        "timeou": None
    },
    "kuva_ukse_avamine": {
        "handler": ukse_avamine,
        "wait_reply": False,
        "timeout": None
    },
    "show_registration": {
        "handler": Regamise_küsimine,
        "wait_reply": True,
        "timeout": 30
    },
    ".........": {
        "handler": "",
        "wait_reply": False,
        "timeout": None
    }
}