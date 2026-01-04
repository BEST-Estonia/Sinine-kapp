import sqlite3
import logging
import datetime


#Tsekib kas kasutaja on olemas databases. user tabelis. UID järgi. tabelis nfcid
def checkuser(UID):
    """
    Connects to database.db and checks if the nfcid exists.
    Returns (True, name) if found.
    Returns (False, None) if not found.
    Logs any errors.
    """
    db_file = 'database.db'
    conn = None
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # 1. The SQL Query: Select the 'name' based on the 'nfcid'
        query = "SELECT name FROM users WHERE nfcid = ?"
        
        # 2. Execute the query
        cursor.execute(query, (UID,))
        
        # 3. Get the result
        # .fetchone() will return a tuple like ('john_doe',) if found
        # Otherwise, it will return None.
        result = cursor.fetchone()
        
        # 4. Check the result and return TWO values
        if result:
            user_name = result[0]  # Get the name from the tuple
            return (True, user_name)
        else:
            return (False, None) # Return False and None for the name
            
    except sqlite3.Error as e:
        logging.error(f"(DB Handler) checkuser: Database error. Error: {e}")
        return (False, None)  # Return a safe default
    except Exception as e:
        logging.error(f"(DB Handler) checkuser: General error. Error: {e}")
        return (False, None)  # Return a safe default
        
    finally:
        # 5. Always close the connection
        if conn:
            conn.close()

#tsekib kas jook on adnmebaasis, kui ei siis tagastab False, None kui ja siis tgastab True, "joogi nimi"
def get_drink_info(barcode):
    """
    Connects to database.db and tries to find a product by its barcode.
    
    Returns (True, drink_name) if found.
    Returns (False, None) if not found or an error occurs.
    Logs any errors.
    """
    db_file = 'database.db'
    conn = None
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # 1. The SQL Query: Select the 'name' based on the 'barcode'
        # This is the line you wanted to fix.
        query = "SELECT name FROM Products WHERE barcode = ?"
        
        # 2. Execute the query
        cursor.execute(query, (barcode,))
        
        # 3. Get the result
        # .fetchone() will return a tuple like ('Coke',) if found
        # Otherwise, it will return None.
        result = cursor.fetchone()
        
        # 4. Check the result and return the info
        if result:
            drink_name = result[0]  # Get the name (e.g., 'Coke') from the tuple
            return (True, drink_name) # Found it!
        else:
            return (False, None) # Did not find it
            
    except sqlite3.Error as e:
        # 5. Log the error
        logging.error(f"(DB Handler) get_drink_info: Database error. Error: {e}")
        return (False, None)  # Return a safe default
    except Exception as e:
        logging.error(f"(DB Handler) get_drink_info: General error. Error: {e}")
        return (False, None)  # Return a safe default
        
    finally:
        # 6. Always close the connection
        if conn:
            conn.close()


#tekitab listi kõikides barcodedest ja teades user_id logib need andmebaasi
def log_user_returned_drinks(nfc_input, list_of_barcodes):
    """
    Logs a list of scanned products as "returned" for a user.
    
    - Fetches the userid from the users table.
    - For each barcode:
        - Tries to find an unreturned item and UPDATE it.
        - If no unreturned item is found, it INSERTS a new 
          transaction with date_taken = NULL.
    
    Returns True if successful, False if any error occurs.
    """
    db_file = 'database.db'
    conn = None
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # --- Start a Database Transaction ---
        cursor.execute("BEGIN TRANSACTION")

        # --- Step 1: Get the userid from the nfcid ---
        cursor.execute("SELECT userid FROM users WHERE nfcid = ?", (nfc_input,))
        user_result = cursor.fetchone()
        
        if not user_result:
            logging.error(f"(DB Handler) log_user_returned_drinks: User not found with NFC ID {nfc_input}")
            conn.rollback()
            return False
        
        user_id = user_result[0]
        
        # --- Step 2: Get the current time for 'date_returned' ---
        date_returned_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # --- Step 3: Loop through barcodes and process each return ---
        for barcode in list_of_barcodes:
            
            # A. Find the 'rental_id' of an item to return
            find_query = """
            SELECT rental_id FROM Transactions
            WHERE userid = ? AND barcode = ? AND date_returned IS NULL
            ORDER BY date_taken ASC
            LIMIT 1 
            """
            cursor.execute(find_query, (user_id, barcode))
            item_to_return = cursor.fetchone()

            # B. Check if we found a matching item
            if item_to_return:
                # --- LOGIC A: Found an item to update ---
                rental_id_to_update = item_to_return[0]
                update_query = """
                UPDATE Transactions
                SET date_returned = ?
                WHERE rental_id = ?
                """
                cursor.execute(update_query, (date_returned_str, rental_id_to_update))
            
            else:
                # --- LOGIC B: (New) Did not find a match, so create a new record ---
                
                # We still need the productname to insert
                cursor.execute("SELECT name FROM Products WHERE barcode = ?", (barcode,))
                product_result = cursor.fetchone()
                
                if not product_result:
                    # The barcode doesn't even exist in Products table.
                    # This is a fatal error, must roll back.
                    logging.warning(f"(DB Handler) log_user_returned_drinks: Product not found with barcode {barcode}. Aborting transaction.")
                    conn.rollback()
                    return False
                
                product_name = product_result[0]

                # Insert a new record with NULL date_taken
                insert_query = """
                INSERT INTO Transactions (userid, productname, date_taken, date_returned, barcode)
                VALUES (?, ?, NULL, ?, ?)
                """
                cursor.execute(insert_query, (user_id, product_name, date_returned_str, barcode))

        # --- Step 4: If all loops succeeded, commit the changes ---
        conn.commit()
        logging.info(f"Successfully processed {len(list_of_barcodes)} returned items for user {user_id} ({nfc_input})")
        return True

    except sqlite3.Error as e:
        logging.error(f"(DB Handler) log_user_returned_drinks: Database error. Error: {e}")
        if conn:
            conn.rollback()
        return False
    except Exception as e:
        logging.error(f"(DB Handler) log_user_returned_drinks: General error. Error: {e}")
        if conn:
            conn.rollback()
        return False
        
    finally:
        if conn:
            conn.close()

#Loob uue kasutaja andmebaasi pinnkoodi ja nfcinputist saadud nfc id järgi
def create_new_user(nfc_input, pinnkood):
    """
    Create a new user row in the `users` table using the name associated
    with `pinnkood` in the `Pintable` table.

    Returns True on success, False on failure.
    """
    db_file = 'database.db'
    conn = None
    try:
        # Normalize pin: try to convert to int, but allow string fallback
        try:
            pin_val = int(pinnkood)
        except (ValueError, TypeError):
            pin_val = pinnkood

        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Look up the name associated with this pin in Pintable
        cursor.execute("SELECT nimi FROM Pintable WHERE pinnkood = ?", (pin_val,))
        row = cursor.fetchone()
        if not row:
            logging.error(f"(DB Handler) create_new_user: Pin not found in Pintable: {pinnkood}")
            return False

        name = row[0]

        # Ensure NFC ID isn't already present
        cursor.execute("SELECT userid FROM users WHERE nfcid = ?", (nfc_input,))
        if cursor.fetchone():
            logging.warning(f"(DB Handler) create_new_user: NFC ID already exists: {nfc_input}")
            return False

        # Insert the new user
        cursor.execute("INSERT INTO users (nfcid, name) VALUES (?, ?)", (nfc_input, name))
        
        # Mark the PIN as registered
        cursor.execute("UPDATE Pintable SET isregistered = 1 WHERE pinnkood = ?", (pin_val,))
        
        conn.commit()
        logging.info(f"(DB Handler) create_new_user: Created user '{name}' with NFC {nfc_input}")
        return True

    except sqlite3.IntegrityError as e:
        logging.error(f"(DB Handler) create_new_user: Integrity error: {e}")
        if conn:
            conn.rollback()
        return False
    except sqlite3.Error as e:
        logging.error(f"(DB Handler) create_new_user: Database error: {e}")
        if conn:
            conn.rollback()
        return False
    except Exception as e:
        logging.error(f"(DB Handler) create_new_user: General error: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


# Log taken drinks (Sisestab Transactions tabelisse kui kasutaja võtab jooke)
def log_user_taken_drinks(nfc_input, list_of_barcodes):
    """
    Logs a list of scanned products as "taken" for a user.

    - Fetches the userid from the users table using the provided `nfc_input`.
    - For each barcode in `list_of_barcodes`:
        - Looks up product name in `Products`.
        - Inserts a new Transactions row with `date_taken` set and `date_returned` NULL.

    Returns True on success, False on any failure.
    """
    db_file = 'database.db'
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Start a transaction so either all inserts succeed or none
        cursor.execute("BEGIN TRANSACTION")

        # Resolve userid from nfcid
        cursor.execute("SELECT userid FROM users WHERE nfcid = ?", (nfc_input,))
        user_result = cursor.fetchone()
        if not user_result:
            logging.error(f"(DB Handler) log_user_taken_drinks: User not found with NFC ID {nfc_input}")
            conn.rollback()
            return False

        user_id = user_result[0]
        date_taken_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for barcode in list_of_barcodes:
            # Ensure product exists and get its name
            cursor.execute("SELECT name FROM Products WHERE barcode = ?", (barcode,))
            product_result = cursor.fetchone()
            if not product_result:
                logging.warning(f"(DB Handler) log_user_taken_drinks: Product not found with barcode {barcode}. Aborting transaction.")
                conn.rollback()
                return False

            product_name = product_result[0]

            # Insert transaction row
            insert_query = """
            INSERT INTO Transactions (userid, productname, date_taken, date_returned, barcode)
            VALUES (?, ?, ?, NULL, ?)
            """
            cursor.execute(insert_query, (user_id, product_name, date_taken_str, barcode))

        # All inserts succeeded
        conn.commit()
        logging.info(f"(DB Handler) log_user_taken_drinks: Successfully logged {len(list_of_barcodes)} taken items for user {user_id} ({nfc_input})")
        return True

    except sqlite3.Error as e:
        logging.error(f"(DB Handler) log_user_taken_drinks: Database error. Error: {e}")
        if conn:
            conn.rollback()
        return False
    except Exception as e:
        logging.error(f"(DB Handler) log_user_taken_drinks: General error. Error: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

#Kontrollib kas kasutaja sisestatud pinnkood on pinnkoodi andmebaasis
#Võtab sisse kasutaja sisestatud pinnkoodi ja returnim True on andmebaasis False pole sellist adnmebaasis
def check_pin_code_dict(pinnkood):
    """
    Check whether a given `pinnkood` exists in the `Pintable` table of `database.db`.
    Returns True if found, False otherwise. Logs errors on database failures.
    """
    db_file = 'database.db'
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT pinnkood FROM Pintable WHERE pinnkood = ?", (pinnkood,))
        result = cursor.fetchone()
        return bool(result)
    except sqlite3.Error as e:
        logging.error(f"(DB Handler) check_pin_code_dict: Database error. Error: {e}")
        return False
    except Exception as e:
        logging.error(f"(DB Handler) check_pin_code_dict: General error. Error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def is_user_registered(pinnkood):
    """
    Checks if user with that pincode isregistered is 0 or 1.
    Returns True if isregistered == 1.
    Returns False if isregistered == 0 or error/not found.
    """
    db_file = 'database.db'
    conn = None
    try:
        # Normalize pin: try to convert to int, but allow string fallback
        try:
            pin_val = int(pinnkood)
        except (ValueError, TypeError):
            pin_val = pinnkood

        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT isregistered FROM Pintable WHERE pinnkood = ?", (pin_val,))
        result = cursor.fetchone()
        
        if result:
            return result[0] == 1
        return False
    except sqlite3.Error as e:
        logging.error(f"(DB Handler) is_user_registered: Database error. Error: {e}")
        return False
    except Exception as e:
        logging.error(f"(DB Handler) is_user_registered: General error. Error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def nime_kaeve_pintabelist(pinnkood):
    """
    Searches the Pintable for a given pinnkood and returns the corresponding name.
    
    Args:
        pinnkood: The PIN code to search for
    
    Returns:
        (True, name) if pinnkood found in Pintable
        (False, None) if pinnkood not found or error occurs
    
    Logs any errors.
    """
    db_file = 'database.db'
    conn = None
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Search Pintable for the pinnkood and get the name
        query = "SELECT nimi FROM Pintable WHERE pinnkood = ?"
        
        cursor.execute(query, (pinnkood,))
        result = cursor.fetchone()
        
        if result:
            name = result[0]  # Get the name from the tuple
            return (True, name)
        else:
            logging.warning(f"(DB Handler) nime_kaeve_pintabelist: PIN code {pinnkood} not found in Pintable")
            return (False, None)
    
    except sqlite3.Error as e:
        logging.error(f"(DB Handler) nime_kaeve_pintabelist: Database error. Error: {e}")
        return (False, None)
    except Exception as e:
        logging.error(f"(DB Handler) nime_kaeve_pintabelist: General error. Error: {e}")
        return (False, None)
    finally:
        if conn:
            conn.close()

def get_unreturned_drinks(nfc_input):
    """
    Skännib transaction tabelit ja otsib kõik kasutaja võetud joogid mis pole tagastatud.
    Args:
        nfc_input: nfc tag
    
    Returns:
        A list of tuples: [(productname, barcode, date_taken), ...]
        Returns an empty list if user not found or no unreturned items.
        Logs any errors.
    """
    db_file = 'database.db'
    conn = None
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Step 1: Get userid from nfcid
        cursor.execute("SELECT userid FROM users WHERE nfcid = ?", (nfc_input,))
        user_result = cursor.fetchone()
        
        if not user_result:
            logging.warning(f"(DB Handler) get_unreturned_drinks: User not found with NFC ID {nfc_input}")
            return []
        
        user_id = user_result[0]
        
        # Step 2: Get all unreturned drinks for this user
        # WHERE date_returned IS NULL means the drink hasn't been returned yet
        query = """
        SELECT productname, barcode, date_taken FROM Transactions
        WHERE userid = ? AND date_returned IS NULL
        ORDER BY date_taken ASC
        """
        cursor.execute(query, (user_id,))
        unreturned_items = cursor.fetchall()
        
        if unreturned_items:
            logging.info(f"(DB Handler) get_unreturned_drinks: Found {len(unreturned_items)} unreturned items for user {user_id} ({nfc_input})")
        else:
            logging.info(f"(DB Handler) get_unreturned_drinks: No unreturned items found for user {user_id} ({nfc_input})")
        
        return unreturned_items
    
    except sqlite3.Error as e:
        logging.error(f"(DB Handler) get_unreturned_drinks: Database error. Error: {e}")
        return []
    except Exception as e:
        logging.error(f"(DB Handler) get_unreturned_drinks: General error. Error: {e}")
        return []
    finally:
        if conn:
            conn.close()

def keep_stock(scanned_barcodes, action_type):
    """
    Updates the stock count for the provided barcodes.
    
    Args:
        scanned_barcodes: List of barcodes (integers or strings).
        action_type: String, either "taken" (decrements stock) or "returned" (increments stock).
        
    Returns:
        True if successful, False otherwise.
    """
    db_file = 'database.db'
    conn = None
    
    # Determine the adjustment value
    if action_type == "taken":
        adjustment = -1
    elif action_type == "returned":
        adjustment = 1
    else:
        logging.error(f"(DB Handler) keep_stock: Invalid action_type '{action_type}'. Must be 'taken' or 'returned'.")
        return False

    if not scanned_barcodes:
        return True

    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        cursor.execute("BEGIN TRANSACTION")
        
        query = "UPDATE Products SET stock = stock + ? WHERE barcode = ?"
        
        for barcode in scanned_barcodes:
            cursor.execute(query, (adjustment, barcode))
            
        conn.commit()
        logging.info(f"(DB Handler) keep_stock: Updated stock for {len(scanned_barcodes)} items. Action: {action_type}")
        return True
        
    except sqlite3.Error as e:
        logging.error(f"(DB Handler) keep_stock: Database error. Error: {e}")
        if conn:
            conn.rollback()
        return False
    except Exception as e:
        logging.error(f"(DB Handler) keep_stock: General error. Error: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

#Vahetab kasutaja nfc kaardi uue vastu
def update_user_nfc(nfc_input, nfc_uus):
    """
    Finds user with nfc_input and replaces that nfc uid with nfc_uus variable.
    Returns True on success, False on failure.
    """
    db_file = 'database.db'
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Check if new NFC ID is already in use
        cursor.execute("SELECT userid FROM users WHERE nfcid = ?", (nfc_uus,))
        if cursor.fetchone():
            logging.warning(f"(DB Handler) update_user_nfc: New NFC ID {nfc_uus} is already in use.")
            return False

        # Update the user's NFC ID
        cursor.execute("UPDATE users SET nfcid = ? WHERE nfcid = ?", (nfc_uus, nfc_input))
        
        if cursor.rowcount == 0:
            logging.warning(f"(DB Handler) update_user_nfc: No user found with NFC ID {nfc_input}")
            return False

        conn.commit()
        logging.info(f"(DB Handler) update_user_nfc: Updated NFC ID from {nfc_input} to {nfc_uus}")
        return True

    except sqlite3.Error as e:
        logging.error(f"(DB Handler) update_user_nfc: Database error: {e}")
        if conn:
            conn.rollback()
        return False
    except Exception as e:
        logging.error(f"(DB Handler) update_user_nfc: General error: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def register_new_card(uus_nfc, nimi):
    """
    Search user table for given name and assigns new nfcid to user.
    Returns True on success, False on failure.
    """
    db_file = 'database.db'
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Check if new NFC ID is already in use
        cursor.execute("SELECT userid FROM users WHERE nfcid = ?", (uus_nfc,))
        if cursor.fetchone():
            logging.warning(f"(DB Handler) register_new_card: New NFC ID {uus_nfc} is already in use.")
            return False

        # Update the user's NFC ID based on name
        cursor.execute("UPDATE users SET nfcid = ? WHERE name = ?", (uus_nfc, nimi))
        
        if cursor.rowcount == 0:
            logging.warning(f"(DB Handler) register_new_card: No user found with name {nimi}")
            return False

        conn.commit()
        logging.info(f"(DB Handler) register_new_card: Assigned new NFC {uus_nfc} to user {nimi}")
        return True

    except Exception as e:
        logging.error(f"(DB Handler) register_new_card: Error: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()