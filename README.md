Sinu ees on projekt SININE KAPP. 
KÄIVITAMINE
a. Loe rewuirements.txt ja installi vajalikud tarkvarad.
b. drawer.py failis run_touchscreen funktsioonis leia read ja asenda.
        screen = pygame.display.set_mode((800, 600))
        #screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        ↓↓↓↓↓↓↓↓↓↓↓↓↓           
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
c. ava terminal projekti kasutas ja kirjuta käsk py main.py
d. PROFIT! NAUDI!

Siin on lühidalt kirjeldaldut iga faili eesmärk ja seal peituvate funktsioonide ja klasside tööpõhimõtted. EEsmärk on hoida main.py lihtsasti loetav ja viia keerulised koodijupid muudesse failidesse sääraselt, et nad on lihtsasti ja modulaarselt kasutatavad. Kood on läbivalt kommenteeritud. Projekt jookseb multiprocessina. main.py on omaette protsess ja kõik mida kuvatakse ekraanil jookseb eraldi protsessi pealt.
kasutame kahte queue'd command_queue ja reply_queu
    command_queu on järjekord kuhu main.py lisab käske ja andmeid mida ekraan peab kuvama
    reply_queue on järjekord kuhu lisame kõik kasutaja inputi puuteekraanil, main.py'le lugemiseks

Programmi käivitamiseks jooksutada projekti kasutast py main.py

1. main.py
----------------------------------------------------------------------------------------
Lihtsalt loetav üleüldine loogika. Koosneb main_loop() joogi_väljastus(), joogi_tagastus() ja GUI_....() funktsioonidest.

    main_loop()
    While True loop mis jookseb kogaeg. Alustab kaks queued kuhu saab lisada käske ekraani jaoks ja teine queue, mille läbi saab kasutaja inputi lugeda.

    joogi_väljastus()
    Looogika selle kohta, mis toimub kui kasutaja valib väljastuse.

    joogi_tagastus()
    Pmst sama mis väljastus aga tagastamise loogika

    GUI_...() fubnktsioonid
    funktsioonid mis lisavad käske command_queue'sse. Nt command_queue.put( ("DEFAULT", None) ). Käsk peab olema TUPLET vormis. esimene lahter ütleb, mis ekraanipilti kuvada ja teine lahter on adnmete edastamiseks drawer.py koodile. draer.py funktsioon run_touchscreen loeb neid käske ja käivitab vastavlt sellele sobiva ekraanikuva.
    Kui andmeid edastada pole vaja siis jätta None

2. hardware_handler.py
----------------------------------------------------------------------------------------------------------------------------
See kood sisaldab funktsioone riistvaraga suhtlemise jaoks. Suuhtleb riistvaraga, tegeleb timeoutidega ja edastab infot main.py'le. Hoiab main.py loetavana, sest kogu keeruline riistvara käsitlus on selles failis.
Kui main.py loogika vajab midagi järgnevast loetelust:
    qr_koodi skänn
    kaal
    nfc input
    ...
    siis pöörduda selles failis olevate funktsioonide poole. Nt vaja NFC tagi siis pöörduda get_NFC() funktsiooni poole main.py's hardware_handler.get_NFC(). 

3. database_handler.py
----------------------------------------------------------------------------------------------------------------------------
Sisaldab funktsioone andmebaasiga suhtlemise jaoks. Adnmebaasiga suhtluse jaoks kutsumem välja funktsiooni sellest failist. Kasutab sqllite et querysi teha.

4. drawer.py
----------------------------------------------------------------------------------------------------------------------------
Kõik, mis puudutab puuteekraanile pildi kuvamist ja kasutaja inputi saamist ning quesse lisamist. koosneb run_touchscreen(command_q, reply_q) funktsioonist ja iga erineva kuva nt(tervitus_kuva, Joogiväljastus_kuva vahekuva) jaoks on eraldi 
Täpne ja põhjalik kasutusjuhend on Front_end_juhend.txt failis

class struktuur.

    run_touchscreen().
    Käivitab algul DEFAULT ekraani ja siis loeb command_queu'd. Vastavalt sellele käivitab sobiva ekraani klassi. Lisaks lisab reply_queue'sse kasutaja vastuse.

    class "......" 
    kogu loogika ekraanil kuvamiseks. Ekraani klassi ehitamisel saab kasutada ette määratud fonte, värve ja nupu loogikat mis on ui_components.py failis. 

5. ui_components.py
----------------------------------------------------------------------------------------------------------------------------
Sisaldab graafilise liidese komponente ("Toolbox").

    class Button
    Nupu objekt, mis tegeleb ise enda joonistamise ja vajutuse tuvastamisega. Võtab sisse asukoha, teksti, värvi ja käsu ID, mille tagastab vajutamisel.

6. styles.py
----------------------------------------------------------------------------------------------------------------------------
Sisaldab stiilide definitsioone ("The Look").

    class Colors, class FontManager
    Hoiab tsentraalselt värve ja fonte. `drawer.py` kasutab seda faili, et vältida igas punktsi eraldi värvi ja fondi kirjeldamist ja tagada ühtne disain (nt `fonts.header`, `Colors.GREEN`).

7. lcd.py
----------------------------------------------------------------------------------------------------------------------------
Tegeleb riistvaralise LCD ekraaniga suhtlemisega.

    Kasutatakse `main.py` poolt, et kuvada kasutajale jooksvat infot (nt "Skaneeri tooted..." või toote nime), samal ajal kui puuteekraan näitab reklaami või muud staatilist pilti.
    