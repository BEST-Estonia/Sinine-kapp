
#mockup databaasid

#pinnkoodi list kus kõik bestikad ja pinnkood kaardi regamiseks
pin_code_dict = {
    "1111": "Karl registreerija"
}

#REgistreeritud kasutajate kaardi uid ja nimi
registered_user_dict = {
    "11111111": "Peeter Termomeeter",
    "22222222": "Mari Karu"
}


#Jookide dictionary triipkood ja joogi nimetus ning joogi kaal
drink_dict = {
    "123456789": ["Saku kuld 0.5L ", 0.7],
    "987654321": ["sommersby 0.33L", 0.3]
}





#Tsekib kas kasutaja on olemas
def checkuser(UID):
    if UID in registered_user_dict:
        name = registered_user_dict[UID]
        return "Y", name
    else:
        return "n", None

#tsekib kas jook on adnmebaasis, kui ei siis tagastab n kui ja siis y
def check_is_drink_in_db (barcode):
    if barcode in drink_dict:
        return "y"
    else:
        return "n"


#Barcodei alusel küsib dbst joogi nime ja suurust, kui jook on andmebaasis olemas
def get_drink_info(barcode):
    joogi_olemasolu = check_is_drink_in_db(barcode)
    if joogi_olemasolu == "y":
        drink_name = drink_dict[barcode][0]
        return joogi_olemasolu, drink_name
    else:
        return joogi_olemasolu, "Tühi"


#tekitab listi kõikides barcodedest ja teades user_id logib need andmebaasi
def log_user_taken_drinks(user_id, barcode):
    user_taken = []
    user_taken = user_taken.append(barcode)
    #SIIT edasi peaks tulema kood, mis loeb kokku joogid ja sisetab andmebaasi

#Loob uue kasutaja andmebaasi pinnkoodi ja nfcinputist saadud nfc id järgi
def create_new_user(nfc_input, pinnkood):
    name = pin_code_dict[pinnkood]
    registered_user_dict[nfc_input] = name


#Kontrollib kas kasutaja sisestatud pinnkood on pinnkoodi andmebaasis
#Võtab sisse kasutaja sisestatud pinnkoodi ja returnim y- on andmebaasis n- pole sellist adnmebaasis
def check_pin_code_dict(pinnkood):
    if pinnkood in pin_code_dict:
        return "y"
    else: 
        return "n"
    
def log_user_returned_drinks(user_id, barcode):
    user_returned = []
    user_returned = user_returned.append(barcode)