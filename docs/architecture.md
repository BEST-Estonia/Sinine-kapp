# System Design

## Goals
- Provide a touch-friendly kiosk UI on a 7" display for lending and returning drinks from a communal fridge/closet.
- Track the inventory of drink SKUs, quantities, and per-container pricing.
- Associate users to RFID tags; log every lending/return event tied to a user and timestamp.
- Operate offline using a lightweight SQL database (SQLite) while keeping hooks for migrating to a remote server later.

## Hardware and OS Assumptions
- Raspberry Pi-class single board computer running Raspberry Pi OS or similar Linux distribution.
- 7" touchscreen (800x480 or 1024x600). Application runs in kiosk/fullscreen mode using Tkinter.
- USB RFID reader exposing tag IDs over a serial interface; PySerial used to read tag scans.

## Software Components
1. **UI Layer (`ui/main_window.py`)**
   - Tkinter window sized to match the touchscreen resolution.
   - Three main views: inventory overview, lend/return form, and activity log.
   - Virtual keypad modal for amount entry to keep it touch-friendly.
2. **Application Services (`services/`)
   - `InventoryService` handles drink CRUD, quantity updates, and ensures stock does not drop below zero.
   - `TransactionService` records each lend/return event and calculates outstanding balances.
   - `RFIDService` listens to scans, resolves them to known users, and publishes events to the UI via callbacks.
3. **Data Access Layer (`data/`)
   - `database.py` bootstraps SQLite (file path configurable) and applies schema migrations.
   - Tables:
     - `drinks(id, name, description, unit_volume_ml, unit_price, quantity_on_hand)`
     - `users(id, name, rfid_tag, email)`
     - `transactions(id, user_id, drink_id, quantity, action, created_at)` where `action` is `lend` or `return`.
4. **RFID Integration (`hardware/rfid_reader.py`)**
   - Abstract class `BaseReader` plus concrete `SerialRFIDReader` that consumes a serial port stream.
   - Emits callbacks when a full tag UID is parsed; keeps the hardware-specific code isolated.
5. **Configuration (`config.py`)**
   - Central location for database path, serial port, baud rate, and UI layout constants.

## Data Flow
1. User taps "Scan RFID"; the reader starts listening and, upon scan, resolves the user.
2. UI shows the user name and allows selecting a drink + quantity. Balance preview is computed.
3. Confirming the lend/return updates the database (transaction + inventory) within a SQLite transaction.
4. Activity log refreshes to show the latest event; optional notification overlay confirms the action.

## Extensibility
- API boundary between services and UI allows future migration to another framework (e.g., Qt or web UI).
- Database migrations live under `migrations/` so schema can evolve without data loss.
- RFID reader abstraction allows swapping in networked readers or mock readers for development/testing.

