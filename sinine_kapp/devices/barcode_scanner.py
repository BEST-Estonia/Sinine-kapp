"""Direct USB keyboard-style barcode scanner reader.

The main pygame app captures scanner input through keyboard events while the
touchscreen process is active. This module is still useful for standalone tools
and for direct reads from /dev/input/by-id devices.
"""

import logging
import os
import select
import struct
import time
from pathlib import Path


# ---------------------------------------------------------------------------
# Linux input constants
# ---------------------------------------------------------------------------

INPUT_BY_ID_DIR = Path("/dev/input/by-id")
INPUT_EVENT_FORMAT = "llHHI"
INPUT_EVENT_SIZE = struct.calcsize(INPUT_EVENT_FORMAT)
EV_KEY = 0x01
KEY_DOWN = 1
KEY_ENTER = 28
KEY_KPENTER = 96
KEY_BACKSPACE = 14

KEYCODE_TO_CHAR = {
    2: "1",
    3: "2",
    4: "3",
    5: "4",
    6: "5",
    7: "6",
    8: "7",
    9: "8",
    10: "9",
    11: "0",
    12: "-",
    13: "=",
    16: "q",
    17: "w",
    18: "e",
    19: "r",
    20: "t",
    21: "y",
    22: "u",
    23: "i",
    24: "o",
    25: "p",
    26: "[",
    27: "]",
    30: "a",
    31: "s",
    32: "d",
    33: "f",
    34: "g",
    35: "h",
    36: "j",
    37: "k",
    38: "l",
    39: ";",
    40: "'",
    43: "\\",
    44: "z",
    45: "x",
    46: "c",
    47: "v",
    48: "b",
    49: "n",
    50: "m",
    51: ",",
    52: ".",
    53: "/",
    55: "*",
    57: " ",
    71: "7",
    72: "8",
    73: "9",
    74: "-",
    75: "4",
    76: "5",
    77: "6",
    78: "+",
    79: "1",
    80: "2",
    81: "3",
    82: "0",
    83: ".",
}


# ---------------------------------------------------------------------------
# Device discovery
# ---------------------------------------------------------------------------

def list_keyboard_devices() -> list[Path]:
    """Return keyboard-like input devices exposed through /dev/input/by-id."""
    if not INPUT_BY_ID_DIR.exists():
        return []

    return sorted(INPUT_BY_ID_DIR.glob("*-event-kbd"))


def find_barcode_device(device_path: str | None = None) -> Path | None:
    """Pick the most likely barcode scanner input device."""
    if device_path:
        path = Path(device_path)
        return path if path.exists() else None

    candidates = list_keyboard_devices()
    if not candidates:
        return None

    preferred_keywords = (
        "barcode",
        "scanner",
        "honeywell",
        "symbol",
        "datalogic",
        "usb_adapter",
        "usb-device",
    )

    for candidate in candidates:
        label = candidate.name.lower()
        if any(keyword in label for keyword in preferred_keywords):
            return candidate

    if len(candidates) == 1:
        return candidates[0]

    for candidate in candidates:
        label = candidate.name.lower()
        if "logitech" not in label and "hdmi" not in label:
            return candidate

    return candidates[0]


# ---------------------------------------------------------------------------
# Barcode read loop
# ---------------------------------------------------------------------------

def read_barcode(timeout: float = 10.0, device_path: str | None = None) -> str | None:
    """Read one barcode from a keyboard-like Linux input device."""
    device = find_barcode_device(device_path)
    if device is None:
        logging.warning("No barcode scanner input device found")
        return None

    deadline = time.monotonic() + timeout
    buffer: list[str] = []

    fd = os.open(device, os.O_RDONLY | os.O_NONBLOCK)
    try:
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return None

            readable, _, _ = select.select([fd], [], [], remaining)
            if not readable:
                return None

            event_bytes = os.read(fd, INPUT_EVENT_SIZE * 32)
            if not event_bytes:
                continue

            # Input events arrive as fixed-size binary structs. Barcode
            # scanners usually emit normal key-down events plus Enter.
            for offset in range(0, len(event_bytes), INPUT_EVENT_SIZE):
                chunk = event_bytes[offset : offset + INPUT_EVENT_SIZE]
                if len(chunk) != INPUT_EVENT_SIZE:
                    continue

                _, _, event_type, event_code, event_value = struct.unpack(
                    INPUT_EVENT_FORMAT, chunk
                )

                if event_type != EV_KEY or event_value != KEY_DOWN:
                    continue

                if event_code in (KEY_ENTER, KEY_KPENTER):
                    if buffer:
                        return "".join(buffer)
                    continue

                if event_code == KEY_BACKSPACE:
                    if buffer:
                        buffer.pop()
                    continue

                character = KEYCODE_TO_CHAR.get(event_code)
                if character is not None:
                    buffer.append(character)
    finally:
        os.close(fd)
