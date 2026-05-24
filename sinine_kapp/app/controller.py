from collections import Counter
import atexit
import logging
import multiprocessing
import queue
import signal
import time

from ..devices import hardware
from ..devices.lcd import LCD
from ..paths import LOG_FILE
from ..services import database
from ..ui import touchscreen

APP_EXIT = "__APP_EXIT__"
lcd = None
# QUEUES initialization
_gui_proc = None
command_queue = None
reply_queue = None
_shutting_down = False


# Set up logging (kasutus: logging.debug .info .warning .error .critical)
logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def _require_lcd():
    if lcd is None:
        raise RuntimeError("LCD is not initialized")
    return lcd


def _handle_signal(signum, _frame):
    logging.info("Received signal %s, shutting down application", signum)
    raise SystemExit(128 + signum)


def _install_signal_handlers():
    handled_signals = [signal.SIGINT, signal.SIGTERM]
    if hasattr(signal, "SIGHUP"):
        handled_signals.append(signal.SIGHUP)

    for sig in handled_signals:
        signal.signal(sig, _handle_signal)


def _shutdown_gui_process():
    global _gui_proc

    if _gui_proc is None:
        return

    if command_queue is not None:
        try:
            command_queue.put(("STOP", None))
        except Exception:
            pass

    _gui_proc.join(timeout=2)

    if _gui_proc.is_alive():
        _gui_proc.terminate()
        _gui_proc.join(timeout=2)

    _gui_proc = None


def _cleanup():
    global _shutting_down

    if _shutting_down:
        return

    _shutting_down = True

    _shutdown_gui_process()

    if lcd is not None:
        try:
            lcd.cleanup()
        except Exception:
            logging.exception("LCD cleanup failed")

    try:
        hardware.cleanup()
    except Exception:
        logging.exception("Hardware cleanup failed")


def _read_reply(timeout=None):
    if timeout is None:
        message = reply_queue.get()
    else:
        message = reply_queue.get(timeout=timeout)

    if message == APP_EXIT:
        raise SystemExit

    return message

def Empty_reply_queue():
    try:
        while True:
            message = reply_queue.get_nowait()
            if message == APP_EXIT:
                raise SystemExit
    except queue.Empty:
        pass

def Empty_command_queue():
    try:
        while True:
            command_queue.get_nowait()
    except queue.Empty:
        pass

def Oota_kasutaja_kinnitust(timeout):
    try:
        response = _read_reply(timeout=timeout)
        if response == True: 
            pass
    except queue.Empty:
        pass

def wait_for_barcode_from_queue(timeout):
    """Waits for a barcode message from the reply_queue."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        remaining_time = timeout - (time.time() - start_time)
        if remaining_time <= 0:
            break
        try:
            # Wait for a short duration to be responsive
            message = _read_reply(timeout=min(1, remaining_time))
            if isinstance(message, str) and message.startswith("BARCODE:"):
                return message.replace("BARCODE:", "", 1)
            # else, it's a different UI event, ignore it and keep waiting
        except queue.Empty:
            continue
    return None # Timeout

def check_for_cancel():
    try:
        msg = reply_queue.get_nowait()
        if msg == APP_EXIT:
            raise SystemExit
        if msg == "tagasi":
            return True
        if msg is True: # Handle "Jätka" button from MESSAGE screen as cancel
            return True
    except queue.Empty:
        pass
    return False

#Funktsioonid GUI protsessi käivitamiseks ja käsitlemiseks

def GUI_default():
    """
    Show the default welcome screen in the GUI process.
    Does NOT block main — just sends a command and returns immediately.
    """
  
    
    if command_queue is None:
        logging.error("GUI handler not initialized")
        return
    
    command_queue.put( ("DEFAULT", None) )
    logging.info("Sent 'kuva_default_screen' command to GUI")
def GUI_valikuvaade(nimi):

    # 2. Send command (returns immediately, non-blocking)
    nimi = nimi
    command_queue.put( ("VALIKUVAADE", nimi) )
    
    try:
        # Wait up to 30 seconds for user input
        reply = _read_reply(timeout=30)
        return str(reply) # Return "1" or "2"
    except queue.Empty:
        logging.warning("User timed out on choice screen")
        return None

def GUI_ukse_avamine(action_type, unreturned_items=None):
    """argument 1- ukse avamine ja jookide võtmine
    argument 2- ukse avamine ja jookide tagastamine
    
    For return mode (action_type="2"), optionally pass unreturned_items list
    to display what drinks the user needs to return.
    """
    
    # If returning drinks and we have unreturned items, pass them as tuple
    if action_type == "2":
        command_queue.put( ("UKSE_AVAMINE_TAGASTAMINE", unreturned_items) )
    else:
        command_queue.put( ("UKSE_AVAMINE_VÕTMINE", None) )

    

    logging.info(f"Sent door opening screen command: {action_type}")
#ekraanivaade, mis kuvatakse samal ajal kui uks lahti
def GUI_reklaam():
     command_queue.put( ("REKLAAM", None) )

#käivitab registreerimise küsimise drawery. ja returnib main loopile pinkoodi kui kasutaja otsustas regada
def GUI_registreerimise_küsimine():
    command_queue.put(("REGISTREERIMINE", None)) #Reutirb vastus(True/False), pinnkood
    try:
        vastus, pinnkood = _read_reply(timeout=60)
        return vastus, pinnkood
    except queue.Empty:
        return False, None
    
#Ütleb drawerile mis jooke ja kui palju võeti. selle põhjal drawer kuvab
def GUI_võetud(scanned_items_info):
    """
    Võtab vastu listi joogiinfo SÕNEDEGA (stringidega), loendab need kokku
    ja saadab info drawerisse kuvamiseks.
    """
    
    # 'scanned_items_info' list näeb välja juba selline:
    # ['Saku Kuld', 'sommersby', 'Saku Kuld']

  
    drink_counts = Counter(scanned_items_info)
    
    # See teeb automaatselt sõnastiku:
    # {'Saku Kuld': 2, 'Coca-Cola': 1}

    # 3. Nüüd saada see drawerisse
    print(f"DEBUG: Kokkuvõte saadetud drawerisse: {drink_counts}")
    command_queue.put( ("VÄLJASTATUD_JOOGID", drink_counts) )

#Ütleb drawerile mis jooke vüeti ja drawer kuvab. 
def GUI_tagastatud(scanned_items_info):
    """
    Võtab vastu listi joogiinfo SÕNEDEGA (stringidega), loendab need kokku
    ja saadab info drawerisse kuvamiseks.
    """
    
    # 'scanned_items_info' list näeb välja juba selline:
    # ['Saku Kuld', 'sommersby', 'Saku Kuld']

  
    drink_counts = Counter(scanned_items_info)
    
    # See teeb automaatselt sõnastiku:
    # {'Saku Kuld': 2, 'Coca-Cola': 1}

    # 3. Nüüd saada see drawerisse
    print(f"DEBUG: Kokkuvõte saadetud drawerisse: {drink_counts}")
    command_queue.put( ("TAGASTATUD_JOOGID", drink_counts) )

def GUI_live_cart(scanned_items_info):
    drink_counts = Counter(scanned_items_info)
    command_queue.put( ("LIVE_CART", drink_counts) )

def GUI_kasutaja_registreeritud(nimi):
    command_queue.put( ("KASUTAJA_REGISTREERITUD", nimi) )
    
#Ekraanivaade, mis kuvatakse kui pinnkoodile polnud andmebaasis vastet
def GUI_pinn_vale():
    GUI_message("Vale pinnkood")

def GUI_message(message, show_button=True):
    command_queue.put( ("MESSAGE", (message, show_button)) )

def _show_database_error_if_needed(timeout=8):
    if database.last_connection_error() is None:
        return False

    GUI_message("Andmebaasiga ei saa ühendust. Kontrolli võrku või serverit.")
    Oota_kasutaja_kinnitust(timeout)
    return True

def admin_loop():
    """
    Handles the admin screen logic loop.
    """
    command_queue.put(("ADMIN", None))

    while True:
        try:
            valik = _read_reply()

            if valik == "BACK":
                logging.info("Admin loop: barcode scanning disabled")
                command_queue.put(("DISABLE_BARCODE_SCANNING", None))
                return # Exit to main loop

            elif isinstance(valik, tuple) and valik[0] == "PRODUCT_NAME":
                product_name = valik[1]

                # Enable barcode scanning for product addition
                logging.info("Admin loop: enabling barcode scanning for product addition")
                command_queue.put(("ENABLE_BARCODE_SCANNING", None))

                # Scanning flow
                while True:
                    GUI_message(f"Skänni uue toote triipkood", show_button=False)
                    code1 = wait_for_barcode_from_queue(timeout=20)
                    if not code1:
                        GUI_message("Triipkoodi ei leitud. Proovi uuesti.", show_button=True)
                        Oota_kasutaja_kinnitust(10)
                        break # Back to admin menu

                    GUI_message("Skänni uuesti kontrolliks", show_button=False)
                    time.sleep(2) # Wait to prevent immediate re-read
                    Empty_reply_queue()
                    code2 = wait_for_barcode_from_queue(timeout=20)

                    if code1 == code2:
                        # Assuming database service has this method
                        try:
                            database.add_product(product_name, code1)
                            GUI_message(f"{product_name} on lisatud andmebaasi", show_button=True)
                        except AttributeError:
                            logging.error("database.add_product method missing")
                            GUI_message("Viga andmebaasiga suhtlemisel", show_button=True)

                        Oota_kasutaja_kinnitust(10)
                        break
                    else:
                        GUI_message("Koodid ei ühti. Proovi uuesti.", show_button=True)
                        Oota_kasutaja_kinnitust(10)
                        # Loop continues to retry scanning

                # Disable barcode scanning after product addition
                logging.info("Admin loop: disabling barcode scanning after product addition")
                command_queue.put(("DISABLE_BARCODE_SCANNING", None))
                # Return to admin screen
                command_queue.put(("ADMIN", None))

            elif valik == "REMOVE_PRODUCT":
                while True:
                    try:
                        products = database.get_all_products()
                    except AttributeError:
                        logging.error("database.get_all_products missing")
                        products = []

                    command_queue.put(("REMOVE_PRODUCT_LIST", products))

                    resp = _read_reply()
                    if resp == "BACK":
                        command_queue.put(("ADMIN", None))
                        break
                    elif isinstance(resp, tuple) and resp[0] == "DELETE_PRODUCT":
                        pid = resp[1]
                        try:
                            database.remove_product(pid)
                            GUI_message("Toode eemaldatud", show_button=False)
                            time.sleep(1)
                        except AttributeError:
                            GUI_message("Viga andmebaasiga", show_button=True)
                            Oota_kasutaja_kinnitust(5)
                        # Loop continues to refresh list

        except queue.Empty:
            pass

def kontohaldus(): 
    nfc_input = hardware.get_nfc(check_for_cancel)
    if nfc_input is None:
        return None, None
    print(f"DEBUG: Loetud NFC tag {nfc_input}")
    #Db handler kontrollib kas nfc uid on andmebaasis. kui jah tagastab IsinDB = True, kui ei False ja nimi
    IsinDB, nimi = database.checkuser(nfc_input)
    if IsinDB == True:
        unreturned_drinks = database.get_unreturned_drinks(nfc_input)
        payload = (nimi, unreturned_drinks)
        Empty_reply_queue()
        command_queue.put( ("KONTOHALDUS", payload) ) #Käivitab ekraani kust näeb jookide seisu
        return nfc_input, nimi
    else:
        if _show_database_error_if_needed():
            return None, None
        GUI_message("Kaarti ei leitud")
        Oota_kasutaja_kinnitust(5)
        return None, None
    
def uus_kaart(LOGITUD, nimi, nfc_input): #UUe NFC kaardi regamise funkt. juhul kui kasutaja sisse logitd ja juhul kui kaart kadunud
    '''Kui LOGITUD = True siis kasutaja sisse logitud ja registreerib uue kaardi
       Kui LOGITUD = False siis kasutaja pole sisse logitud ja registreerib kaardi pinnkoodiga'''
    payload = (LOGITUD, nimi, nfc_input)
    Empty_reply_queue()
    command_queue.put( ("UUS_KAART", payload) )
    if LOGITUD == True:
        nfc_uus = hardware.get_nfc()
        
        is_card_registered, existing_owner = database.checkuser(nfc_uus)
        if _show_database_error_if_needed():
            return
        if is_card_registered:
            GUI_message(f"Kaart juba registreeritud kasutajale {existing_owner}!")
            Oota_kasutaja_kinnitust(10)
            return
        
        database.update_user_nfc(nfc_input, nfc_uus)
        GUI_message(f"Uus kaart nimele {nimi} registreeritud")
        Oota_kasutaja_kinnitust(10)
    elif LOGITUD == False: #Kaardi regamine kui kasutajal vana kaart kadunud
        command_queue.put( ("KAOTATUD_KAART", None))
        pinnkood = _read_reply()
        is_pin_in_pintable =  database.check_pin_code_dict(pinnkood) #kontrollib kas pin on andmebaasis
        is_user_registered = database.is_user_registered(pinnkood) #kontrollib kas pin on juba registreeritud kasutajale
        found, nimi = database.nime_kaeve_pintabelist(pinnkood)
        if _show_database_error_if_needed():
            return

        if is_pin_in_pintable == True and is_user_registered == True:
            GUI_message(f"Kasutaja {nimi} leitud. Viipa uut kaarti registreerimiseks", show_button=False)
            uus_nfc = hardware.get_nfc()
            # Kontrollime, kas kaart on juba kellegi teise nimel
            is_card_registered, existing_owner = database.checkuser(uus_nfc)
            if _show_database_error_if_needed():
                return
            
            if is_card_registered:
                GUI_message(f"Kaart juba registreeritud kasutajale {existing_owner}!")
                Oota_kasutaja_kinnitust(10)
                return
            # --- FIX END ---

            database.register_new_card(uus_nfc, nimi)
            GUI_message(f"Uus kaart nimele {nimi} on edukalt registreeritud.")
            return
            database.register_new_card(uus_nfc, nimi)
            GUI_message(f"Uus kaart nimele {nimi} on edukalt registreeritud.")
            return
        elif is_pin_in_pintable == True and is_user_registered == False:
            command_queue.put(("REGISTREERI_PINNKOODI_ALUSEL", None))
            vastus = _read_reply(timeout=60)
            if vastus == True:
                GUI_message(f"Viipa kiipkaarti kasutaja {nimi} registreerimiseks.", show_button=False)
                nfc_input = hardware.get_nfc()
                IsinDB, kasutu_muutuja = database.checkuser(nfc_input)
                if _show_database_error_if_needed():
                    return
                Empty_reply_queue()
                if IsinDB == True:
                    GUI_message("Kaart on juba registreeritud mõnele kasutajale")
                    Oota_kasutaja_kinnitust(15)
                else:
                    database.create_new_user(nfc_input, pinnkood)
                    Empty_reply_queue()
                    GUI_message(f"Kasutaja {nimi} registreeritud! proosit!")
                    Oota_kasutaja_kinnitust(15)
            else: 
                pass
        else: 
            GUI_message("Pinnkoodi ei leitud.")
            Oota_kasutaja_kinnitust(10)

#Main loop käivitab default ekraani vaate, jääb nfc inputi ootama ja otsustab kas minna edasi
#valiku või regamis ekraanile või kontohalduse ekraanile
#!!!!!!!! Iga print fn selles plokis on debuggimiseks ja ei kuvata lõpuks puuteekraanil.
# Printimisi peavad handlema teised funktsiooni ja lõpuks touchscreen.py
def main_loop():
    global command_queue, reply_queue, _gui_proc
    command_queue = multiprocessing.Queue()
    reply_queue = multiprocessing.Queue()
    _gui_proc = multiprocessing.Process(target=touchscreen.run_touchscreen, args=(command_queue, reply_queue))
    _gui_proc.start()

    # Initialize door sensor with button
    hardware.init_door_sensor()

    while True:
        Empty_reply_queue()
        GUI_default()
        valik = _read_reply()  # Ootab, kuni kasutaja vajutab ekraanil midagi kas
        """LOGI SISSE - kasutaja saab jooke väljastada või tagastada
           LOGIN_SEADED - kasutaja siseneb kontohalduse menüüsse kust saab vaadata võetud jookide seisu ja uut kaarti regada
           KAOTATUD KAART - kasutaja registreerib uue pinkoodi alusel"""
            
        if valik == "LOGI_SISSE":
            #Ootab  handlerilt nfc inputi
            nfc_input = hardware.get_nfc(check_for_cancel)
            if nfc_input is None:
                continue
            print(f"DEBUG: Loetud NFC tag {nfc_input}")
            #Db handler kontrollib kas nfc uid on andmebaasis. kui jah tagastab IsinDB = True, kui ei False ja nimi
            IsinDB, nimi = database.checkuser(nfc_input)
            if IsinDB == True:
                valik = GUI_valikuvaade(nimi) #Valiku vaade küsib kasutajalt kas tahan kapist võtta või kappi panna
                
                #Tagastab mis valisid antud juhul 1 Võtan kapist alksi 2 tagastan. 

                print(f"DEBUG: Valisid {valik}")
                if valik == "1":
                    joogi_väljastus(nfc_input)  
                elif valik == "2":
                    joogi_tagastus(nfc_input) 
                    pass
                else:
                    # Kui valik oli "Tühista" vms, ei tee me midagi
                    # ja tsükkel algab automaatselt uuesti
                    pass
                # --- LÕPP ---
        
            else: 
                if _show_database_error_if_needed():
                    continue
            #Küsime kasutajalt kas tahab registreerida uue kasutaja mis vastab nfc uid-le. Ootame vastuseks True/False ja pinnkoodi
                vastus, pinnkood = GUI_registreerimise_küsimine()
            
                if vastus == True:
                    pinnkood = int(pinnkood)
                    
                    is_pin_in_pintable =  database.check_pin_code_dict(pinnkood) #kontrollib kas pin on andmebaasis
                    is_user_registered = database.is_user_registered(pinnkood) #kontrollib kas pin on juba registreeritud kasutajale
                    if _show_database_error_if_needed():
                        continue
                    if is_pin_in_pintable == True:
                        if is_user_registered == True:
                            logging.info("Kasutaja üritas registreerida juba registreeritud PIN-koodi.")
                            Empty_reply_queue()
                            GUI_message("See PIN on juba registreeritud kiipkaardile, uue kaardi registreerimiseks valige Kontohaldus avaekraanilt")
                            Oota_kasutaja_kinnitust(30)
                            continue 
                        else:
                            database.create_new_user(nfc_input, pinnkood) #annab funktsioonile sisse nfc uid ja sisestatud pinnkoodi ja loob uue kasutaja
                            found, nimi = database.nime_kaeve_pintabelist(pinnkood) #kaevab pintabelist nime mis vastab pinnkoodile
                            if found:
                                # Clear any stale messages from previous screens
                                Empty_reply_queue()
                                
                                GUI_kasutaja_registreeritud(nimi)
                                #ootab et et kasutaja vajutaks jätka. timeoutx sekundit siis kood jätkub
                                Oota_kasutaja_kinnitust(30)
                                continue
                            else:
                                GUI_message("Jõudsid koodi osasse mida keegi näha ei tohiks, palun võta ühendust adminiga.")
                                Oota_kasutaja_kinnitust(30)
                                continue
                    else:
                        #Kui pin koodi pole andmebaasis siis kuvab veateate
                        Empty_reply_queue()
                        GUI_message("Sisestatud PIN-kood ei ole kehtiv. Palun proovi uuesti.")
                        Oota_kasutaja_kinnitust(20)
                        continue

                #Kui kasutaja ei taha kontot regada siis loop jätkub default screeniga
                else:
                    Empty_reply_queue() 
                    GUI_message("Tagasi avaekraanile.")
                    Oota_kasutaja_kinnitust(20)
                    Empty_command_queue()
                    Empty_reply_queue() 
                    continue

        elif valik == "LOGIN_SEADED":  
            nfc_input, nimi = kontohaldus() #funktsioon handleb sisse logimist kui ebaõnnestub algab mainloop uuesti
            if nfc_input is None:
                continue
            vastus = _read_reply()
            if vastus == "UUS_KAART": #kui kasutaja tahab uuendada kaarti ja on juba regatud
                uus_kaart(True, nimi, nfc_input)
            else:
                continue
        elif valik == "KAOTATUD_KAART": 
            uus_kaart(False, None, None)
        elif valik == "UUS_KONTO":
            Empty_reply_queue()
            command_queue.put(("UUE_KONTO_REGAMINE_PINNKOODIGA", None))
            vastus = _read_reply()
            pinnkood = vastus
            if vastus == "CANCEL":
                pass
            else:
                is_pin_in_pintable =  database.check_pin_code_dict(pinnkood) #kontrollib kas pin on andmebaasis
                is_user_registered = database.is_user_registered(pinnkood) #kontrollib kas pin on juba registreeritud kasutajale
                if _show_database_error_if_needed():
                    continue
                if is_pin_in_pintable == True:
                    if is_user_registered == True:
                        logging.info("Kasutaja üritas registreerida juba registreeritud PIN-koodi.")
                        Empty_reply_queue()
                        GUI_message("See PIN on juba registreeritud kiipkaardile, uue kaardi registreerimiseks valige Kontohaldus avaekraanilt")
                        Oota_kasutaja_kinnitust(30)
                        continue 
                    else:
                        found, nimi = database.nime_kaeve_pintabelist(pinnkood) #kaevab pintabelist nime mis vastab pinnkoodile
                        GUI_message(f"Tere, {nimi}! Viipa kiipkaarti kasutaja registreerimiseks", show_button=False)
                        nfc_input = hardware.get_nfc()
                        database.create_new_user(nfc_input, pinnkood) #annab funktsioonile sisse nfc uid ja sisestatud pinnkoodi ja loob uue kasutaja
                        
                        if found:
                            Empty_reply_queue()                               
                            GUI_kasutaja_registreeritud(nimi)
                            #ootab et et kasutaja vajutaks jätka. timeout x sekundit siis kood jätkub
                            Oota_kasutaja_kinnitust(30)
                            continue
                        else:
                            GUI_message("Jõudsid koodi osasse mida keegi näha ei tohiks, palun võta ühendust adminiga.")
                            Oota_kasutaja_kinnitust(30)
                            continue
                else:
                    #Kui pin koodi pole andmebaasis siis kuvab veateate
                    Empty_reply_queue()
                    GUI_message("Sisestatud PIN-kood ei ole kehtiv. Palun proovi uuesti.")
                    Oota_kasutaja_kinnitust(20)
                    continue

        elif valik == "ADMIN":
            GUI_message("Viipa admin kiipi", show_button=True)
            nfc_input = hardware.get_nfc(check_for_cancel)
            
            if nfc_input:
                is_in_db, name = database.checkuser(nfc_input)
                if is_in_db and name == "ADMIN":
                    admin_loop()
                else:
                    if _show_database_error_if_needed():
                        continue
                    GUI_message("Vale kaart")
                    Oota_kasutaja_kinnitust(3)
            # If nfc_input is None (cancelled via button), loop restarts automatically


#Joogi väljastuse plokk
def joogi_väljastus(nfc_input):
    nfc_input = nfc_input
    GUI_ukse_avamine("1")
    time.sleep(1)  # Näita ukse avamise ekraani 4 sekundit

    _require_lcd().set_backlight(True)

    #Avab ukse
    hardware.Ukse_avaja()

    # Enable barcode scanning before door opens
    logging.info("joogi_väljastus: enabling barcode scanning")
    command_queue.put(("ENABLE_BARCODE_SCANNING", None))

    # Oota kuni uks avaneb
    wait_start = time.time()
    while not hardware.is_door_open():
        if time.time() - wait_start > 10: # 10s timeout
            break
        time.sleep(0.1)

    #poe ostukorvi vaade vmidagi. Ma ka ei tea enam
    GUI_live_cart([])

     #Siia salvestub list jookidest mis skännitakse.
    scanned_items_info = []
    scanned_barcodes = [] #See on list triipkoodidest
    #Kapi sisese LCD tühjendus ja sõnumi kuvamine
    _require_lcd().clear()
    _require_lcd().show_message("Skaneeri tooted...")

    #LOOP mis käib nii kaua kuni kapi uks on lahti.
    while hardware.is_door_open(): #kui isdooropen tagastab True on uks lahti False siis kinni
        barcode_to_process = None
        try:
            # Check for messages from GUI (non-blocking)
            message = reply_queue.get_nowait()
            if message == APP_EXIT:
                raise SystemExit
            logging.info(f"MAIN-LOOP: Got message from reply_q: {message}")

            if isinstance(message, str) and message.startswith("BARCODE:"):
                barcode_to_process = message.replace("BARCODE:", "", 1)

        except queue.Empty:
            # No message, do nothing
            pass

        if barcode_to_process:
            logging.info(f"MAIN-LOOP: Processing as barcode: {barcode_to_process}")
            is_in_db, drink_info = database.get_drink_info(barcode_to_process)

            if is_in_db == False:
                _require_lcd().show_message("Toodet pole nimekirjas")
                time.sleep(1) # Show message briefly
                _require_lcd().clear()
                _require_lcd().show_message("Skaneeri tooted...")
                continue # Skip to next loop iteration

            # This part only runs for valid barcodes
            scanned_barcodes.append(barcode_to_process)
            scanned_items_info.append(drink_info)
            GUI_live_cart(scanned_items_info)
            print(f"DEBUG: {scanned_items_info}")

            count = scanned_items_info.count(drink_info)
            _require_lcd().show_message(f"{drink_info} X{count}")
            time.sleep(1) # Show message briefly
            _require_lcd().clear()
            _require_lcd().show_message("Skaneeri tooted...")

        # Väike paus, et tsükkel ei koormaks protsessorit
        time.sleep(0.05)


    _require_lcd().set_backlight(False)
    # Disable barcode scanning when door closes
    logging.info("joogi_väljastus: disabling barcode scanning")
    command_queue.put(("DISABLE_BARCODE_SCANNING", None))

    # 3. Tsükkel lõppes (Uks pandi kinni)
    # Kood jõuab siia hetkel, kui door sensor tagastab False


    # --- CART REVIEW LOGIC START ---
    # 1. Map names to barcodes so we can reconstruct the list later
    name_to_barcode = {}
    for name, code in zip(scanned_items_info, scanned_barcodes):
        name_to_barcode[name] = code

    # 2. Send data to review screen
    logging.info(f"MAIN-LOOP: Final cart before review: {scanned_items_info}")
    Empty_reply_queue()
    drink_counts = Counter(scanned_items_info)
    command_queue.put(("CART_REVIEW", dict(drink_counts)))

    # 3. Wait for user confirmation (modified counts)
    try:
        final_counts = _read_reply(timeout=300) # 5 min timeout
    except queue.Empty:
        final_counts = drink_counts

    # 4. Reconstruct scanned lists based on final counts
    scanned_barcodes = []
    scanned_items_info = []
    if isinstance(final_counts, dict):
        for name, count in final_counts.items():
            if count > 0:
                code = name_to_barcode.get(name)
                if code:
                    scanned_barcodes.extend([code] * count)
                    scanned_items_info.extend([name] * count)
    # --- CART REVIEW LOGIC END ---
    GUI_võetud(scanned_items_info)
    time.sleep(6)
    # 4. Salvesta andmed andmebaasi
    # Anna kogu 'scanned_items' list ja 'nfc_input' andmebaasile
    database.log_user_taken_drinks(nfc_input, scanned_barcodes)
    database.keep_stock(scanned_barcodes, "taken")
    # Tühjenda LCD uueks kasutajaks
    _require_lcd().clear()

    # (Funktsioon lõppeb ja main_loop läheb tagasi algusesse, ootama uut NFC-d)
    Empty_reply_queue()
    Empty_command_queue()
    return


def joogi_tagastus(nfc_input):

    #kasutja id
    nfc_input = nfc_input

    # Fetch unreturned drinks before opening the door
    unreturned_drinks = database.get_unreturned_drinks(nfc_input)
    logging.info(
        f"joogi_tagastus: unreturned payload type={type(unreturned_drinks).__name__}, count={len(unreturned_drinks) if hasattr(unreturned_drinks, '__len__') else 'n/a'}"
    )

    GUI_ukse_avamine("2", unreturned_drinks)
    Oota_kasutaja_kinnitust(30)

    _require_lcd().set_backlight(True)
    hardware.Ukse_avaja()

    # Enable barcode scanning before door opens
    logging.info("joogi_tagastus: enabling barcode scanning")
    command_queue.put(("ENABLE_BARCODE_SCANNING", None))

    # Oota kuni uks avaneb
    wait_start = time.time()
    while not hardware.is_door_open():
        if time.time() - wait_start > 10: # 10s timeout
            break
        time.sleep(0.1)

    #Reklaam samal ajal kui uks lahti
    GUI_live_cart([])

     #Siia salvestub jookide nimikiri mis skännitakse. See on list jookdie NIMEDEST
    scanned_items_info = []
    scanned_barcodes = [] #See on list triipkoodidest
    #Kapi sisese LCD tühjendus ja sõnumi kuvamine
    _require_lcd().clear()
    _require_lcd().show_message("Skaneeri tooted...")

    #LOOP mis käib nii kaua kuni kapi uks on lahti.
    while hardware.is_door_open(): #kui isdooropen tagastab True on uks lahti False siis kinni
        barcode_to_process = None
        try:
            # Check for messages from GUI (non-blocking)
            message = reply_queue.get_nowait()
            if message == APP_EXIT:
                raise SystemExit
            logging.info(f"MAIN-LOOP: Got message from reply_q: {message}")

            if isinstance(message, str) and message.startswith("BARCODE:"):
                barcode_to_process = message.replace("BARCODE:", "", 1)

        except queue.Empty:
            # No message, do nothing
            pass

        if barcode_to_process:
            logging.info(f"MAIN-LOOP: Processing as barcode: {barcode_to_process}")
            is_in_db, drink_info = database.get_drink_info(barcode_to_process)

            if is_in_db == False:
                _require_lcd().show_message("Toodet pole nimekirjas")
                time.sleep(1) # Show message briefly
                _require_lcd().clear()
                _require_lcd().show_message("Skaneeri tooted...")
                continue # Skip to next loop iteration

            # This part only runs for valid barcodes
            scanned_barcodes.append(barcode_to_process)
            scanned_items_info.append(drink_info)
            GUI_live_cart(scanned_items_info)
            print(f"DEBUG: {scanned_items_info}")

            count = scanned_items_info.count(drink_info)
            _require_lcd().show_message(f"{drink_info} X{count}")
            time.sleep(1) # Show message briefly
            _require_lcd().clear()
            _require_lcd().show_message("Skaneeri tooted...")

        # Väike paus, et tsükkel ei koormaks protsessorit
        time.sleep(0.05)

    _require_lcd().set_backlight(False)
    # Disable barcode scanning when door closes
    logging.info("joogi_tagastus: disabling barcode scanning")
    command_queue.put(("DISABLE_BARCODE_SCANNING", None))

    # 3. Tsükkel lõppes (Uks pandi kinni)
    # Kood jõuab siia hetkel, kui door sensor tagastab False

    print("DEBUG: Uks suletud. Lõpetan sessiooni...---")

    # --- CART REVIEW LOGIC START ---
    # 1. Map names to barcodes
    name_to_barcode = {}
    for name, code in zip(scanned_items_info, scanned_barcodes):
        name_to_barcode[name] = code

    # 2. Send data to review screen
    logging.info(f"MAIN-LOOP: Final cart before review: {scanned_items_info}")
    Empty_reply_queue()
    drink_counts = Counter(scanned_items_info)
    command_queue.put(("CART_REVIEW", dict(drink_counts)))

    # 3. Wait for user confirmation
    try:
        final_counts = _read_reply(timeout=300)
    except queue.Empty:
        final_counts = drink_counts

    # 4. Reconstruct scanned lists
    scanned_barcodes = []
    scanned_items_info = []
    if isinstance(final_counts, dict):
        for name, count in final_counts.items():
            if count > 0:
                code = name_to_barcode.get(name)
                if code:
                    scanned_barcodes.extend([code] * count)
                    scanned_items_info.extend([name] * count)
    # --- CART REVIEW LOGIC END ---
    GUI_tagastatud(scanned_items_info) #Kuvab mis joogid kasutaja võttis
    time.sleep(6)
    # 4. Salvesta andmed andmebaasi
    # Anna kogu 'scanned_items' list ja 'user_id' andmebaasile
    database.log_user_returned_drinks(nfc_input, scanned_barcodes)
    database.keep_stock(scanned_barcodes, "returned")
    # 6. Korista ja lõpeta

    # Tühjenda LCD uueks kasutajaks
    _require_lcd().clear()

    Empty_reply_queue()
    # (Funktsioon lõppeb ja taastab kontrolli main_loopile)
    return


   

#KOOOD ALGAB SIIT 
#Käivitame drawreri eraldi protsessina

def run():
    global lcd

    _install_signal_handlers()
    atexit.register(_cleanup)

    lcd = LCD()

    try:
        main_loop()
    finally:
        _cleanup()


if __name__ == "__main__":
    run()
