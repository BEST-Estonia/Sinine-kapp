"""MFRC522 NFC reader access used by the controller."""

import time
from typing import Callable

from mfrc522 import SimpleMFRC522


CancelCallback = Callable[[], bool]


def read_tag(cancel_check_callback: CancelCallback | None = None) -> int | None:
    """Block until an NFC tag UID is read or cancellation is requested."""
    reader = SimpleMFRC522()
    try:
        while True:
            tag_id, _text = reader.read_no_block()
            if tag_id:
                return tag_id
            if cancel_check_callback and cancel_check_callback():
                return None
            time.sleep(0.1)
    finally:
        pass


def read_tag_details(cancel_check_callback: CancelCallback | None = None) -> tuple[int | None, str]:
    """Block until a tag is read and return both UID and stored text."""
    reader = SimpleMFRC522()
    try:
        while True:
            tag_id, text = reader.read_no_block()
            if tag_id:
                return tag_id, (text or "").strip()
            if cancel_check_callback and cancel_check_callback():
                return None, ""
            time.sleep(0.1)
    finally:
        pass
