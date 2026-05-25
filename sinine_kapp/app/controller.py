"""Main application controller for the cabinet.

This module owns the cabinet workflow. It starts the touchscreen process,
talks to hardware, calls the portal API, and coordinates the app by passing
screen commands through ``command_queue`` and reading UI replies from
``reply_queue``.
"""

from collections import Counter
import atexit
import logging
import multiprocessing
import queue
import signal
import time
from typing import Any

from ..devices import hardware
from ..devices.lcd import LCD
from ..paths import LOG_FILE
from ..services import database
from ..ui import touchscreen


# ---------------------------------------------------------------------------
# Process-wide state
# ---------------------------------------------------------------------------

APP_EXIT = "__APP_EXIT__"
lcd = None
_gui_proc = None
command_queue = None
reply_queue = None
_shutting_down = False


# Log to the repo-level main.log file. Use logging.* instead of print for
# anything that should survive kiosk/autostart runs.
logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


# ---------------------------------------------------------------------------
# Startup, shutdown, and cleanup
# ---------------------------------------------------------------------------

def _require_lcd():
    if lcd is None:
        raise RuntimeError("LCD is not initialized")
    return lcd


def _command_queue() -> Any:
    """Return the initialized UI command queue."""
    if command_queue is None:
        raise RuntimeError("GUI command queue is not initialized")
    return command_queue


def _reply_queue() -> Any:
    """Return the initialized UI reply queue."""
    if reply_queue is None:
        raise RuntimeError("GUI reply queue is not initialized")
    return reply_queue


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
            _command_queue().put(("STOP", None))
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


def _check_startup_database_connection():
    ok, details = database.check_connection()

    if ok:
        logging.info("STARTUP CHECK: database connection OK - %s", details)
        try:
            _require_lcd().show_message("DB OK")
            time.sleep(1)
            _require_lcd().clear()
        except Exception:
            logging.exception("Failed to show startup DB OK message on LCD")
        return

    logging.error("STARTUP CHECK: database connection FAILED - %s", details)
    try:
        _require_lcd().show_message("DB viga")
        time.sleep(2)
        _require_lcd().clear()
    except Exception:
        logging.exception("Failed to show startup DB error message on LCD")


# ---------------------------------------------------------------------------
# Queue helpers
# ---------------------------------------------------------------------------

def _read_reply(timeout=None):
    """Read one message from the UI process and convert app-exit into SystemExit."""
    if timeout is None:
        message = _reply_queue().get()
    else:
        message = _reply_queue().get(timeout=timeout)

    if message == APP_EXIT:
        raise SystemExit

    return message


def Empty_reply_queue():
    """Drop stale UI replies before starting a new workflow step."""
    try:
        while True:
            message = _reply_queue().get_nowait()
            if message == APP_EXIT:
                raise SystemExit
    except queue.Empty:
        pass


def Empty_command_queue():
    """Drop stale UI commands when returning to the main menu."""
    try:
        while True:
            _command_queue().get_nowait()
    except queue.Empty:
        pass


def Oota_kasutaja_kinnitust(timeout):
    """Wait for a generic confirmation button, but continue after timeout."""
    try:
        response = _read_reply(timeout=timeout)
        if response == True: 
            pass
    except queue.Empty:
        pass


def wait_for_barcode_from_queue(timeout):
    """Wait for a barcode message while ignoring unrelated UI replies."""
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
    """Cancel callback passed into blocking NFC reads."""
    try:
        msg = _reply_queue().get_nowait()
        if msg == APP_EXIT:
            raise SystemExit
        if msg == "tagasi":
            return True
        if msg is True: # Handle "Jätka" button from MESSAGE screen as cancel
            return True
    except queue.Empty:
        pass
    return False


def check_for_admin_cancel():
    """Admin NFC waits only treat the explicit back button as cancel."""
    try:
        msg = _reply_queue().get_nowait()
        if msg == APP_EXIT:
            raise SystemExit
        if msg == "tagasi":
            return True
        if msg is not None:
            logging.info("Admin auth: ignoring non-cancel UI reply while waiting for NFC: %r", msg)
    except queue.Empty:
        pass
    return False


# ---------------------------------------------------------------------------
# Touchscreen command helpers
# ---------------------------------------------------------------------------

# These small wrappers are the controller-side UI API. They do not draw
# anything directly; they send commands to touchscreen.run_touchscreen().

def GUI_default():
    """
    Show the default welcome screen in the GUI process.
    Does NOT block main — just sends a command and returns immediately.
    """
  
    
    if command_queue is None:
        logging.error("GUI handler not initialized")
        return
    
    _command_queue().put( ("DEFAULT", None) )
    logging.info("Sent 'kuva_default_screen' command to GUI")


def GUI_valikuvaade(nimi):

    # 2. Send command (returns immediately, non-blocking)
    nimi = nimi
    _command_queue().put( ("VALIKUVAADE", nimi) )
    
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
        _command_queue().put( ("UKSE_AVAMINE_TAGASTAMINE", unreturned_items) )
    else:
        _command_queue().put( ("UKSE_AVAMINE_VÕTMINE", None) )

    

    logging.info(f"Sent door opening screen command: {action_type}")


def GUI_reklaam():
     # Currently unused by the main drink flow, but kept as a screen command.
     _command_queue().put( ("REKLAAM", None) )


def GUI_registreerimise_küsimine():
    """Ask whether an unknown NFC card should be registered and collect PIN."""
    _command_queue().put(("REGISTREERIMINE", None)) #Reutirb vastus(True/False), pinnkood
    try:
        vastus, pinnkood = _read_reply(timeout=60)
        return vastus, pinnkood
    except queue.Empty:
        return False, None
    

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
    _command_queue().put( ("VÄLJASTATUD_JOOGID", drink_counts) )


def GUI_tagastatud(scanned_items_info):
    """
    Võtab vastu listi joogiinfo SÕNADEGA (stringidega), loendab need kokku
    ja saadab info drawerisse kuvamiseks.
    """
    
    # 'scanned_items_info' list näeb välja juba selline:
    # ['Saku Kuld', 'sommersby', 'Saku Kuld']

  
    drink_counts = Counter(scanned_items_info)
    
    # See teeb automaatselt sõnastiku:
    # {'Saku Kuld': 2, 'Coca-Cola': 1}

    # 3. Nüüd saada see drawerisse
    print(f"DEBUG: Kokkuvõte saadetud drawerisse: {drink_counts}")
    _command_queue().put( ("TAGASTATUD_JOOGID", drink_counts) )


def GUI_live_cart(scanned_items_info):
    drink_counts = Counter(scanned_items_info)
    _command_queue().put( ("LIVE_CART", drink_counts) )


def GUI_kasutaja_registreeritud(nimi):
    _command_queue().put( ("KASUTAJA_REGISTREERITUD", nimi) )
    

def GUI_pinn_vale():
    GUI_message("Vale pinnkood")


def GUI_message(message, show_button=True, button_text="Jätka", button_value=True):
    _command_queue().put( ("MESSAGE", (message, show_button, button_text, button_value)) )


# ---------------------------------------------------------------------------
# Shared validation and registration helpers
# ---------------------------------------------------------------------------

def _show_database_error_if_needed(timeout=8):
    """Show a user-facing API error if the database service recorded one."""
    if database.last_connection_error() is None:
        return False

    GUI_message("Andmebaasiga ei saa ühendust. Kontrolli võrku või serverit.")
    Oota_kasutaja_kinnitust(timeout)
    return True


def _register_user_from_pin(nfc_input, pinnkood):
    """Register an unused PIN to a newly scanned NFC card."""
    status = database.get_pin_status(pinnkood)
    if _show_database_error_if_needed():
        return False

    if not status['exists']:
        Empty_reply_queue()
        GUI_message("Sisestatud PIN-kood ei ole kehtiv. Palun proovi uuesti.")
        Oota_kasutaja_kinnitust(20)
        return False

    if status['registered']:
        logging.info("Kasutaja üritas registreerida juba registreeritud PIN-koodi.")
        Empty_reply_queue()
        GUI_message("See PIN on juba registreeritud kiipkaardile, uue kaardi registreerimiseks valige Kontohaldus avaekraanilt")
        Oota_kasutaja_kinnitust(30)
        return False

    if nfc_input is None:
        GUI_message("Kiipkaarti ei loetud. Palun proovi uuesti.")
        Oota_kasutaja_kinnitust(10)
        return False

    if not database.create_new_user(nfc_input, pinnkood):
        if _show_database_error_if_needed():
            return False
        GUI_message("Kasutaja registreerimine ebaõnnestus. Palun proovi uuesti.")
        Oota_kasutaja_kinnitust(20)
        return False

    Empty_reply_queue()
    GUI_kasutaja_registreeritud(status['name'])
    Oota_kasutaja_kinnitust(30)
    return True


def _ensure_card_is_available_for_registration(nfc_input):
    """Return True only when a card was scanned and is not already assigned."""
    if nfc_input is None:
        GUI_message("Kiipkaarti ei loetud. Palun proovi uuesti.")
        Oota_kasutaja_kinnitust(10)
        return False

    is_card_registered, existing_owner = database.checkuser(nfc_input)
    if _show_database_error_if_needed():
        return False

    if is_card_registered:
        GUI_message(f"Kaart juba registreeritud kasutajale {existing_owner}!")
        Oota_kasutaja_kinnitust(10)
        return False

    return True


# ---------------------------------------------------------------------------
# Admin and account-management workflows
# ---------------------------------------------------------------------------

def admin_loop():
    """
    Handle the admin menu after the ADMIN NFC card has authenticated.

    The UI returns either simple command strings or structured tuples such as
    ("PRODUCT_NAME", name). Barcode input is enabled only for the add-product
    scan steps so scanner keystrokes do not leak into normal UI screens.
    """
    _command_queue().put(("ADMIN", None))

    while True:
        try:
            valik = _read_reply()

            if valik == "BACK":
                logging.info("Admin loop: barcode scanning disabled")
                _command_queue().put(("DISABLE_BARCODE_SCANNING", None))
                return # Exit to main loop

            elif isinstance(valik, tuple) and valik[0] == "PRODUCT_NAME":
                product_name = valik[1]

                # Enable barcode scanning for product addition
                logging.info("Admin loop: enabling barcode scanning for product addition")
                _command_queue().put(("ENABLE_BARCODE_SCANNING", None))

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
                        try:
                            added = database.add_product(product_name, code1)
                        except AttributeError:
                            logging.error("database.add_product method missing")
                            added = False
                        except Exception:
                            logging.exception("database.add_product failed")
                            added = False

                        if added:
                            GUI_message(f"{product_name} on lisatud andmebaasi", show_button=True)
                        else:
                            GUI_message("Viga andmebaasiga suhtlemisel", show_button=True)

                        Oota_kasutaja_kinnitust(10)
                        break
                    else:
                        GUI_message("Koodid ei ühti. Proovi uuesti.", show_button=True)
                        Oota_kasutaja_kinnitust(10)
                        # Loop continues to retry scanning

                # Disable barcode scanning after product addition
                logging.info("Admin loop: disabling barcode scanning after product addition")
                _command_queue().put(("DISABLE_BARCODE_SCANNING", None))
                # Return to admin screen
                _command_queue().put(("ADMIN", None))

            elif valik == "REMOVE_PRODUCT":
                while True:
                    try:
                        products = database.get_all_products()
                    except AttributeError:
                        logging.error("database.get_all_products missing")
                        products = []
                    except Exception:
                        logging.exception("database.get_all_products failed")
                        GUI_message("Viga andmebaasiga", show_button=True)
                        Oota_kasutaja_kinnitust(5)
                        products = []

                    _command_queue().put(("REMOVE_PRODUCT_LIST", products))

                    resp = _read_reply()
                    if resp == "BACK":
                        _command_queue().put(("ADMIN", None))
                        break
                    elif isinstance(resp, tuple) and resp[0] == "DELETE_PRODUCT":
                        pid = resp[1]
                        try:
                            removed = database.remove_product(pid)
                        except AttributeError:
                            removed = False
                        except Exception:
                            logging.exception("database.remove_product failed")
                            removed = False

                        if removed:
                            GUI_message("Toode eemaldatud", show_button=False)
                            time.sleep(1)
                        else:
                            GUI_message("Viga andmebaasiga", show_button=True)
                            Oota_kasutaja_kinnitust(5)
                        # Loop continues to refresh list

            elif valik == "SHOW_DEBTORS":
                debtors = database.get_debtors()
                if _show_database_error_if_needed():
                    _command_queue().put(("ADMIN", None))
                    continue

                if not debtors:
                    GUI_message("Võlglasi ei ole.", show_button=True, button_text="Tagasi")
                    Oota_kasutaja_kinnitust(10)
                    _command_queue().put(("ADMIN", None))
                    continue

                lines = []
                for debtor in debtors[:8]:
                    name = debtor.get('name') or f"Kasutaja #{debtor.get('userid')}"
                    count = debtor.get('count', 0)
                    lines.append(f"{name}: {count}")

                if len(debtors) > 8:
                    lines.append(f"... ja veel {len(debtors) - 8}")

                GUI_message("Võlglased:\n" + "\n".join(lines), show_button=True, button_text="Tagasi")
                Oota_kasutaja_kinnitust(30)
                _command_queue().put(("ADMIN", None))

        except queue.Empty:
            pass


def kontohaldus(): 
    """Authenticate an existing card and show the account-management screen."""
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
        _command_queue().put( ("KONTOHALDUS", payload) ) #Käivitab ekraani kust näeb jookide seisu
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
    _command_queue().put( ("UUS_KAART", payload) )
    if LOGITUD == True:
        nfc_uus = hardware.get_nfc()
        if not _ensure_card_is_available_for_registration(nfc_uus):
            return

        if database.update_user_nfc(nfc_input, nfc_uus):
            GUI_message(f"Uus kaart nimele {nimi} registreeritud")
        else:
            if _show_database_error_if_needed():
                return
            GUI_message("Uue kaardi registreerimine ebaõnnestus.")
        Oota_kasutaja_kinnitust(10)
    elif LOGITUD == False: #Kaardi regamine kui kasutajal vana kaart kadunud
        _command_queue().put( ("KAOTATUD_KAART", None))
        pinnkood = _read_reply()
        status = database.get_pin_status(pinnkood)
        if _show_database_error_if_needed():
            return

        if status['exists'] == True and status['registered'] == True:
            nimi = status['name']
            GUI_message(f"Kasutaja {nimi} leitud. Viipa uut kaarti registreerimiseks", show_button=False)
            uus_nfc = hardware.get_nfc()
            if not _ensure_card_is_available_for_registration(uus_nfc):
                return

            success, nimi = database.register_new_card_by_pin(uus_nfc, pinnkood)
            if success:
                GUI_message(f"Uus kaart nimele {nimi} on edukalt registreeritud.")
                Oota_kasutaja_kinnitust(10)
            else:
                if _show_database_error_if_needed():
                    return
                GUI_message("Uue kaardi registreerimine ebaõnnestus. Kontrolli, et kasutaja nimi oleks unikaalne.")
                Oota_kasutaja_kinnitust(10)
            return
        elif status['exists'] == True and status['registered'] == False:
            nimi = status['name']
            _command_queue().put(("REGISTREERI_PINNKOODI_ALUSEL", None))
            vastus = _read_reply(timeout=60)
            if vastus == True:
                GUI_message(f"Viipa kiipkaarti kasutaja {nimi} registreerimiseks.", show_button=False)
                nfc_input = hardware.get_nfc()
                if nfc_input is None:
                    return
                Empty_reply_queue()
                if _ensure_card_is_available_for_registration(nfc_input):
                    _register_user_from_pin(nfc_input, pinnkood)
            else: 
                pass
        else: 
            GUI_message("Pinnkoodi ei leitud.")
            Oota_kasutaja_kinnitust(10)


# ---------------------------------------------------------------------------
# Drink take/return workflow
# ---------------------------------------------------------------------------

def _wait_for_door_open(timeout=10):
    """Wait briefly for the door sensor to report open after unlocking."""
    wait_start = time.time()
    while not hardware.is_door_open():
        if time.time() - wait_start > timeout:
            logging.warning("Door did not report open before timeout")
            return False
        time.sleep(0.1)
    return True


def _scan_items_until_door_closes():
    """Collect barcode events from the UI process while the cabinet door is open."""
    scanned_items_info = []
    scanned_barcodes = []

    GUI_live_cart([])
    _require_lcd().clear()
    _require_lcd().show_message("Skaneeri tooted...")

    while hardware.is_door_open():
        barcode_to_process = None
        try:
            message = _reply_queue().get_nowait()
            if message == APP_EXIT:
                raise SystemExit
            logging.info(f"MAIN-LOOP: Got message from reply_q: {message}")

            if isinstance(message, str) and message.startswith("BARCODE:"):
                barcode_to_process = message.replace("BARCODE:", "", 1)

        except queue.Empty:
            pass

        if barcode_to_process:
            logging.info(f"MAIN-LOOP: Processing as barcode: {barcode_to_process}")
            is_in_db, drink_info = database.get_drink_info(barcode_to_process)

            if is_in_db == False:
                _require_lcd().show_message("Toodet pole nimekirjas")
                time.sleep(1)
                _require_lcd().clear()
                _require_lcd().show_message("Skaneeri tooted...")
                continue

            scanned_barcodes.append(barcode_to_process)
            scanned_items_info.append(drink_info)
            GUI_live_cart(scanned_items_info)

            count = scanned_items_info.count(drink_info)
            _require_lcd().show_message(f"{drink_info} X{count}")
            time.sleep(1)
            _require_lcd().clear()
            _require_lcd().show_message("Skaneeri tooted...")

        time.sleep(0.05)

    return scanned_items_info, scanned_barcodes


def _review_cart(scanned_items_info, scanned_barcodes):
    """Let the user confirm/edit final counts, then rebuild barcode lists."""
    name_to_barcodes = {}
    for name, code in zip(scanned_items_info, scanned_barcodes):
        name_to_barcodes.setdefault(name, []).append(code)

    logging.info(f"MAIN-LOOP: Final cart before review: {scanned_items_info}")
    Empty_reply_queue()
    original_counts = Counter(scanned_items_info)
    _command_queue().put(("CART_REVIEW", dict(original_counts)))

    try:
        final_counts = _read_reply(timeout=300)
    except queue.Empty:
        final_counts = original_counts

    if not isinstance(final_counts, dict):
        final_counts = original_counts

    final_items = []
    final_barcodes = []
    for name, count in final_counts.items():
        available_codes = name_to_barcodes.get(name, [])
        for code in available_codes[:max(0, int(count))]:
            final_items.append(name)
            final_barcodes.append(code)

    return final_items, final_barcodes


def _run_drink_session(nfc_input, action_type):
    """Shared implementation for both taking and returning drinks."""
    is_return = action_type == "returned"
    scanned_items_info = []
    scanned_barcodes = []

    if is_return:
        unreturned_drinks = database.get_unreturned_drinks(nfc_input)
        logging.info(
            f"joogi_tagastus: unreturned payload type={type(unreturned_drinks).__name__}, "
            f"count={len(unreturned_drinks) if hasattr(unreturned_drinks, '__len__') else 'n/a'}"
        )
        GUI_ukse_avamine("2", unreturned_drinks)
        Oota_kasutaja_kinnitust(30)
    else:
        GUI_ukse_avamine("1")
        time.sleep(1)

    try:
        _require_lcd().set_backlight(True)
        hardware.Ukse_avaja()

        logging.info("drink session: enabling barcode scanning for %s", action_type)
        _command_queue().put(("ENABLE_BARCODE_SCANNING", None))
        _wait_for_door_open()

        scanned_items_info, scanned_barcodes = _scan_items_until_door_closes()

    finally:
        _require_lcd().set_backlight(False)
        logging.info("drink session: disabling barcode scanning for %s", action_type)
        _command_queue().put(("DISABLE_BARCODE_SCANNING", None))

    final_items, final_barcodes = _review_cart(scanned_items_info, scanned_barcodes)

    if is_return:
        GUI_tagastatud(final_items)
    else:
        GUI_võetud(final_items)
    time.sleep(3)

    if not database.record_drink_session(nfc_input, action_type, final_barcodes):
        if _show_database_error_if_needed():
            pass
        else:
            GUI_message("Tehingu salvestamine ebaõnnestus. Palun võta ühendust adminiga.")
            Oota_kasutaja_kinnitust(15)

    _require_lcd().clear()
    Empty_reply_queue()
    Empty_command_queue()


def joogi_väljastus(nfc_input):
    _run_drink_session(nfc_input, "taken")


def joogi_tagastus(nfc_input):
    _run_drink_session(nfc_input, "returned")


# ---------------------------------------------------------------------------
# Main menu router
# ---------------------------------------------------------------------------

def main_loop():
    """Start the UI process, then route top-level user choices forever.

    Most top-level screen buttons return a command string. The controller then
    performs hardware/API work and sends the next screen command back to the
    UI process.
    """
    global command_queue, reply_queue, _gui_proc
    command_queue = multiprocessing.Queue()
    reply_queue = multiprocessing.Queue()
    _gui_proc = multiprocessing.Process(target=touchscreen.run_touchscreen, args=(command_queue, reply_queue))
    _gui_proc.start()

    # Initialize door sensor with button
    hardware.init_door_sensor()

    while True:
        # Each loop iteration starts from a clean main menu state.
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
                    _register_user_from_pin(nfc_input, pinnkood)
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
            _command_queue().put(("UUE_KONTO_REGAMINE_PINNKOODIGA", None))
            vastus = _read_reply()
            pinnkood = vastus
            if vastus == "CANCEL":
                pass
            else:
                status = database.get_pin_status(pinnkood)
                if _show_database_error_if_needed():
                    continue
                if status['exists'] and not status['registered']:
                    GUI_message(f"Tere, {status['name']}! Viipa kiipkaarti kasutaja registreerimiseks", show_button=False)
                    nfc_input = hardware.get_nfc()
                    if nfc_input is None:
                        continue
                    if not _ensure_card_is_available_for_registration(nfc_input):
                        continue
                    _register_user_from_pin(nfc_input, pinnkood)
                    continue
                _register_user_from_pin(None, pinnkood)
                continue

        elif valik == "ADMIN":
            while True:
                Empty_reply_queue()
                GUI_message("Viipa admin kiipi", show_button=True, button_text="Tagasi", button_value="tagasi")
                logging.info("Admin auth: waiting for NFC")
                nfc_input = hardware.get_nfc(check_for_admin_cancel)
                logging.info("Admin auth: NFC result=%s", nfc_input)

                if nfc_input is None:
                    break

                is_in_db, name = database.checkuser(nfc_input)
                logging.info("Admin auth: checkuser exists=%s name=%s", is_in_db, name)
                if is_in_db and name == "ADMIN":
                    admin_loop()
                    break

                if _show_database_error_if_needed():
                    break

                GUI_message("Vale kaart. Viipa admin kiipi uuesti.", show_button=False)
                time.sleep(2)



# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def run():
    global lcd

    _install_signal_handlers()
    atexit.register(_cleanup)

    lcd = LCD()

    try:
        _check_startup_database_connection()
        main_loop()
    finally:
        _cleanup()


if __name__ == "__main__":
    run()
