from collections import Counter
import time
import drawer
import hardware_handler
import database_handler
import lcd
import logging
import multiprocessing
import queue

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
        response = reply_queue.get(timeout)
        if response == True: 
            pass
    except queue.Empty:
        pass

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

def GUI_kasutaja_registreeritud(nimi):
    command_queue.put( ("KASUTAJA_REGISTREERITUD", nimi) )
    
#Ekraanivaade, mis kuvatakse kui pinnkoodile polnud andmebaasis vastet
def GUI_pinn_vale():
    drawer.Vale_pinnkood()

def GUI_message(message):
    command_queue.put( ("MESSAGE", message) )

def kontohaldus(): 
    nfc_input = hardware_handler.get_nfc()
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
            GUI_message(f"Kasutaja {nimi} leitud. Viipa uut kaarti registreerimiseks")
            uus_nfc = hardware_handler.get_nfc()
            database_handler.register_new_card(uus_nfc, nimi)
            GUI_message(f"Uus kaart nimele {nimi} on edukalt registreeritud.")
            return
        elif is_pin_in_pintable == True and is_user_registered == False:
            command_queue.put(("REGISTREERI_PINNKOODI_ALUSEL", None))
            vastus = reply_queue.get(60)
            if vastus == True:
                GUI_message(f"Viipa kiipkaarti kasutaja {nimi} registreerimiseks.")
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
            nfc_input = hardware_handler.get_nfc()
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
                        GUI_message(f"Tere, {nimi}! Viipa kiipkaarti kasutaja registreerimiseks")
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


#Joogi väljastuse plokk
def joogi_väljastus(nfc_input):
    nfc_input = nfc_input
    GUI_ukse_avamine("1")
    time.sleep(4)  # Näita ukse avamise ekraani 4 sekundit
    #Küsib handlerilt hetkekaalu
    hetke_kaal = hardware_handler.get_wheight()
    

    #Avab ukse
    hardware_handler.Ukse_avaja()
    

    #Reklaam samal ajal kui uks lahti
    GUI_reklaam()

     #Siia salvestub list jookidest mis skännitakse.
    scanned_items_info = []
    scanned_barcodes = [] #See on list triipkoodidest
    #Kapi sisese LCD tühjendus ja sõnumi kuvamine
    lcd.clear()
    lcd.show_message("Skaneeri tooted...")

    #LOOP mis käib nii kaua kuni kapi uks on lahti.
    while hardware_handler.is_door_open(): #kui isdooropen tagastab True on uks lahti False siis kinni
            
        barcode = hardware_handler.get_barcode_scan()
        
       #Kui barcode loetud
        if barcode:

            #saame databse handlerilt "n/y" vastuse kas jook on andmebaasis ja joogi info
            is_in_db, drink_info = database_handler.get_drink_info(barcode)
            
            # kui toode pole andmebaasis siis....
            #Kui toode on andmebaasis siis loop jätkub
            if is_in_db == False:
                lcd.show_message("Toodet pole nimekirjas")
                continue #hüppab tagasi loop algusse

            else:
                scanned_barcodes.append(barcode) 
                scanned_items_info.append(drink_info)
                print(f"DEBUG: {scanned_items_info}")
            # D. Uuenda LCD-ekraani
            
            lcd.show_message(drink_info) 
            
        # Väike paus, et tsükkel ei koormaks protsessorit
        time.sleep(0.05) 

    # 3. Tsükkel lõppes (Uks pandi kinni)
    # Kood jõuab siia hetkel, kui hardware_handler.is_door_open() tagastab False
    
    print("Uks suletud. Lõpetan sessiooni...")

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
    
    # Annab GUI_Võetud funktsioonile ette scannitud joogid. 
    # GUI_võetud() loendab üle mitu korda mis jooki võeti ja annab sõnastiku üle drawer.pyle
    # ja annab parameetrid ette drawer failile
    GUI_võetud(scanned_items_info)
    #Ootab, et kasutaja vajutaks jätka. timeout kui ei vajuta siis kood jätkub.
    Oota_kasutaja_kinnitust(30)
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
    GUI_reklaam()

     #Siia salvestub jookide nimikiri mis skännitakse. See on list jookdie NIMEDEST
    scanned_items_info = []
    scanned_barcodes = [] #See on list triipkoodidest
    #Kapi sisese LCD tühjendus ja sõnumi kuvamine
    lcd.clear()
    lcd.show_message("Skaneeri tooted...")

    #LOOP mis käib nii kaua kuni kapi uks on lahti.
    while hardware_handler.is_door_open(): #kui isdooropen tagastab True on uks lahti False siis kinni
        barcode = hardware_handler.get_barcode_scan()
        
       #Kui barcode loetud
        if barcode:

            #saame databse handlerilt "n/y" vastuse kas jook on andmebaasis ja joogi info
            is_in_db, drink_info = database_handler.get_drink_info(barcode)
            
            # kui toode pole andmebaasis siis....
            #Kui toode on andmebaasis siis loop jätkub
            if is_in_db == False:
                lcd.show_message("Toodet pole nimekirjas")
                continue #hüppab tagasi loop algusse

            else:
                scanned_barcodes.append(barcode) 
                scanned_items_info.append(drink_info)
                print(f"DEBUG: {scanned_items_info}")
            # D. Uuenda LCD-ekraani
            
            lcd.show_message(drink_info) 
            
        # Väike paus, et tsükkel ei koormaks protsessorit
        time.sleep(0.05) 

    # 3. Tsükkel lõppes (Uks pandi kinni)
    # Kood jõuab siia hetkel, kui hardware_handler.is_door_open() tagastab False
    
    print("DEBUG: Uks suletud. Lõpetan sessiooni...---")

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
    
    # Annab GUI_Võetud funktsioonile ette scannitud joogid. 
    # GUI_võetud() loendab üle mitu korda mis jooki võeti ja annab sõnastiku üle drawer.pyle
    # ja annab parameetrid ette drawer failile
    GUI_tagastatud(scanned_items_info)
    
    try:
        response = reply_queue.get(timeout=30)
        if response == True: 
            pass
    except queue.Empty:
        pass
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
