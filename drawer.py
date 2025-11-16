import time


#KUVAB DEFAULT TERVITUS EKRAANI
def Default_screen():
    print("---Praegu on kuvatud default ekraan\n Viipa nfc kaarti---")
   


#KUI kasutaja on sisse logitud siis kuvab valikut (VÕTAN JOOGI või TAGASTAN)
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