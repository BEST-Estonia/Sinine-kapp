from collections import Counter
import time
import drawer
import hardware_handler
import database_handler
import lcd
import logging
import multiprocessing
import queue

# Global queues for GUI communication
_gui_proc = None
_command_queue = None
_reply_queue = None

def start_gui_handler():
    """Initialize the GUI process and queues. Call once at startup."""
    global _gui_proc, _command_queue, _reply_queue
    
    _command_queue = multiprocessing.Queue()
    _reply_queue = multiprocessing.Queue()
    _gui_proc = multiprocessing.Process(
        target=drawer.gui_handler,
        args=(_command_queue, _reply_queue),
        daemon=True
    )
    _gui_proc.start()
    logging.info("Started GUI handler process")

# Set up logging (kasutus: logging.debug .info .warning .error .critical)
logging.basicConfig(
    filename='main.log',  # Log file name
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


#DEFAULT SCREEN


def GUI_default():
    """
    Show the default welcome screen in the GUI process.
    Does NOT block main — just sends a command and returns immediately.
    """
    global _command_queue
    
    if _command_queue is None:
        logging.error("GUI handler not initialized")
        return
    
    cmd = {"cmd": "kuva_default_screen"}
    _command_queue.put(cmd)
    logging.info("Sent 'kuva_default_screen' command to GUI")



#Ekraanivaade, kus kuvatakse Tere ""NIMI" valik(võtan joogi/tagastan) 
# Võtab inputiks kasutaja nime et nimeliselt terviatada
#tagastab mis valiku kasutaja tegi 1-võtab jooki 2-tagastav
def GUI_valikuvaade(nimi):
    # 1. Create unique ID for this request
    reply_id = f"choice_{time.time()}"
    
    # 2. Send command (returns immediately, non-blocking)
    cmd = {
        "cmd": "kuva_valikuvaade",           # Tells drawer which screen to show
        "data": {"name": nimi},         # Data to display on screen
        "reply_id": reply_id,            # So we know which reply is ours
        "wait_reply": True
    }
    _command_queue.put(cmd)
    
    # 3. Wait for reply (blocking, but with timeout)
    try:
        reply = _reply_queue.get(timeout=30)
        if reply.get("reply_id") == reply_id:  # Make sure it's OUR reply
            return reply.get("result")         # Return 1 or 2
    except queue.Empty:
        return None  # Timeout

def GUI_ukse_avamine(action_type):
    """
    Fire-and-forget screen that shows door opening confirmation message.
    Does NOT block main or wait for reply.
    
    action_type: "take" or "return"
    """
    global _command_queue
    
    if _command_queue is None:
        logging.error("GUI handler not initialized")
        return
    
    cmd = {
        "cmd": "kuva_ukse_avamine",
        "data": {"action": action_type},
        "wait_reply": False
    }
    _command_queue.put(cmd)
    logging.info(f"Sent door opening screen command: {action_type}")

#ekraanivaade, mis kuvatakse samal ajal kui uks lahti
def GUI_reklaam():
    drawer.Reklaam()

#käivitab registreerimise küsimise drawery. ja returnib main loopile pinkoodi kui kasutaja otsustas regada
def GUI_registreerimise_küsimine():
    vastus, pinnkood = drawer.Regamise_küsimine()
    return vastus, pinnkood

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
    drawer.Võetud(drink_counts)

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
    drawer.Tagastatud(drink_counts)

#Kuvab draweri abil teksti "Kasutaja registreeritud"
def GUI_kasutaja_registreeritud():
    drawer.Kasutaja_regatud()

#Ekraanivaade, mis kuvatakse kui pinnkoodile polnud andmebaasis vastet
def GUI_pinn_vale():
    drawer.Vale_pinnkood()



#Main loop käivitab default ekraani vaate, jääb nfc inputi ootama ja otsustab kas minna edasi
#valiku või regamis ekraanile
#!!!!!!!! Iga print fn selles plokis on debuggimiseks ja ei kuvata lõpuks puuteekraanil.
# Printimisi peavad handlema teised funktsiooni ja lõpuks drawer.py
def main_loop():
    start_gui_handler()
    while True:

        GUI_default()

        #Ootab ardunio handlerilt nfc inputi
        nfc_input = hardware_handler.get_nfc()
        print(f"DEBUG: Loetud NFC tag {nfc_input}")
        #Db handler kontrollib kas nfc uid on andmebaasis. kui jah tagastab IsinDB = True kui ei False ja nimi
        IsinDB, nimi = database_handler.checkuser(nfc_input)
        if IsinDB == True:
            valik = GUI_valikuvaade(nimi) #Valiku vaade küsib kasutajalt kas tahan kapist võtta või kappi panna
            
            #Tagastab mis valisid antud juhul 1 Võtan kapist alksi 2 tagastan. 

            print(f"DEBUG: Valisid {valik}")
            if valik == "1":
                joogi_väljastus(nfc_input)  
            elif valik == "2":
                joogi_tagastus(nfc_input) 
            else:
                # Kui valik oli "Tühista" vms, ei tee me midagi
                # ja tsükkel algab automaatselt uuesti
                pass
            # --- LÕPP ---
    
        else: 
            #laseb GUI fnil joonistajal küsida kas tahad regada sest kaarti ei leitud. 
            # GUi väljastab kasutaja pinkoodi ja if statement laseb db_handleril luua uues kasutaja kui pinn olemas
            
            vastus, pinnkood = GUI_registreerimise_küsimine()
           
            if vastus == "y":
                pinnkood = int(pinnkood)
                is_pin_in_dict =  database_handler.check_pin_code_dict(pinnkood) #kontrollib kas pin on andmebaasis
                if is_pin_in_dict == True:
                    print("DEBUG ",  is_pin_in_dict)
                    database_handler.create_new_user(nfc_input, pinnkood) #annab funktsioonile sisse nfc uid ja sisestatud pinnkoodi ja loob uue kasutaja
                    GUI_kasutaja_registreeritud()
                    time.sleep(5)
                    continue
                else:
                    GUI_pinn_vale()

            #Kui kasutaja ei taha kontot regada siis loop jätkub default screeniga
            else:
                continue
            

#Joogi väljastuse plokk
def joogi_väljastus(nfc_input):
    print("Aa")
    GUI_ukse_avamine("1")
    time.sleep(4)
     # ootab 4 sekundit enne kui uske avab, et kasutaja jüuaks lugeda mis ta valis
    #kasutja id 
    nfc_input = nfc_input

    #Küsib handlerilt hetkekaalu
    hetke_kaal = hardware_handler.get_wheight()
    

    #Avab ukse
    hardware_handler.Ukse_avaja()

    #Reklaam samal ajal kui uks lahti
    GUI_default()

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
    
    print("Uks suletud. Lõpetan sessiooni...")

    # 4. Salvesta andmed andmebaasi
    # Anna kogu 'scanned_items' list ja 'nfc_input' andmebaasile
    database_handler.log_user_taken_drinks(nfc_input, scanned_barcodes)
    
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
    GUI_võetud(scanned_items_info)
    
    # (Funktsioon lõppeb ja main_loop läheb tagasi algusesse, ootama uut NFC-d)

    #Ootab enne main loopi algust, et kasutaja jüuaks lugeda mis võttis
    time.sleep(15)
    main_loop()


def joogi_tagastus(nfc_input):

    #kasutja id 
    nfc_input = nfc_input

    #Küsib handlerilt hetkekaalu
    hetke_kaal = hardware_handler.get_wheight()
    
    #ootab natuke enne kui ukse avab
    time.sleep(2)

    #Avab ukse
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
    
    #Ootab enne main loopi algust, et kasutaja jüuaks lugeda mis võttis
    time.sleep(15)
    # (Funktsioon lõppeb ja main_loop läheb tagasi algusesse, ootama uut NFC-d)
    main_loop()











    




#KOOOD ALGAB SIIT 
#Järgnev süntaks on vajalik selleks et drawer saask töötada eraldi protsessina 
# ja ei takistaks main programmi tööd


if __name__ == "__main__":
    try:
        main_loop()
    finally:
        if _gui_proc is not None and _gui_proc.is_alive():
            _gui_proc.terminate()









