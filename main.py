from collections import Counter
import time
import drawer
import hardware_handler
import database_handler
from lcd import LCD
import logging
import multiprocessing
import queue
lcd = LCD()
# QUEUES initialization
_gui_proc = None
command_queue = None
reply_queue = None


# Set up logging (kasutus: logging.debug .info .warning .error .critical)
logging.basicConfig(
    filename='main.log',  # Log file name
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def Empty_reply_queue():
    try:
        while True:
            reply_queue.get_nowait()
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
        response = reply_queue.get(timeout=timeout)
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
            message = reply_queue.get(timeout=min(1, remaining_time))
            if isinstance(message, str) and message.startswith("BARCODE:"):
                return message.replace("BARCODE:", "", 1)
            # else, it's a different UI event, ignore it and keep waiting
        except queue.Empty:
            continue
    return None # Timeout

def check_for_cancel():
    try:
        msg = reply_queue.get_nowait()
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
        reply = reply_queue.get(timeout=30)
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
        vastus, pinnkood = reply_queue.get(timeout=60)
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
    drawer.Vale_pinnkood()

def GUI_message(message, show_button=True):
    command_queue.put( ("MESSAGE", (message, show_button)) )

def admin_loop():
    """
    Handles the admin screen logic loop.
    """
    command_queue.put(("ADMIN", None))
    
    while True:
        try:
            valik = reply_queue.get()
            
            if valik == "BACK":
                return # Exit to main loop
            
            elif isinstance(valik, tuple) and valik[0] == "PRODUCT_NAME":
                product_name = valik[1]
                
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
                        # Assuming database_handler has this method
                        try:
                            database_handler.add_product(product_name, code1)
                            GUI_message(f"{product_name} on lisatud andmebaasi", show_button=True)
                        except AttributeError:
                            logging.error("database_handler.add_product method missing")
                            GUI_message("Viga andmebaasiga suhtlemisel", show_button=True)
                        
                        Oota_kasutaja_kinnitust(10)
                        break
                    else:
                        GUI_message("Koodid ei ühti. Proovi uuesti.", show_button=True)
                        Oota_kasutaja_kinnitust(10)
                        # Loop continues to retry scanning
                
                # Return to admin screen
                command_queue.put(("ADMIN", None))
                
            elif valik == "REMOVE_PRODUCT":
                while True:
                    try:
                        products = database_handler.get_all_products()
                    except AttributeError:
                        logging.error("database_handler.get_all_products missing")
                        products = []
                        
                    command_queue.put(("REMOVE_PRODUCT_LIST", products))
                    
                    resp = reply_queue.get()
                    if resp == "BACK":
                        command_queue.put(("ADMIN", None))
                        break
                    elif isinstance(resp, tuple) and resp[0] == "DELETE_PRODUCT":
                        pid = resp[1]
                        try:
                            database_handler.remove_product(pid)
                            GUI_message("Toode eemaldatud", show_button=False)
                            time.sleep(1)
                        except AttributeError:
                            GUI_message("Viga andmebaasiga", show_button=True)
                            Oota_kasutaja_kinnitust(5)
                        # Loop continues to refresh list
                
        except queue.Empty:
            pass

def kontohaldus(): 
    nfc_input = hardware_handler.get_nfc(check_for_cancel)
    if nfc_input is None:
        return None, None
    print(f"DEBUG: Loetud NFC tag {nfc_input}")
    #Db handler kontrollib kas nfc uid on andmebaasis. kui jah tagastab IsinDB = True, kui ei False ja nimi
    IsinDB, nimi = database_handler.checkuser(nfc_input)
    if IsinDB == True:
        unreturned_drinks = database_handler.get_unreturned_drinks(nfc_input)
        payload = (nimi, unreturned_drinks)
        Empty_reply_queue()
        command_queue.put( ("KONTOHALDUS", payload) ) #Käivitab ekraani kust näeb jookide seisu
        return nfc_input, nimi
    else:
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
        nfc_uus = hardware_handler.get_nfc()
        
        is_card_registered, existing_owner = database_handler.checkuser(nfc_uus)
        if is_card_registered:
            GUI_message(f"Kaart juba registreeritud kasutajale {existing_owner}!")
            Oota_kasutaja_kinnitust(10)
            return
        
        database_handler.update_user_nfc(nfc_input, nfc_uus)
        GUI_message(f"Uus kaart nimele {nimi} registreeritud")
        Oota_kasutaja_kinnitust(10)
    elif LOGITUD == False: #Kaardi regamine kui kasutajal vana kaart kadunud
        command_queue.put( ("KAOTATUD_KAART", None))
        pinnkood = reply_queue.get()
        is_pin_in_pintable =  database_handler.check_pin_code_dict(pinnkood) #kontrollib kas pin on andmebaasis
        is_user_registered = database_handler.is_user_registered(pinnkood) #kontrollib kas pin on juba registreeritud kasutajale
        found, nimi = database_handler.nime_kaeve_pintabelist(pinnkood)

        if is_pin_in_pintable == True and is_user_registered == True:
            GUI_message(f"Kasutaja {nimi} leitud. Viipa uut kaarti registreerimiseks", show_button=False)
            uus_nfc = hardware_handler.get_nfc()
            # Kontrollime, kas kaart on juba kellegi teise nimel
            is_card_registered, existing_owner = database_handler.checkuser(uus_nfc)
            
            if is_card_registered:
                GUI_message(f"Kaart juba registreeritud kasutajale {existing_owner}!")
                Oota_kasutaja_kinnitust(10)
                return
            # --- FIX END ---

            database_handler.register_new_card(uus_nfc, nimi)
            GUI_message(f"Uus kaart nimele {nimi} on edukalt registreeritud.")
            return
            database_handler.register_new_card(uus_nfc, nimi)
            GUI_message(f"Uus kaart nimele {nimi} on edukalt registreeritud.")
            return
        elif is_pin_in_pintable == True and is_user_registered == False:
            command_queue.put(("REGISTREERI_PINNKOODI_ALUSEL", None))
            vastus = reply_queue.get(60)
            if vastus == True:
                GUI_message(f"Viipa kiipkaarti kasutaja {nimi} registreerimiseks.", show_button=False)
                nfc_input = hardware_handler.get_nfc()
                IsinDB, kasutu_muutuja = database_handler.checkuser(nfc_input)
                Empty_reply_queue()
                if IsinDB == True:
                    GUI_message("Kaart on juba registreeritud mõnele kasutajale")
                    Oota_kasutaja_kinnitust(15)
                else:
                    database_handler.create_new_user(nfc_input, pinnkood)
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
# Printimisi peavad handlema teised funktsiooni ja lõpuks drawer.py
def main_loop():
    global command_queue, reply_queue, _gui_proc
    command_queue = multiprocessing.Queue()
    reply_queue = multiprocessing.Queue()
    _gui_proc = multiprocessing.Process(target=drawer.run_touchscreen, args=(command_queue, reply_queue))
    _gui_proc.start()

    while True:
        Empty_reply_queue()
        GUI_default()
        valik = reply_queue.get()  # Ootab, kuni kasutaja vajutab ekraanil midagi kas
        """LOGI SISSE - kasutaja saab jooke väljastada või tagastada
           LOGIN_SEADED - kasutaja siseneb kontohalduse menüüsse kust saab vaadata võetud jookide seisu ja uut kaarti regada
           KAOTATUD KAART - kasutaja registreerib uue pinkoodi alusel"""
            
        if valik == "LOGI_SISSE":
            #Ootab  handlerilt nfc inputi
            nfc_input = hardware_handler.get_nfc(check_for_cancel)
            if nfc_input is None:
                continue
            print(f"DEBUG: Loetud NFC tag {nfc_input}")
            #Db handler kontrollib kas nfc uid on andmebaasis. kui jah tagastab IsinDB = True, kui ei False ja nimi
            IsinDB, nimi = database_handler.checkuser(nfc_input)
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
            #Küsime kasutajalt kas tahab registreerida uue kasutaja mis vastab nfc uid-le. Ootame vastuseks True/False ja pinnkoodi
                vastus, pinnkood = GUI_registreerimise_küsimine()
            
                if vastus == True:
                    pinnkood = int(pinnkood)
                    
                    is_pin_in_pintable =  database_handler.check_pin_code_dict(pinnkood) #kontrollib kas pin on andmebaasis
                    is_user_registered = database_handler.is_user_registered(pinnkood) #kontrollib kas pin on juba registreeritud kasutajale
                    if is_pin_in_pintable == True:
                        if is_user_registered == True:
                            logging.info("Kasutaja üritas registreerida juba registreeritud PIN-koodi.")
                            Empty_reply_queue()
                            GUI_message("See PIN on juba registreeritud kiipkaardile, uue kaardi registreerimiseks valige Kontohaldus avaekraanilt")
                            Oota_kasutaja_kinnitust(30)
                            continue 
                        else:
                            database_handler.create_new_user(nfc_input, pinnkood) #annab funktsioonile sisse nfc uid ja sisestatud pinnkoodi ja loob uue kasutaja
                            found, nimi = database_handler.nime_kaeve_pintabelist(pinnkood) #kaevab pintabelist nime mis vastab pinnkoodile
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
            vastus = reply_queue.get()
            if vastus == "UUS_KAART": #kui kasutaja tahab uuendada kaarti ja on juba regatud
                uus_kaart(True, nimi, nfc_input)
            else:
                continue
        elif valik == "KAOTATUD_KAART": 
            uus_kaart(False, None, None)
        elif valik == "UUS_KONTO":
            Empty_reply_queue()
            command_queue.put(("UUE_KONTO_REGAMINE_PINNKOODIGA", None))
            vastus = reply_queue.get()
            pinnkood = vastus
            if vastus == "CANCEL":
                pass
            else:
                is_pin_in_pintable =  database_handler.check_pin_code_dict(pinnkood) #kontrollib kas pin on andmebaasis
                is_user_registered = database_handler.is_user_registered(pinnkood) #kontrollib kas pin on juba registreeritud kasutajale
                if is_pin_in_pintable == True:
                    if is_user_registered == True:
                        logging.info("Kasutaja üritas registreerida juba registreeritud PIN-koodi.")
                        Empty_reply_queue()
                        GUI_message("See PIN on juba registreeritud kiipkaardile, uue kaardi registreerimiseks valige Kontohaldus avaekraanilt")
                        Oota_kasutaja_kinnitust(30)
                        continue 
                    else:
                        found, nimi = database_handler.nime_kaeve_pintabelist(pinnkood) #kaevab pintabelist nime mis vastab pinnkoodile
                        GUI_message(f"Tere, {nimi}! Viipa kiipkaarti kasutaja registreerimiseks", show_button=False)
                        nfc_input = hardware_handler.get_nfc()
                        database_handler.create_new_user(nfc_input, pinnkood) #annab funktsioonile sisse nfc uid ja sisestatud pinnkoodi ja loob uue kasutaja
                        
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
            nfc_input = hardware_handler.get_nfc(check_for_cancel)
            
            if nfc_input:
                is_in_db, name = database_handler.checkuser(nfc_input)
                if is_in_db and name == "ADMIN":
                    admin_loop()
                else:
                    GUI_message("Vale kaart")
                    Oota_kasutaja_kinnitust(3)
            # If nfc_input is None (cancelled via button), loop restarts automatically


#Joogi väljastuse plokk
def joogi_väljastus(nfc_input):
    nfc_input = nfc_input
    GUI_ukse_avamine("1")
    time.sleep(1)  # Näita ukse avamise ekraani 4 sekundit
    #Küsib handlerilt hetkekaalu
    hetke_kaal = hardware_handler.get_wheight()
    

    #Avab ukse
    hardware_handler.Ukse_avaja()
    

    #poe ostukorvi vaade vmidagi. Ma ka ei tea enam
    GUI_live_cart([])

     #Siia salvestub list jookidest mis skännitakse.
    scanned_items_info = []
    scanned_barcodes = [] #See on list triipkoodidest
    #Kapi sisese LCD tühjendus ja sõnumi kuvamine
    lcd.clear()
    lcd.show_message("Skaneeri tooted...")

    #LOOP mis käib nii kaua kuni kapi uks on lahti.
    while hardware_handler.is_door_open(): #kui isdooropen tagastab True on uks lahti False siis kinni
        barcode_to_process = None
        try:
            # Check for messages from GUI (non-blocking)
            message = reply_queue.get_nowait()
            logging.info(f"MAIN-LOOP: Got message from reply_q: {message}")

            if isinstance(message, str) and message.startswith("BARCODE:"):
                barcode_to_process = message.replace("BARCODE:", "", 1)

        except queue.Empty:
            # No message, do nothing
            pass

        if barcode_to_process:
            logging.info(f"MAIN-LOOP: Processing as barcode: {barcode_to_process}")
            is_in_db, drink_info = database_handler.get_drink_info(barcode_to_process)

            if is_in_db == False:
                lcd.show_message("Toodet pole nimekirjas")
                time.sleep(1) # Show message briefly
                lcd.clear()
                lcd.show_message("Skaneeri tooted...")
                continue # Skip to next loop iteration
            
            # This part only runs for valid barcodes
            scanned_barcodes.append(barcode_to_process) 
            scanned_items_info.append(drink_info)
            GUI_live_cart(scanned_items_info)
            print(f"DEBUG: {scanned_items_info}")
            
            count = scanned_items_info.count(drink_info)
            lcd.show_message(f"{drink_info} X{count}")
            time.sleep(1) # Show message briefly
            lcd.clear()
            lcd.show_message("Skaneeri tooted...")
            
        # Väike paus, et tsükkel ei koormaks protsessorit
        time.sleep(0.05)


    # 3. Tsükkel lõppes (Uks pandi kinni)
    # Kood jõuab siia hetkel, kui hardware_handler.is_door_open() tagastab False
    
    
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
        final_counts = reply_queue.get(timeout=300) # 5 min timeout
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
    database_handler.log_user_taken_drinks(nfc_input, scanned_barcodes)
    database_handler.keep_stock(scanned_barcodes, "taken")
    # 5. Arvuta uus kaal-- OOTAB veel implementeerimist
    lõpp_kaal = hardware_handler.get_wheight()
    kaalu_vahe = hetke_kaal - lõpp_kaal
    print(f"---Kaalu muutus: {kaalu_vahe}g----")
    
    # Tühjenda LCD uueks kasutajaks
    lcd.clear()
    
    # (Funktsioon lõppeb ja main_loop läheb tagasi algusesse, ootama uut NFC-d)   
    Empty_reply_queue()
    Empty_command_queue()
    return


def joogi_tagastus(nfc_input):

    #kasutja id 
    nfc_input = nfc_input

    #Küsib handlerilt hetkekaalu
    hetke_kaal = hardware_handler.get_wheight()
    
    # Fetch unreturned drinks before opening the door
    unreturned_drinks = database_handler.get_unreturned_drinks(nfc_input)
    
    GUI_ukse_avamine("2", unreturned_drinks)
    Oota_kasutaja_kinnitust(30)
   
    hardware_handler.Ukse_avaja()

    #Reklaam samal ajal kui uks lahti
    GUI_live_cart([])

     #Siia salvestub jookide nimikiri mis skännitakse. See on list jookdie NIMEDEST
    scanned_items_info = []
    scanned_barcodes = [] #See on list triipkoodidest
    #Kapi sisese LCD tühjendus ja sõnumi kuvamine
    lcd.clear()
    lcd.show_message("Skaneeri tooted...")

    #LOOP mis käib nii kaua kuni kapi uks on lahti.
    while hardware_handler.is_door_open(): #kui isdooropen tagastab True on uks lahti False siis kinni
        barcode_to_process = None
        try:
            # Check for messages from GUI (non-blocking)
            message = reply_queue.get_nowait()
            logging.info(f"MAIN-LOOP: Got message from reply_q: {message}")

            if isinstance(message, str) and message.startswith("BARCODE:"):
                barcode_to_process = message.replace("BARCODE:", "", 1)

        except queue.Empty:
            # No message, do nothing
            pass

        if barcode_to_process:
            logging.info(f"MAIN-LOOP: Processing as barcode: {barcode_to_process}")
            is_in_db, drink_info = database_handler.get_drink_info(barcode_to_process)

            if is_in_db == False:
                lcd.show_message("Toodet pole nimekirjas")
                time.sleep(1) # Show message briefly
                lcd.clear()
                lcd.show_message("Skaneeri tooted...")
                continue # Skip to next loop iteration
            
            # This part only runs for valid barcodes
            scanned_barcodes.append(barcode_to_process) 
            scanned_items_info.append(drink_info)
            GUI_live_cart(scanned_items_info)
            print(f"DEBUG: {scanned_items_info}")
            
            count = scanned_items_info.count(drink_info)
            lcd.show_message(f"{drink_info} X{count}")
            time.sleep(1) # Show message briefly
            lcd.clear()
            lcd.show_message("Skaneeri tooted...")
            
        # Väike paus, et tsükkel ei koormaks protsessorit
        time.sleep(0.05)

    # 3. Tsükkel lõppes (Uks pandi kinni)
    # Kood jõuab siia hetkel, kui hardware_handler.is_door_open() tagastab False
    
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
        final_counts = reply_queue.get(timeout=300)
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
    database_handler.log_user_returned_drinks(nfc_input, scanned_barcodes)
    database_handler.keep_stock(scanned_barcodes, "returned")
    # 5. Arvuta uus kaal-- OOTAB veel implementeerimist
    lõpp_kaal = hardware_handler.get_wheight()
    kaalu_vahe = hetke_kaal - lõpp_kaal
    print(f"---Kaalu muutus: {kaalu_vahe}g----")
    
    # 6. Korista ja lõpeta
    
    # Tühjenda LCD uueks kasutajaks
    lcd.clear()
    
    Empty_reply_queue()
    # (Funktsioon lõppeb ja taastab kontrolli main_loopile)
    return


   

#KOOOD ALGAB SIIT 
#Käivitame drawreri eraldi protsessina

if __name__ == "__main__":
    try:
        main_loop()
    finally:
        if _gui_proc is not None and _gui_proc.is_alive():
            _gui_proc.terminate()
