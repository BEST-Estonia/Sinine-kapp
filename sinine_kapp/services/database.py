import json
import logging
import os
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from ..paths import ENV_FILE

_ENV_LOADED = False
_LAST_CONNECTION_ERROR: str | None = None
_DEFAULT_TIMEOUT_SECONDS = 8


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
                '(API DB Handler) Loaded environment values from %s (overwrite=%s)',
                candidate,
                overwrite,
            )

    _ENV_LOADED = True


def _request_timeout() -> int:
    raw_value = os.environ.get('SININE_KAPP_API_TIMEOUT', '').strip()
    if not raw_value:
        return _DEFAULT_TIMEOUT_SECONDS

    try:
        return max(1, int(raw_value))
    except ValueError:
        logging.warning(
            '(API DB Handler) Invalid SININE_KAPP_API_TIMEOUT=%r, using %s seconds',
            raw_value,
            _DEFAULT_TIMEOUT_SECONDS,
        )
        return _DEFAULT_TIMEOUT_SECONDS


def _api_base_url() -> str:
    _load_environment_once()
    base_url = os.environ.get('SININE_KAPP_API_BASE_URL', '').strip().rstrip('/')
    if not base_url:
        raise RuntimeError(
            'SININE_KAPP_API_BASE_URL is missing. Set it to the portal API URL, '
            'for example http://192.168.88.154:3000'
        )
    return base_url


def _api_key() -> str:
    _load_environment_once()
    api_key = os.environ.get('SININE_KAPP_DEVICE_API_KEY', '').strip()
    if not api_key:
        raise RuntimeError('SININE_KAPP_DEVICE_API_KEY is missing.')
    return api_key


def last_connection_error() -> str | None:
    return _LAST_CONNECTION_ERROR


def _api_request(path: str, method: str = 'GET', payload: dict[str, Any] | None = None):
    global _LAST_CONNECTION_ERROR

    body = None
    headers = {
        'Accept': 'application/json',
        'X-Sinine-Kapp-Key': _api_key(),
    }

    if payload is not None:
        body = json.dumps(payload).encode('utf-8')
        headers['Content-Type'] = 'application/json'

    url = f'{_api_base_url()}/sinine-kapp{path}'
    request = Request(url, data=body, headers=headers, method=method)

    try:
        with urlopen(request, timeout=_request_timeout()) as response:
            raw_body = response.read().decode('utf-8')
            _LAST_CONNECTION_ERROR = None
            if not raw_body:
                return None
            return json.loads(raw_body)
    except HTTPError as exc:
        raw_error = exc.read().decode('utf-8', errors='replace')
        message = raw_error or str(exc)
        try:
            parsed = json.loads(raw_error)
            message = parsed.get('error') or parsed.get('message') or message
        except json.JSONDecodeError:
            pass
        _LAST_CONNECTION_ERROR = f'HTTP {exc.code}: {message}'
        raise RuntimeError(_LAST_CONNECTION_ERROR) from exc
    except URLError as exc:
        _LAST_CONNECTION_ERROR = str(exc.reason)
        raise RuntimeError(_LAST_CONNECTION_ERROR) from exc
    except Exception as exc:
        _LAST_CONNECTION_ERROR = str(exc)
        raise


def _quote(value: Any) -> str:
    return quote(str(value), safe='')


def check_connection() -> tuple[bool, str]:
    try:
        _api_request('/kiosk/health')
        return True, f'connected to portal API at {_api_base_url()}'
    except Exception as exc:
        return False, str(exc)


def checkuser(UID):
    try:
        data = _api_request(f'/kiosk/users/by-nfc/{_quote(UID)}')
        return bool(data.get('exists')), data.get('name')
    except Exception as e:
        logging.error(f'(API DB Handler) checkuser: Error: {e}')
        return False, None


def get_drink_info(barcode):
    try:
        data = _api_request(f'/kiosk/products/by-barcode/{_quote(barcode)}')
        return bool(data.get('exists')), data.get('name')
    except Exception as e:
        logging.error(f'(API DB Handler) get_drink_info: Error: {e}')
        return False, None


def log_user_returned_drinks(nfc_input, list_of_barcodes):
    try:
        data = _api_request(
            '/kiosk/returned',
            method='POST',
            payload={
                'nfcid': str(nfc_input),
                'barcodes': [str(barcode) for barcode in list_of_barcodes],
            },
        )
        return bool(data.get('success'))
    except Exception as e:
        logging.error(f'(API DB Handler) log_user_returned_drinks: Error: {e}')
        return False


def create_new_user(nfc_input, pinnkood):
    try:
        data = _api_request(
            '/kiosk/users/register',
            method='POST',
            payload={'nfcid': str(nfc_input), 'pinnkood': int(pinnkood)},
        )
        return bool(data.get('success'))
    except Exception as e:
        logging.error(f'(API DB Handler) create_new_user: Error: {e}')
        return False


def log_user_taken_drinks(nfc_input, list_of_barcodes):
    try:
        data = _api_request(
            '/kiosk/taken',
            method='POST',
            payload={
                'nfcid': str(nfc_input),
                'barcodes': [str(barcode) for barcode in list_of_barcodes],
            },
        )
        return bool(data.get('success'))
    except Exception as e:
        logging.error(f'(API DB Handler) log_user_taken_drinks: Error: {e}')
        return False


def check_pin_code_dict(pinnkood):
    try:
        data = _api_request(
            '/kiosk/pins/exists',
            method='POST',
            payload={'pinnkood': int(pinnkood)},
        )
        return bool(data.get('exists'))
    except Exception as e:
        logging.error(f'(API DB Handler) check_pin_code_dict: Error: {e}')
        return False


def is_user_registered(pinnkood):
    try:
        data = _api_request(
            '/kiosk/pins/registered',
            method='POST',
            payload={'pinnkood': int(pinnkood)},
        )
        return bool(data.get('registered'))
    except Exception as e:
        logging.error(f'(API DB Handler) is_user_registered: Error: {e}')
        return False


def nime_kaeve_pintabelist(pinnkood):
    try:
        data = _api_request(f'/kiosk/pins/{_quote(int(pinnkood))}/name')
        return bool(data.get('found')), data.get('name')
    except Exception as e:
        logging.error(f'(API DB Handler) nime_kaeve_pintabelist: Error: {e}')
        return False, None


def get_pin_status(pinnkood):
    exists = check_pin_code_dict(pinnkood)
    if _LAST_CONNECTION_ERROR is not None:
        return {'exists': False, 'registered': False, 'name': None}

    if not exists:
        return {'exists': False, 'registered': False, 'name': None}

    registered = is_user_registered(pinnkood)
    if _LAST_CONNECTION_ERROR is not None:
        return {'exists': True, 'registered': False, 'name': None}

    found, name = nime_kaeve_pintabelist(pinnkood)
    if _LAST_CONNECTION_ERROR is not None:
        return {'exists': True, 'registered': registered, 'name': None}

    return {'exists': found, 'registered': registered, 'name': name}


def get_unreturned_drinks(nfc_input):
    try:
        data = _api_request(f'/kiosk/users/{_quote(nfc_input)}/unreturned')
        return data.get('items', [])
    except Exception as e:
        logging.error(f'(API DB Handler) get_unreturned_drinks: Error: {e}')
        return []


def keep_stock(scanned_barcodes, action_type):
    """
    Stock is updated atomically by the portal API transaction endpoints.

    This compatibility function remains because the controller still calls it
    after logging take/return transactions.
    """
    return True


def record_drink_session(nfc_input, action_type, list_of_barcodes):
    if action_type == 'taken':
        return log_user_taken_drinks(nfc_input, list_of_barcodes)
    if action_type == 'returned':
        return log_user_returned_drinks(nfc_input, list_of_barcodes)

    logging.error(f'(API DB Handler) record_drink_session: Unknown action type: {action_type}')
    return False


def update_user_nfc(nfc_input, nfc_uus):
    try:
        data = _api_request(
            '/kiosk/users/nfc',
            method='PUT',
            payload={'oldNfcid': str(nfc_input), 'newNfcid': str(nfc_uus)},
        )
        return bool(data.get('success'))
    except Exception as e:
        logging.error(f'(API DB Handler) update_user_nfc: Error: {e}')
        return False


def register_new_card(uus_nfc, nimi):
    try:
        data = _api_request(
            '/kiosk/users/register-card',
            method='POST',
            payload={'nfcid': str(uus_nfc), 'name': str(nimi)},
        )
        return bool(data.get('success'))
    except Exception as e:
        logging.error(f'(API DB Handler) register_new_card: Error: {e}')
        return False


def register_new_card_by_pin(uus_nfc, pinnkood):
    status = get_pin_status(pinnkood)
    if _LAST_CONNECTION_ERROR is not None:
        return False, None

    if not status['exists']:
        return False, None

    if status['registered']:
        success = register_new_card(uus_nfc, status['name'])
    else:
        success = create_new_user(uus_nfc, pinnkood)

    return success, status['name'] if success else None


def add_product(name, barcode):
    try:
        data = _api_request(
            '/kiosk/products/admin',
            method='POST',
            payload={'name': str(name), 'barcode': str(barcode)},
        )
        return bool(data.get('success'))
    except Exception as e:
        logging.error(f'(API DB Handler) add_product: Error adding product: {e}')
        return False


def get_all_products():
    try:
        data = _api_request('/kiosk/products/admin')
        return data.get('products', [])
    except Exception as e:
        logging.error(f'(API DB Handler) get_all_products: Error: {e}')
        return []


def get_debtors():
    try:
        data = _api_request('/kiosk/debtors')
        return data.get('debtors', [])
    except Exception as e:
        logging.error(f'(API DB Handler) get_debtors: Error: {e}')
        return []


def remove_product(product_id):
    try:
        _api_request(f'/kiosk/products/admin/{_quote(product_id)}', method='DELETE')
        return True
    except Exception as e:
        logging.error(f'(API DB Handler) remove_product: Error: {e}')
        return False
