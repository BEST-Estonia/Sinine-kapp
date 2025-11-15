# Sinine Kapp Drink Lending Kiosk

Python-based touchscreen UI for lending beverages from a shared closet/fridge. The app pairs an RFID tag with each user, keeps an SQLite inventory + transaction log, and runs full screen on a 7" display (800×480 or 1024×600).

## Features
- Touch-friendly Tkinter UI with on-screen keypad for entering lend/return quantities.
- Offline-friendly SQLite database storing drinks, users, and per-transaction logs.
- RFID abstraction that supports both real serial readers (via `pyserial`) and a mock mode for development without hardware.
- Recent-activity feed so staff can audit usage at a glance.
- Configurable resolution + ports through environment variables (see `sinine_kapp/config.py`).

## Hardware & OS Assumptions
- Raspberry Pi or similar single-board computer running Raspberry Pi OS (Wayland or X11 works).
- Official 7" Pi touchscreen or comparable 1024×600 HDMI display.
- USB/UART RFID reader that outputs tag IDs as ASCII plus newline.

## Getting Started
1. **Install Python 3.11+** on your device.
2. **Create a virtual environment** (optional but recommended):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
3. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```
4. **Run the kiosk UI** (the `src` directory is used as the module root):
   ```powershell
   $env:PYTHONPATH = "src"
   python -m sinine_kapp.app
   ```
   On Linux:
   ```bash
   export PYTHONPATH=src
   python -m sinine_kapp.app
   ```

The first launch seeds a couple of sample users/drinks so you can test immediately. When `SININE_MOCK_RFID=true` (default) you’ll see a "Simulate RFID" box for entering a fake tag.

## Display & Kiosk Mode Tips
- Set `SININE_DISPLAY_WIDTH`/`SININE_DISPLAY_HEIGHT` to match your 7" panel (e.g. `800` × `480`).
- On Raspberry Pi OS, add a systemd service that activates the virtual env and runs `python -m sinine_kapp.app` at boot.
- For kiosk-style fullscreen, you can hide the window chrome by adding `self.attributes('-fullscreen', True)` inside `MainWindow` once you are ready.

## Database Layout
The schema lives in `sinine_kapp/data/database.py` (and mirrored in `migrations/0001_initial.sql`):
- `users`: RFID-tagged members.
- `drinks`: Inventory with quantity, volume and pricing metadata.
- `transactions`: Immutable log storing who lent/returned what and when.

The database file defaults to `data/sinine_kapp.db` (relative to the repo). You can point it elsewhere with `SININE_DB_PATH`.

## RFID Integration
- Set `SININE_RFID_PORT` (e.g. `/dev/ttyUSB0`) and optionally `SININE_RFID_BAUD` once hardware is connected.
- Switch off mock mode with `SININE_MOCK_RFID=false` to activate the real serial reader (`pyserial` handles reconnection).
- The `RFIDService` publishes scans into the UI; unregistered tags show a warning so you can enroll them from an admin script later.

## Additional Notes
- Detailed architecture/flow notes live in `docs/architecture.md`.
- The codebase is intentionally modular (`services/`, `hardware/`, `ui/`) so you can swap the UI framework or persist data remotely later.
- For production, consider adding authentication for admin tasks (enrolling tags, editing prices) and syncing transactions to a central server.
