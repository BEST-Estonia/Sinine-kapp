import datetime
import logging
import os
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from ..paths import ENV_FILE

_MYSQL_CONFIG: dict[str, Any] | None = None
_ENV_LOADED = False
_MYSQL_DRIVER_NAME: str | None = None
_MYSQL_CONNECTOR_WARNING_LOGGED = False
_LAST_CONNECTION_ERROR: str | None = None


def _load_env_file(path: Path, overwrite: bool = False) -> bool:
    if not path.exists():
        return False

    loaded_any = False

    for raw_line in path.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue

        key, value = line.split('=', 1)
        key = key.strip().lstrip('\ufeff')
        if not key:
            continue

        value = value.strip().strip('"').strip("'")

        if overwrite or key not in os.environ:
            os.environ[key] = value
            loaded_any = True

    return loaded_any


def _load_environment_once() -> None:
    global _ENV_LOADED

    if _ENV_LOADED:
        return

    candidates = [
        (ENV_FILE, True),
        (ENV_FILE.parent.parent / 'portaal' / '.env', False),
    ]

    for candidate, overwrite in candidates:
        loaded = _load_env_file(candidate, overwrite=overwrite)
        if loaded:
            logging.info(
                '(DB Handler) Loaded environment values from %s (overwrite=%s)',
                candidate,
                overwrite,
            )

    _ENV_LOADED = True


def _parse_database_url(database_url: str) -> dict[str, Any]:
    parsed = urlparse(database_url)

    if parsed.scheme not in {'mysql', 'mysql2'}:
        raise ValueError(f'Unsupported DATABASE_URL scheme: {parsed.scheme}')

    database = parsed.path.lstrip('/')
    if not database:
        raise ValueError('DATABASE_URL must include a database name')

    return {
        'host': parsed.hostname or 'localhost',
        'port': parsed.port or 3306,
        'user': unquote(parsed.username or 'root'),
        'password': unquote(parsed.password or ''),
        'database': database,
    }


def _connection_timeout(name: str, default: int) -> int:
    raw_value = os.environ.get(name, '').strip()
    if not raw_value:
        return default

    try:
        return max(1, int(raw_value))
    except ValueError:
        logging.warning(
            '(DB Handler) Invalid %s=%r, using %s seconds',
            name,
            raw_value,
            default,
        )
        return default


def last_connection_error() -> str | None:
    return _LAST_CONNECTION_ERROR


def _connect_mysql(params: dict[str, Any]):
    global _MYSQL_DRIVER_NAME, _MYSQL_CONNECTOR_WARNING_LOGGED

    try:
        import mysql.connector  # type: ignore

        conn = mysql.connector.connect(
            host=params['host'],
            port=int(params['port']),
            user=str(params['user']),
            password=str(params['password']),
            database=str(params['database']),
            autocommit=False,
            connection_timeout=_connection_timeout('SININE_KAPP_DB_CONNECT_TIMEOUT', 5),
        )
        if _MYSQL_DRIVER_NAME is None:
            _MYSQL_DRIVER_NAME = 'mysql-connector-python'
        return conn
    except ModuleNotFoundError:
        if not _MYSQL_CONNECTOR_WARNING_LOGGED:
            logging.warning(
                '(DB Handler) mysql-connector-python is not installed, trying pymysql fallback driver.'
            )
            _MYSQL_CONNECTOR_WARNING_LOGGED = True

    try:
        import pymysql  # type: ignore

        connect_timeout = _connection_timeout('SININE_KAPP_DB_CONNECT_TIMEOUT', 5)
        conn = pymysql.connect(
            host=str(params['host']),
            port=int(params['port']),
            user=str(params['user']),
            password=str(params['password']),
            database=str(params['database']),
            autocommit=False,
            charset='utf8mb4',
            connect_timeout=connect_timeout,
            read_timeout=10,
            write_timeout=10,
        )
        if _MYSQL_DRIVER_NAME is None:
            _MYSQL_DRIVER_NAME = 'pymysql'
        return conn
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            'MySQL backend selected but no driver is installed. '
            'Install one: pip install mysql-connector-python OR pip install pymysql'
        ) from exc


def _mysql_config() -> dict[str, Any]:
    global _MYSQL_CONFIG

    _load_environment_once()
    if _MYSQL_CONFIG is not None:
        return _MYSQL_CONFIG

    database_url = os.environ.get('DATABASE_URL', '').strip()
    if not database_url:
        raise RuntimeError(
            'DATABASE_URL is missing. This project is configured for external database use only.'
        )

    _MYSQL_CONFIG = _parse_database_url(database_url)
    logging.info(
        '(DB Handler) Using MySQL backend target: %s@%s:%s/%s',
        _MYSQL_CONFIG['user'],
        _MYSQL_CONFIG['host'],
        _MYSQL_CONFIG['port'],
        _MYSQL_CONFIG['database'],
    )
    return _MYSQL_CONFIG


def _connect():
    global _LAST_CONNECTION_ERROR

    try:
        conn = _connect_mysql(_mysql_config())
        _LAST_CONNECTION_ERROR = None
        return conn
    except Exception as exc:
        _LAST_CONNECTION_ERROR = str(exc)
        raise


def check_connection() -> tuple[bool, str]:
    """
    Performs a lightweight startup health check against the configured database.

    Returns (True, details) when a connection and SELECT 1 succeed.
    Returns (False, error_message) when the external database is unreachable.
    """
    conn = None

    try:
        conn = _connect()
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        cursor.fetchone()

        config = _mysql_config()
        driver = _MYSQL_DRIVER_NAME or 'unknown-driver'
        return (
            True,
            f"{driver} connected to {config['user']}@{config['host']}:{config['port']}/{config['database']}",
        )

    except Exception as exc:
        return False, str(exc)

    finally:
        if conn:
            conn.close()


def _sql(query: str) -> str:
    return query.replace('?', '%s')


def _execute(cursor, query: str, params: tuple[Any, ...] = ()) -> None:
    cursor.execute(_sql(query), params)


def _fetchone(cursor, query: str, params: tuple[Any, ...] = ()): 
    _execute(cursor, query, params)
    return cursor.fetchone()


def _fetchall(cursor, query: str, params: tuple[Any, ...] = ()): 
    _execute(cursor, query, params)
    return cursor.fetchall()


def _rollback_safely(conn) -> None:
    try:
        conn.rollback()
    except Exception:
        pass


def _now_sql_timestamp() -> str:
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def _get_user_id(cursor, nfc_input: Any) -> int | None:
    row = _fetchone(cursor, 'SELECT userid FROM `users` WHERE nfcid = ?', (str(nfc_input),))
    if not row:
        return None
    return int(row[0])


def _get_product_name(cursor, barcode: Any) -> str | None:
    row = _fetchone(cursor, 'SELECT name FROM `Products` WHERE barcode = ?', (str(barcode),))
    if not row:
        return None
    return str(row[0])


def _normalize_pin(pinnkood):
    try:
        return int(pinnkood)
    except (ValueError, TypeError):
        return pinnkood


def get_pin_status(pinnkood):
    """
    Returns details for a PIN from Pintable.

    Shape:
    - {'exists': False, 'registered': False, 'name': None}
    - {'exists': True, 'registered': bool, 'name': '...'}
    """
    conn = None

    try:
        pin_val = _normalize_pin(pinnkood)
        conn = _connect()
        cursor = conn.cursor()
        row = _fetchone(
            cursor,
            'SELECT nimi, isregistered FROM `Pintable` WHERE pinnkood = ?',
            (pin_val,),
        )

        if not row:
            return {'exists': False, 'registered': False, 'name': None}

        return {'exists': True, 'registered': bool(row[1]), 'name': str(row[0])}

    except Exception as e:
        logging.error(f'(DB Handler) get_pin_status: Error: {e}')
        return {'exists': False, 'registered': False, 'name': None}

    finally:
        if conn:
            conn.close()


def checkuser(UID):
    """
    Checks if user exists by nfcid.

    Returns (True, name) if found, else (False, None).
    """
    conn = None

    try:
        conn = _connect()
        cursor = conn.cursor()
        row = _fetchone(cursor, 'SELECT name FROM `users` WHERE nfcid = ?', (str(UID),))

        if row:
            return True, str(row[0])
        return False, None

    except Exception as e:
        logging.error(f'(DB Handler) checkuser: Error: {e}')
        return False, None

    finally:
        if conn:
            conn.close()


def get_drink_info(barcode):
    """
    Tries to find product by barcode.

    Returns (True, drink_name) if found, else (False, None).
    """
    conn = None

    try:
        conn = _connect()
        cursor = conn.cursor()
        row = _fetchone(cursor, 'SELECT name FROM `Products` WHERE barcode = ?', (str(barcode),))

        if row:
            return True, str(row[0])
        return False, None

    except Exception as e:
        logging.error(f'(DB Handler) get_drink_info: Error: {e}')
        return False, None

    finally:
        if conn:
            conn.close()


def log_user_returned_drinks(nfc_input, list_of_barcodes):
    """
    Compatibility wrapper for older callers.

    Returns are now recorded through record_drink_session(), which refuses to
    accept a returned barcode unless the user has a matching open transaction.
    """
    return record_drink_session(nfc_input, 'returned', list_of_barcodes)


def create_new_user(nfc_input, pinnkood):
    """
    Creates a user in `users` using name from `Pintable` for given pin.

    Returns True on success, False otherwise.
    """
    conn = None

    try:
        pin_val = _normalize_pin(pinnkood)

        conn = _connect()
        cursor = conn.cursor()

        pin_row = _fetchone(cursor, 'SELECT nimi FROM `Pintable` WHERE pinnkood = ?', (pin_val,))
        if not pin_row:
            logging.error(f'(DB Handler) create_new_user: Pin not found in Pintable: {pinnkood}')
            return False

        name = str(pin_row[0])

        existing_user = _fetchone(cursor, 'SELECT userid FROM `users` WHERE nfcid = ?', (str(nfc_input),))
        if existing_user:
            logging.warning(f'(DB Handler) create_new_user: NFC ID already exists: {nfc_input}')
            return False

        _execute(cursor, 'INSERT INTO `users` (nfcid, name) VALUES (?, ?)', (str(nfc_input), name))
        _execute(cursor, 'UPDATE `Pintable` SET isregistered = 1 WHERE pinnkood = ?', (pin_val,))

        conn.commit()
        logging.info(f"(DB Handler) create_new_user: Created user '{name}' with NFC {nfc_input}")
        return True

    except Exception as e:
        logging.error(f'(DB Handler) create_new_user: Error: {e}')
        if conn:
            _rollback_safely(conn)
        return False

    finally:
        if conn:
            conn.close()


def log_user_taken_drinks(nfc_input, list_of_barcodes):
    """
    Compatibility wrapper for older callers.

    Takes are now recorded through record_drink_session() so transaction rows
    and stock updates commit together.
    """
    return record_drink_session(nfc_input, 'taken', list_of_barcodes)


def check_pin_code_dict(pinnkood):
    """
    Returns True if `pinnkood` exists in `Pintable`, else False.
    """
    conn = None

    try:
        pin_val = _normalize_pin(pinnkood)
        conn = _connect()
        cursor = conn.cursor()
        row = _fetchone(cursor, 'SELECT pinnkood FROM `Pintable` WHERE pinnkood = ?', (pin_val,))
        return bool(row)

    except Exception as e:
        logging.error(f'(DB Handler) check_pin_code_dict: Error: {e}')
        return False

    finally:
        if conn:
            conn.close()


def is_user_registered(pinnkood):
    """
    Returns True when Pintable.isregistered == 1 for given pin.
    """
    conn = None

    try:
        pin_val = _normalize_pin(pinnkood)

        conn = _connect()
        cursor = conn.cursor()
        row = _fetchone(cursor, 'SELECT isregistered FROM `Pintable` WHERE pinnkood = ?', (pin_val,))

        if not row:
            return False

        return bool(row[0])

    except Exception as e:
        logging.error(f'(DB Handler) is_user_registered: Error: {e}')
        return False

    finally:
        if conn:
            conn.close()


def nime_kaeve_pintabelist(pinnkood):
    """
    Reads name (`nimi`) from Pintable by pin code.

    Returns (True, name) if found else (False, None).
    """
    conn = None

    try:
        pin_val = _normalize_pin(pinnkood)
        conn = _connect()
        cursor = conn.cursor()
        row = _fetchone(cursor, 'SELECT nimi FROM `Pintable` WHERE pinnkood = ?', (pin_val,))

        if row:
            return True, str(row[0])

        logging.warning(
            f'(DB Handler) nime_kaeve_pintabelist: PIN code {pinnkood} not found in Pintable'
        )
        return False, None

    except Exception as e:
        logging.error(f'(DB Handler) nime_kaeve_pintabelist: Error: {e}')
        return False, None

    finally:
        if conn:
            conn.close()


def get_unreturned_drinks(nfc_input):
    """
    Returns all unreturned drinks for user NFC.

    Output shape: [(productname, barcode, date_taken), ...]
    """
    conn = None

    try:
        conn = _connect()
        cursor = conn.cursor()

        user_id = _get_user_id(cursor, nfc_input)
        if user_id is None:
            logging.warning(
                f'(DB Handler) get_unreturned_drinks: User not found with NFC ID {nfc_input}'
            )
            return []

        rows = _fetchall(
            cursor,
            '''
            SELECT productname, barcode, date_taken
            FROM `Transactions`
            WHERE userid = ? AND date_returned IS NULL
            ORDER BY date_taken ASC
            ''',
            (user_id,),
        )

        if rows:
            logging.info(
                f'(DB Handler) get_unreturned_drinks: Found {len(rows)} unreturned items '
                f'for user {user_id} ({nfc_input})'
            )
        else:
            logging.info(
                f'(DB Handler) get_unreturned_drinks: No unreturned items found '
                f'for user {user_id} ({nfc_input})'
            )

        return rows

    except Exception as e:
        logging.error(f'(DB Handler) get_unreturned_drinks: Error: {e}')
        return []

    finally:
        if conn:
            conn.close()


def keep_stock(scanned_barcodes, action_type):
    """
    Updates stock counts for scanned barcodes.

    - action_type='taken'    -> decrement stock
    - action_type='returned' -> increment stock
    """
    conn = None

    if action_type == 'taken':
        adjustment = -1
    elif action_type == 'returned':
        adjustment = 1
    else:
        logging.error(
            f"(DB Handler) keep_stock: Invalid action_type '{action_type}'. Must be 'taken' or 'returned'."
        )
        return False

    if not scanned_barcodes:
        return True

    try:
        conn = _connect()
        cursor = conn.cursor()
        _execute(cursor, 'BEGIN')

        for barcode in scanned_barcodes:
            _execute(
                cursor,
                'UPDATE `Products` SET stock = COALESCE(stock, 0) + ? WHERE barcode = ?',
                (adjustment, str(barcode)),
            )

        conn.commit()
        logging.info(
            f'(DB Handler) keep_stock: Updated stock for {len(scanned_barcodes)} items. Action: {action_type}'
        )
        return True

    except Exception as e:
        logging.error(f'(DB Handler) keep_stock: Error: {e}')
        if conn:
            _rollback_safely(conn)
        return False

    finally:
        if conn:
            conn.close()


def record_drink_session(nfc_input, action_type, scanned_barcodes):
    """
    Atomically records a full drink session and stock update.

    action_type:
    - 'taken': insert open transactions and decrement stock.
    - 'returned': close existing open transactions and increment stock.

    Returns True only when all transaction rows and all stock updates commit
    together. On any failure, nothing is written.
    """
    conn = None

    if action_type == 'taken':
        stock_adjustment = -1
    elif action_type == 'returned':
        stock_adjustment = 1
    else:
        logging.error(
            f"(DB Handler) record_drink_session: Invalid action_type '{action_type}'."
        )
        return False

    if not scanned_barcodes:
        logging.info('(DB Handler) record_drink_session: No items to record.')
        return True

    try:
        conn = _connect()
        cursor = conn.cursor()
        _execute(cursor, 'BEGIN')

        user_id = _get_user_id(cursor, nfc_input)
        if user_id is None:
            logging.error(
                f'(DB Handler) record_drink_session: User not found with NFC ID {nfc_input}'
            )
            _rollback_safely(conn)
            return False

        timestamp = _now_sql_timestamp()

        for barcode in scanned_barcodes:
            barcode = str(barcode)
            product_name = _get_product_name(cursor, barcode)
            if not product_name:
                logging.warning(
                    f'(DB Handler) record_drink_session: Product not found with barcode {barcode}.'
                )
                _rollback_safely(conn)
                return False

            if action_type == 'taken':
                _execute(
                    cursor,
                    '''
                    INSERT INTO `Transactions` (userid, productname, date_taken, date_returned, barcode)
                    VALUES (?, ?, ?, NULL, ?)
                    ''',
                    (user_id, product_name, timestamp, barcode),
                )
            else:
                row = _fetchone(
                    cursor,
                    '''
                    SELECT rental_id
                    FROM `Transactions`
                    WHERE userid = ? AND barcode = ? AND date_returned IS NULL
                    ORDER BY date_taken ASC
                    LIMIT 1
                    ''',
                    (user_id, barcode),
                )

                if not row:
                    logging.warning(
                        f'(DB Handler) record_drink_session: User {user_id} attempted to return '
                        f'barcode {barcode} without an open transaction.'
                    )
                    _rollback_safely(conn)
                    return False

                _execute(
                    cursor,
                    'UPDATE `Transactions` SET date_returned = ? WHERE rental_id = ?',
                    (timestamp, int(row[0])),
                )

            _execute(
                cursor,
                'UPDATE `Products` SET stock = COALESCE(stock, 0) + ? WHERE barcode = ?',
                (stock_adjustment, barcode),
            )
            if cursor.rowcount == 0:
                logging.warning(
                    f'(DB Handler) record_drink_session: Stock row not found for barcode {barcode}.'
                )
                _rollback_safely(conn)
                return False

        conn.commit()
        logging.info(
            f'(DB Handler) record_drink_session: Committed {len(scanned_barcodes)} '
            f'items for user {user_id}. Action: {action_type}'
        )
        return True

    except Exception as e:
        logging.error(f'(DB Handler) record_drink_session: Error: {e}')
        if conn:
            _rollback_safely(conn)
        return False

    finally:
        if conn:
            conn.close()


def update_user_nfc(nfc_input, nfc_uus):
    """
    Replaces a user's old NFC id with a new NFC id.

    Returns True on success, False otherwise.
    """
    conn = None

    try:
        conn = _connect()
        cursor = conn.cursor()

        existing = _fetchone(cursor, 'SELECT userid FROM `users` WHERE nfcid = ?', (str(nfc_uus),))
        if existing:
            logging.warning(
                f'(DB Handler) update_user_nfc: New NFC ID {nfc_uus} is already in use.'
            )
            return False

        _execute(cursor, 'UPDATE `users` SET nfcid = ? WHERE nfcid = ?', (str(nfc_uus), str(nfc_input)))

        if cursor.rowcount == 0:
            logging.warning(
                f'(DB Handler) update_user_nfc: No user found with NFC ID {nfc_input}'
            )
            return False

        conn.commit()
        logging.info(
            f'(DB Handler) update_user_nfc: Updated NFC ID from {nfc_input} to {nfc_uus}'
        )
        return True

    except Exception as e:
        logging.error(f'(DB Handler) update_user_nfc: Error: {e}')
        if conn:
            _rollback_safely(conn)
        return False

    finally:
        if conn:
            conn.close()


def register_new_card(uus_nfc, nimi):
    """
    Finds a user by name and assigns a new NFC ID.

    Returns True on success, False on failure.
    """
    conn = None

    try:
        conn = _connect()
        cursor = conn.cursor()

        existing = _fetchone(cursor, 'SELECT userid FROM `users` WHERE nfcid = ?', (str(uus_nfc),))
        if existing:
            logging.warning(
                f'(DB Handler) register_new_card: New NFC ID {uus_nfc} is already in use.'
            )
            return False

        _execute(cursor, 'UPDATE `users` SET nfcid = ? WHERE name = ?', (str(uus_nfc), str(nimi)))

        if cursor.rowcount == 0:
            logging.warning(f'(DB Handler) register_new_card: No user found with name {nimi}')
            return False

        conn.commit()
        logging.info(f'(DB Handler) register_new_card: Assigned new NFC {uus_nfc} to user {nimi}')
        return True

    except Exception as e:
        logging.error(f'(DB Handler) register_new_card: Error: {e}')
        if conn:
            _rollback_safely(conn)
        return False

    finally:
        if conn:
            conn.close()


def register_new_card_by_pin(uus_nfc, pinnkood):
    """
    Assigns a replacement card for the registered user represented by a PIN.

    The legacy schema links Pintable to users by name, so this function refuses
    to update when the name is missing or ambiguous instead of silently changing
    multiple users with the same name.
    """
    conn = None

    try:
        pin_val = _normalize_pin(pinnkood)
        conn = _connect()
        cursor = conn.cursor()

        pin_row = _fetchone(
            cursor,
            'SELECT nimi, isregistered FROM `Pintable` WHERE pinnkood = ?',
            (pin_val,),
        )
        if not pin_row:
            logging.warning(f'(DB Handler) register_new_card_by_pin: PIN not found: {pinnkood}')
            return False, None

        name = str(pin_row[0])
        if not bool(pin_row[1]):
            logging.warning(
                f'(DB Handler) register_new_card_by_pin: PIN {pinnkood} is not registered yet.'
            )
            return False, name

        existing = _fetchone(cursor, 'SELECT userid FROM `users` WHERE nfcid = ?', (str(uus_nfc),))
        if existing:
            logging.warning(
                f'(DB Handler) register_new_card_by_pin: NFC ID {uus_nfc} is already in use.'
            )
            return False, name

        matches = _fetchall(cursor, 'SELECT userid FROM `users` WHERE name = ?', (name,))
        if len(matches) != 1:
            logging.error(
                f'(DB Handler) register_new_card_by_pin: Expected exactly one user named {name}, '
                f'found {len(matches)}.'
            )
            return False, name

        user_id = int(matches[0][0])
        _execute(cursor, 'UPDATE `users` SET nfcid = ? WHERE userid = ?', (str(uus_nfc), user_id))
        conn.commit()
        logging.info(
            f'(DB Handler) register_new_card_by_pin: Assigned new NFC {uus_nfc} to user {user_id} ({name})'
        )
        return True, name

    except Exception as e:
        logging.error(f'(DB Handler) register_new_card_by_pin: Error: {e}')
        if conn:
            _rollback_safely(conn)
        return False, None

    finally:
        if conn:
            conn.close()


def add_product(name, barcode):
    conn = None

    try:
        conn = _connect()
        cursor = conn.cursor()
        existing = _fetchone(cursor, 'SELECT productid FROM `Products` WHERE barcode = ?', (str(barcode),))
        if existing:
            logging.warning(f'(DB Handler) add_product: Barcode already exists: {barcode}')
            return False

        _execute(
            cursor,
            'INSERT INTO `Products` (barcode, name, stock, weight) VALUES (?, ?, ?, ?)',
            (str(barcode), str(name), 0, 0.0),
        )
        conn.commit()
        return True

    except Exception as e:
        logging.error(f'(DB Handler) add_product: Error adding product: {e}')
        if conn:
            _rollback_safely(conn)
        return False

    finally:
        if conn:
            conn.close()


def get_all_products():
    conn = _connect()

    try:
        cursor = conn.cursor()
        rows = _fetchall(
            cursor,
            'SELECT productid, name, barcode FROM `Products` ORDER BY name',
        )
        return rows

    finally:
        conn.close()


def remove_product(product_id):
    conn = _connect()

    try:
        cursor = conn.cursor()
        _execute(cursor, 'DELETE FROM `Products` WHERE productid = ?', (product_id,))
        conn.commit()
        return cursor.rowcount > 0

    finally:
        conn.close()
