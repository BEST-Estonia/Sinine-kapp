# UI Screen Flow

This document maps the current touchscreen flow from:

- [sinine_kapp/app/controller.py](/home/skpi/Sinine-kapp/Sinine-kapp/sinine_kapp/app/controller.py)
- [sinine_kapp/ui/touchscreen.py](/home/skpi/Sinine-kapp/Sinine-kapp/sinine_kapp/ui/touchscreen.py)

The controller owns the cabinet logic. The touchscreen process only shows screens, waits for local UI input, and sends replies back through `reply_queue`.

```mermaid
flowchart LR
    Controller[controller.py<br/>main_loop and workflows]
    Queue[command_queue]
    Router[run_touchscreen<br/>command router]
    Screen[Current screen class]
    Reply[reply_queue]

    Controller --> Queue --> Router --> Screen
    Screen --> Reply --> Controller
```

## Main Menu And Login

```mermaid
flowchart TD
    Default[DEFAULT_SCREEN<br/>Main menu]

    Default -- "Joogi valjastus / tagastus<br/>LOGI_SISSE" --> LoginNfc[NFC login wait]
    LoginNfc -- "Known user" --> Choice[VALIKUVAADE<br/>Take or return?]
    LoginNfc -- "Unknown card" --> RegisterQuestion[REGISTREERIMINE<br/>Register card?]

    RegisterQuestion -- "No / timeout" --> MainMessage[MESSAGE]
    RegisterQuestion -- "Yes + PIN" --> PinCheck{PIN valid and unused?}
    PinCheck -- "Yes" --> Registered[KASUTAJA_REGISTREERITUD]
    PinCheck -- "No" --> PinError[MESSAGE<br/>PIN error]

    Choice -- "1<br/>Vota jook" --> TakeFlow[[Drink Take Flow]]
    Choice -- "2<br/>Tagasta jook" --> ReturnFlow[[Drink Return Flow]]
    Choice -- "Cancel / timeout" --> Default

    MainMessage --> Default
    Registered --> Default
    PinError --> Default
```

## Account And Card Management

```mermaid
flowchart TD
    Default[DEFAULT_SCREEN<br/>Main menu]
    Options[DEFAULT_SCREEN<br/>options state]

    Default -- "Admin / settings button<br/>KONTOHALDUS" --> Options

    Options -- "Logi sisse seadetesse<br/>LOGIN_SEADED" --> AccountNfc[NFC account login]
    AccountNfc -- "Known user" --> Account[KONTOHALDUS]
    AccountNfc -- "Unknown user" --> AccountError[MESSAGE]
    Account -- "UUS_KAART" --> NewCardLogged[UUS_KAART<br/>logged-in replacement]
    NewCardLogged --> AccountDone[MESSAGE]

    Options -- "Kaotasin kaardi<br/>KAOTATUD_KAART" --> LostCard[KAOTATUD_KAART]
    LostCard -- "PIN submitted" --> LostPinCheck{PIN state}
    LostPinCheck -- "Registered user" --> ScanReplacement[MESSAGE<br/>Viipa uut kaarti]
    LostPinCheck -- "PIN exists, not registered" --> RegisterByPin[REGISTREERI_PINNKOODI_ALUSEL]
    LostPinCheck -- "Not found / cancel" --> LostError[MESSAGE]

    Options -- "Loo uus kasutaja<br/>UUS_KONTO" --> NewAccountPin[UUE_KONTO_REGAMINE_PINNKOODIGA]
    NewAccountPin -- "Valid unused PIN" --> ScanNewCard[MESSAGE<br/>Viipa kiipkaarti]
    NewAccountPin -- "Invalid / used / cancel" --> NewAccountError[MESSAGE]
    ScanNewCard --> Registered[KASUTAJA_REGISTREERITUD]

    Options -- "Tagasi" --> Default

    AccountError --> Default
    AccountDone --> Default
    ScanReplacement --> Default
    RegisterByPin --> Default
    LostError --> Default
    Registered --> Default
    NewAccountError --> Default
```

## Drink Take Flow

```mermaid
flowchart TD
    Start[[joogi_valjastus]]
    OpenDoor[UKSE_AVAMINE_VOTMINE<br/>Open door prompt]
    EnableScan[ENABLE_BARCODE_SCANNING<br/>state command]
    LiveCart[LIVE_CART<br/>updates while door is open]
    DisableScan[DISABLE_BARCODE_SCANNING<br/>state command]
    Review[CART_REVIEW<br/>confirm final counts]
    Taken[VÄLJASTATUD_JOOGID<br/>summary]
    Default[DEFAULT_SCREEN]

    Start --> OpenDoor
    OpenDoor --> EnableScan
    EnableScan --> LiveCart
    LiveCart -- "BARCODE events while door open" --> LiveCart
    LiveCart -- "Door closes" --> DisableScan
    DisableScan --> Review
    Review -- "Confirm / timeout" --> Taken
    Taken --> Default
```

## Drink Return Flow

```mermaid
flowchart TD
    Start[[joogi_tagastus]]
    ReturnPrompt[UKSE_AVAMINE_TAGASTAMINE<br/>Shows unreturned drinks]
    EnableScan[ENABLE_BARCODE_SCANNING<br/>state command]
    LiveCart[LIVE_CART<br/>updates while door is open]
    DisableScan[DISABLE_BARCODE_SCANNING<br/>state command]
    Review[CART_REVIEW<br/>confirm final counts]
    Returned[TAGASTATUD_JOOGID<br/>summary]
    Default[DEFAULT_SCREEN]

    Start --> ReturnPrompt
    ReturnPrompt -- "Jatka / timeout" --> EnableScan
    EnableScan --> LiveCart
    LiveCart -- "BARCODE events while door open" --> LiveCart
    LiveCart -- "Door closes" --> DisableScan
    DisableScan --> Review
    Review -- "Confirm / timeout" --> Returned
    Returned --> Default
```

## Admin Flow

```mermaid
flowchart TD
    Default[DEFAULT_SCREEN<br/>Main menu]
    AdminNfc[MESSAGE<br/>Viipa admin kiipi]
    AdminCheck{NFC name == ADMIN?}
    Admin[ADMIN<br/>Admin menu]

    Default -- "ADMIN" --> AdminNfc
    AdminNfc --> AdminCheck
    AdminCheck -- "Yes" --> Admin
    AdminCheck -- "No" --> WrongCard[MESSAGE<br/>Vale kaart]

    Admin -- "BACK" --> Default

    Admin -- "PRODUCT_NAME" --> ScanFirst[MESSAGE<br/>Skanni uue toote triipkood]
    ScanFirst -- "Barcode #1 read" --> ScanSecond[MESSAGE<br/>Skanni uuesti kontrolliks]
    ScanFirst -- "Timeout" --> BarcodeTimeout[MESSAGE<br/>Triipkoodi ei leitud]
    ScanSecond -- "Codes match" --> Added[MESSAGE<br/>Toode lisatud]
    ScanSecond -- "Codes mismatch" --> Mismatch[MESSAGE<br/>Koodid ei uhti]

    Added --> Admin
    BarcodeTimeout --> Admin
    Mismatch --> ScanFirst

    Admin -- "REMOVE_PRODUCT" --> RemoveList[REMOVE_PRODUCT_LIST]
    RemoveList -- "DELETE_PRODUCT" --> Removed[MESSAGE<br/>Toode eemaldatud]
    RemoveList -- "BACK" --> Admin
    Removed --> RemoveList

    WrongCard --> Default
```

## Screen Command Reference

| Command | Screen / action | Notes |
| --- | --- | --- |
| `DEFAULT` | `DEFAULT_SCREEN` | Main menu and secondary account options state. |
| `VALIKUVAADE` | `VALIKUVAADE` | User chooses drink take or drink return after NFC login. |
| `UKSE_AVAMINE_VÕTMINE` | `UKSE_AVAMINE_VÕTMINE` | Door prompt before taking drinks. |
| `UKSE_AVAMINE_TAGASTAMINE` | `UKSE_AVAMINE_TAGASTAMINE` | Door prompt before returning drinks. |
| `LIVE_CART` | `LIVE_CART` | Runtime cart display while the door is open and barcodes are scanned. |
| `CART_REVIEW` | `CART_REVIEW` | Final editable/confirmable counts after door close. |
| `VÄLJASTATUD_JOOGID` | `VÄLJASTATUD_JOOGID` | Summary after taking drinks. |
| `TAGASTATUD_JOOGID` | `TAGASTATUD_JOOGID` | Summary after returning drinks. |
| `REGISTREERIMINE` | `REGISTREERIMINE` | Unknown card registration prompt. |
| `KASUTAJA_REGISTREERITUD` | `KASUTAJA_REGISTREERITUD` | Registration success screen. |
| `KONTOHALDUS` | `KONTOHALDUS` | Logged-in account management screen. |
| `UUS_KAART` | `UUS_KAART` | New/replacement card flow for logged-in user. |
| `KAOTATUD_KAART` | `KAOTATUD_KAART` | Lost card PIN flow. |
| `REGISTREERI_PINNKOODI_ALUSEL` | `REGISTREERI_PINNKOODI_ALUSEL` | Existing PIN registration flow. |
| `UUE_KONTO_REGAMINE_PINNKOODIGA` | `UUE_KONTO_REGAMINE_PINNKOODIGA` | New account PIN flow. |
| `ADMIN` | `ADMIN` | Admin product add/remove menu. |
| `REMOVE_PRODUCT_LIST` | `REMOVE_PRODUCT_LIST` | Admin product deletion list. |
| `MESSAGE` | `MESSAGE` | Shared status/error/wait screen. |
| `REKLAAM` | `REKLAAM` | Defined in UI, but not part of the current main controller flow. |
| `ENABLE_BARCODE_SCANNING` | state command | Enables barcode reader events inside the UI process. |
| `DISABLE_BARCODE_SCANNING` | state command | Disables barcode reader events inside the UI process. |
| `STOP` | process control | Exits the touchscreen process. |

## Cleanup Notes For The UI Rework

- `DEFAULT_SCREEN` currently handles both the main menu and an internal `options` state. Splitting those into two screens would make routing clearer.
- `MESSAGE` is doing several jobs: status screen, error screen, confirmation screen, and NFC/barcode wait screen. It may be worth separating passive status from actionable prompts.
- `LIVE_CART` and `CART_REVIEW` are shared by take and return flows, which is good. They should probably stay generic and receive a mode label from the controller.
- Barcode scanning is controlled by non-screen commands. That is reasonable, but it should be documented clearly because it affects input behavior without changing screens.
- `REKLAAM` is still implemented but appears unused by the current main flow.
- The admin product flow is still controller-heavy. Later cleanup could move product add/remove orchestration into a small admin workflow module.
