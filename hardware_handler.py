"""
See fail tegeleb riistvara suhtlusega.
get_nfc() loeb nfc lugejat ja returnib saadud vastuse
Mai viitsi rohkem edasi kirjutada

"""


import time

#küsib nfc tagi
def get_nfc():
   
    print("")
    ID = input("DEBUG SISesta klaviatuuril nfc---")
    return ID

#Küsib kaalu näitu
def get_wheight():
    time.sleep(1)
    kaal = 40.6
    return kaal


#avab ukse
def Ukse_avaja():
    return 0


#Sebib barcodei
def get_barcode_scan():
    barcode = input("---SISESTA TRIIPKOOD--- →→→ ")
    return barcode



#muutujad simuleerimaks kaua uks lahti on
_door_timer_start = None
_DOOR_DURATION = 8

def is_door_open():
    """
    Simuleerib ust. Esimesel käivitamisel "avab" ukse 10 sekundiks.
    Järgnevatel kordadel kontrollib, kas aeg on täis.
    """
    global _door_timer_start
    
    # 1. Kui taimer ei jookse (on None), siis see on esimene kontroll.
    #    Käivita taimer.
    if _door_timer_start is None:
    
        _door_timer_start = time.time() # Salvesta algusaeg
        return True # Ütleme tsüklile, et uks on lahti

    # 2. Taimer juba jookseb. Kontrollime, kas aeg on täis.
    elapsed_time = time.time() - _door_timer_start
    
    if elapsed_time < _DOOR_DURATION:
        # 3. Aeg POLE veel täis. Uks on endiselt lahti.
      
        return True
    else:
        # 4. Aeg ON täis. "Sulgeme" ukse.
      
        _door_timer_start = None # Nullime taimeri järgmiseks korraks
        return False
