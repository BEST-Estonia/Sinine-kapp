# Sinine Kapp

Raspberry Pi application for a smart drink cabinet with:
- touchscreen UI
- NFC login
- barcode-based drink tracking
- door sensor input
- small LCD feedback
- portal API-backed user/product data

## Project Layout

```text
Sinine-kapp/
├── assets/                  UI assets
├── docs/                    Extra notes and guides
├── tools/                   Small hardware test scripts
├── sinine_kapp/
│   ├── app/                 Main cabinet flow and process orchestration
│   ├── devices/             Hardware integrations (GPIO, NFC, LCD)
│   ├── services/            Portal API access
│   ├── ui/                  Pygame touchscreen UI
│   ├── __main__.py          `python -m sinine_kapp`
│   └── paths.py             Shared project paths
├── main.py                  Thin entrypoint
├── launch                   Boot/autostart launcher
├── launch.sh                Manual launcher
└── requirements.txt
```

## Core Modules

- [sinine_kapp/app/controller.py](/home/skpi/Sinine-kapp/Sinine-kapp/sinine_kapp/app/controller.py) owns the cabinet workflow, queues, and UI process.
- [sinine_kapp/ui/touchscreen.py](/home/skpi/Sinine-kapp/Sinine-kapp/sinine_kapp/ui/touchscreen.py) runs the fullscreen touchscreen UI in a separate process.
- [sinine_kapp/devices/hardware.py](/home/skpi/Sinine-kapp/Sinine-kapp/sinine_kapp/devices/hardware.py) is a thin compatibility facade for older imports.
- [sinine_kapp/devices/barcode_scanner.py](/home/skpi/Sinine-kapp/Sinine-kapp/sinine_kapp/devices/barcode_scanner.py) contains barcode scanner device discovery and raw input reading.
- [sinine_kapp/devices/nfc_reader.py](/home/skpi/Sinine-kapp/Sinine-kapp/sinine_kapp/devices/nfc_reader.py) contains NFC reader access.
- [sinine_kapp/devices/door.py](/home/skpi/Sinine-kapp/Sinine-kapp/sinine_kapp/devices/door.py) contains door sensor and door actuator helpers.
- [sinine_kapp/devices/lcd.py](/home/skpi/Sinine-kapp/Sinine-kapp/sinine_kapp/devices/lcd.py) controls the small LCD.
- [sinine_kapp/services/database.py](/home/skpi/Sinine-kapp/Sinine-kapp/sinine_kapp/services/database.py) contains the portal API client used by the cabinet flow.

## Running

Install Python dependencies:

```bash
pip install -r requirements.txt
sudo apt install python3-rpi-lgpio python3-spidev
```

Start the app from the repo root:

```bash
python3 main.py
```

or:

```bash
python3 -m sinine_kapp
```

## Local And SSH Launch

The touchscreen UI is written so it can start:
- from a local Pi session
- from an SSH / VS Code SSH shell

If the SSH shell has no display variables, the UI now falls back to:
- `DISPLAY=:0`
- `XAUTHORITY=~/.Xauthority`
- `XDG_RUNTIME_DIR=/run/user/<uid>`

That means SSH launch works as long as the Pi already has a local graphical session running.

## Hardware Pin Overview

This is the quickest code-based wiring overview I could extract from the repo and its current RFID library defaults.

### LCD Display

Defined in [sinine_kapp/devices/lcd.py](/home/skpi/Sinine-kapp/Sinine-kapp/sinine_kapp/devices/lcd.py):

- `GPIO24` / physical pin `18`: LCD chip select (`CS`)
- `GPIO27` / physical pin `13`: LCD data/command (`DC`)
- `GPIO22` / physical pin `15`: LCD reset (`RST`)
- `GPIO26` / physical pin `37`: LCD backlight control
- `SPI0 SCLK` / physical pin `23`: shared SPI clock via `board.SPI()`
- `SPI0 MOSI` / physical pin `19`: shared SPI MOSI via `board.SPI()`
- `SPI0 MISO` / physical pin `21`: shared SPI MISO via `board.SPI()`

### Door Sensor

Defined in [sinine_kapp/devices/door.py](/home/skpi/Sinine-kapp/Sinine-kapp/sinine_kapp/devices/door.py):

- `GPIO21` / physical pin `40`: door sensor input

Current logic:
- pulled up internally with `GPIO.PUD_UP`
- `LOW` means door closed
- `HIGH` means door open

### NFC Reader

Used through [sinine_kapp/devices/nfc_reader.py](/home/skpi/Sinine-kapp/Sinine-kapp/sinine_kapp/devices/nfc_reader.py), which relies on `SimpleMFRC522()`.

These pins are inferred from the currently installed `mfrc522` library defaults, not declared directly in this repo:

- `SPI0 CE0` / `GPIO8` / physical pin `24`: MFRC522 chip select
- `SPI0 SCLK` / physical pin `23`: shared SPI clock
- `SPI0 MOSI` / physical pin `19`: shared SPI MOSI
- `SPI0 MISO` / physical pin `21`: shared SPI MISO
- `GPIO22` / physical pin `15`: MFRC522 reset pin default when using BCM mode

### Barcode Scanner

There are no Raspberry Pi GPIO pins for the barcode scanner in the codebase.

Defined in [sinine_kapp/devices/barcode_scanner.py](/home/skpi/Sinine-kapp/Sinine-kapp/sinine_kapp/devices/barcode_scanner.py):

- expected as a USB HID keyboard-style input device
- read through `/dev/input/by-id/*-event-kbd`

### Touchscreen

There are no GPIO pins defined for the touchscreen in this repo.

The UI code treats it as a display + pointer device managed by Linux / pygame:
- fullscreen window in [sinine_kapp/ui/touchscreen.py](/home/skpi/Sinine-kapp/Sinine-kapp/sinine_kapp/ui/touchscreen.py)
- touch events received as `pygame.MOUSEBUTTONDOWN`

### Important Note

Based on the current code and library defaults, `GPIO22` is used by both:
- LCD reset
- MFRC522 reset

That overlap may be intentional hardware sharing, or it may be a wiring/configuration conflict worth verifying on the real cabinet.

## Portal API Setup

Create `.env` in the repo root. The Raspberry Pi cabinet calls the `portaal`
API, and the API writes to MySQL.

```env
SININE_KAPP_API_BASE_URL=http://PORTAAL_HOST_OR_IP:3000
SININE_KAPP_DEVICE_API_KEY=THE_SAME_SECRET_AS_PORTAAL
SININE_KAPP_API_TIMEOUT=8
```

The same `SININE_KAPP_DEVICE_API_KEY` must be set in `portaal/.env`.

Test from the Pi:

```bash
curl -H "X-Sinine-Kapp-Key: THE_SAME_SECRET_AS_PORTAAL" \
  http://PORTAAL_HOST_OR_IP:3000/sinine-kapp/kiosk/health
```

## Utility Scripts

- [tools/barcodetest.py](/home/skpi/Sinine-kapp/Sinine-kapp/tools/barcodetest.py)
- [tools/nfctest.py](/home/skpi/Sinine-kapp/Sinine-kapp/tools/nfctest.py)
- [tools/gpio4test.py](/home/skpi/Sinine-kapp/Sinine-kapp/tools/gpio4test.py)

These are not part of the main application flow.

- `barcodetest.py` reads directly from the scanner input device, so it works for scanner troubleshooting even over SSH.
- `nfctest.py` waits for one NFC tag at a time and prints the UID and text.
- `gpio4test.py` only checks the door sensor state.

## UI Flow

- [docs/ui_screen_flow.md](/home/skpi/Sinine-kapp/Sinine-kapp/docs/ui_screen_flow.md) maps the current touchscreen paths with Mermaid diagrams.
- [docs/ui_architecture.md](/home/skpi/Sinine-kapp/Sinine-kapp/docs/ui_architecture.md) explains the reusable UI helpers and preferred screen pattern.

## Current Direction

This cleanup keeps the current cabinet behavior but makes the repo easier to read:
- root contains entrypoints and top-level assets only
- runtime code lives inside one package
- device code, UI code, and data access are separated by folder
- launch scripts point to one application entrypoint

There is still room to keep splitting the large controller and touchscreen modules later, but the project is now structured so that work can happen module-by-module instead of inside one flat repo root.
