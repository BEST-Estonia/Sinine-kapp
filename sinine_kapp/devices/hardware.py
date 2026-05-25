"""
Compatibility facade for older imports.

New code should import from the specific device modules:
- sinine_kapp.devices.barcode_scanner
- sinine_kapp.devices.nfc_reader
- sinine_kapp.devices.door
"""

from .barcode_scanner import find_barcode_device, list_keyboard_devices, read_barcode
from .door import cleanup, init_sensor, is_open, open_door
from .nfc_reader import read_tag, read_tag_details


def get_barcode(timeout=10, device_path=None):
    """Compatibility wrapper around barcode_scanner.read_barcode()."""
    return read_barcode(timeout=timeout, device_path=device_path)


def get_nfc(cancel_check_callback=None):
    """Compatibility wrapper around nfc_reader.read_tag()."""
    return read_tag(cancel_check_callback=cancel_check_callback)


def Ukse_avaja():
    """Compatibility wrapper around door.open_door()."""
    return open_door()


def init_door_sensor():
    """Compatibility wrapper around door.init_sensor()."""
    return init_sensor()


def is_door_open():
    """Compatibility wrapper around door.is_open()."""
    return is_open()
