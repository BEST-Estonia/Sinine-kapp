from collections import Counter
import time
import drawer
import hardware_handler
import database_handler
import lcd
import logging
import multiprocessing


# Set up logging (kasutus: logging.debug .info .warning .error .critical)
logging.basicConfig(
    filename='main.log',  # Log file name
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


#DEFAULT SCREEN
# We start the drawer.Default_screen in a separate process so the GUI remains
# active while the main loop continues. All process-management changes are
# contained inside this function per your request.
_gui_proc = None
_gui_stop_event = None

def GUI_default():
    """
    Ensure the default GUI screen is running in a separate process.
    If the GUI process is already running, return immediately.
    Otherwise, start a multiprocessing.Process that runs drawer.Default_screen(stop_event).
    """
    global _gui_proc, _gui_stop_event

    # If already running and alive, do nothing
    if _gui_proc is not None and _gui_proc.is_alive():
        return

    # Create a stop Event that can be shared with the child process
    _gui_stop_event = multiprocessing.Event()

    # Start the GUI process. Pass the stop event so the GUI can exit when we set it.
    _gui_proc = multiprocessing.Process(target=drawer.Default_screen, args=(_gui_stop_event, None), daemon=True)
    _gui_proc.start()
    logging.info("Started GUI default screen process")

def GUI_stop_default(timeout=3):
    """Signal the GUI default process to stop and wait up to `timeout` seconds."""
    global _gui_proc, _gui_stop_event
    try:
        if _gui_stop_event is not None:
            _gui_stop_event.set()
        if _gui_proc is not None:
            _gui_proc.join(timeout)
            if _gui_proc.is_alive():
                _gui_proc.terminate()
                logging.warning("Terminated GUI default process after timeout")
    except Exception as e:
        logging.error(f"Error stopping GUI process: {e}")

#Ekraanivaade, kus kuvatakse Tere ""NIMI" valik(võtan joogi/tagastan) 
# Võtab inputiks kasutaja nime et nimeliselt terviatada
#tagastab mis valiku kasutaja tegi 1-võtab jooki 2-tagastav
def GUI_valikuvaade(nimi):
    valik = drawer.Valiku_vaade(nimi)
    return valik

#VAHEekraan, mis kuvatakse peale seda kui use on vajutanud VÕTAN Joogi. Kuvab "Valisid võtan joogi"
def GUI_võtmine():
    drawer.Võtmine()

#sama mis eelmine aga tagastamsie kohta
def GUI_tagastamine():
    drawer.Tagastamine()

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



#Main loop käivitab drfault ekraani vaate, jääb nfc inputi ootama ja otsustab kas minna edasi
#valiku vüi regamis ekraanile
#!!!!!!!! Iga print fn selles plokis on debuggimiseks ja ei tohiks kõppkoodis olla.
# Printimisi peavad handlema teised funktsiooni ja lõpuks drawer.py
def main_loop():
    while True:

        GUI_default()

        #Ootab ardunio handlerilt nfc inputi
        nfc_input = hardware_handler.get_nfc()
        print(f"DEBUG: Loetud NFC tag {nfc_input}")
        #Db handler kontrollib kas uid on andmebaasis ´, tagast yvõi n kui pole
        IsinDB, nimi = database_handler.checkuser(nfc_input)
        if IsinDB == True:
            valik = GUI_valikuvaade(nimi)
            
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
            # GUi väljastab kasutaja pinkoodi ja if statement laseb db_ghandleril luua uues kasutaja kui pinn olemas
            #kui pin ei matchi prompti pini uuesti
            vastus, pinnkood = GUI_registreerimise_küsimine()
           
            if vastus == "y":
                pinnkood = int(pinnkood)
                is_pin_in_dict =  database_handler.check_pin_code_dict(pinnkood) #kontrollib kas pin on valid
                if is_pin_in_dict == True:
                    print("DEBUG ",  is_pin_in_dict)
                    database_handler.create_new_user(nfc_input, pinnkood)
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

    #kasutja id 
    nfc_input = nfc_input

    #Küsib handlerilt hetkekaalu
    hetke_kaal = hardware_handler.get_wheight()
    
    #käsib GUIL_vütmine kuvada vaheekraani enne ukse avamist
    GUI_võtmine()

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
    
    print("Uks suletud. Lõpetan sessiooni...")

    # 4. Salvesta andmed andmebaasi
    # Anna kogu 'scanned_items' list ja 'nfc_input' andmebaasile
    database_handler.log_user_taken_drinks(nfc_input, scanned_barcodes)
    
    # 5. Arvuta uus kaal (valikuline, aga hea varguse tuvastamiseks)
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
    GUI_tagastamine()

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
    
    # 5. Arvuta uus kaal (valikuline, aga hea varguse tuvastamiseks)
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
        # Ensure GUI process is stopped when program exits
        try:
            GUI_stop_default()
        except Exception:
            pass

#KUi valitud võtmine siis kõivitub plokk joogi väljastuse jaoks









