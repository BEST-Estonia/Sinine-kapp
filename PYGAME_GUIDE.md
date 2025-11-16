# Pygame UI Implementation Guide

## Overview

This implementation provides a complete Raspberry Pi touchscreen UI with:
- Mock SQL database for user management
- 4 main functions: Open doors, Return drink, Admin, Stock/Inventory
- RFID card authentication
- Full-screen separate windows for each function
- Visual feedback and navigation

## Features Implemented

### 1. Mock SQL Database
- **Location**: `src/database/user_db.py`
- **Database file**: `src/database/users.db` (auto-generated, excluded from git)
- **Pre-populated users**:
  - Card 1: Alice Johnson
  - Card 2: Bob Smith
  - Card 3: Charlie Brown

### 2. Main Screen
- **Character mascot**: Blue cupboard character displayed on left
- **Message**: "Please pick an option"
- **4 buttons**:
  - Open doors (requires card scan)
  - Return drink (requires card scan)
  - Admin (requires card scan)
  - Stock/Inventory (direct access, no card required)

### 3. Screen Navigation
Each button opens a **full-screen separate window** (not just status updates):
- Smooth transitions between screens
- Back button on each sub-screen to return to main menu
- State management for user session

### 4. Card Scanning & Verification
When clicking "Open doors", "Return drink", or "Admin":
1. User is shown a card scan screen
2. RFID reader prompts for card number (console input for mock)
3. Database checks if card is registered:
   - **Registered**: Shows "Welcome, [Name]!" and proceeds to the function
   - **Not registered**: Shows "Access denied! Card [number] not registered."
4. User can click "Back" to cancel and return to main menu

### 5. Screen Details

#### Open Doors Screen
- Displays user name after successful card scan
- Shows "Door unlocked! Please take your item."
- Displays weight readings from top and bottom shelves
- Back button to return to main menu

#### Return Drink Screen
- Displays user name after successful card scan
- Prompts for QR code scan
- Shows "Return registered! QR: [code]" when complete
- Back button to return to main menu

#### Admin Panel
- Displays user name after successful card scan
- Shows list of all registered users with their card numbers
- Back button to return to main menu

#### Stock/Inventory Screen
- **No card scan required** - direct access
- Shows inventory list with visual quantity bars:
  - Green bars for healthy stock (>5 units)
  - Red bars for low stock (≤5 units)
- Back button to return to main menu

## File Structure

```
src/
├── app/
│   ├── ui_pygame.py          # Main UI manager
│   └── screens.py             # All screen classes
├── database/
│   ├── __init__.py
│   ├── user_db.py             # Database manager
│   └── users.db               # SQLite database (auto-generated)
├── hardware/
│   ├── mock_rfid.py           # Mock RFID reader
│   ├── mock_qr.py             # Mock QR scanner
│   ├── mock_scales.py         # Mock weight scales
│   └── mock_camera.py         # Mock camera
└── main.py                    # Application entry point

assets/
└── character.png              # Character mascot image
```

## How to Use

### Testing with Mock RFID

When prompted "MOCK: enter RFID UID (or blank to cancel):" in the console:
- Enter `1`, `2`, or `3` for registered users
- Enter any other number for access denial demo
- Press Enter without typing to cancel

### Testing with Mock QR

When prompted "MOCK: enter QR code (or blank to cancel):" in the console:
- Enter any text to simulate a QR code
- Press Enter without typing to cancel

### Running the Application

```bash
cd src
python main.py
```

## Code Architecture

### Modular Design

The code follows a modular architecture with clear separation of concerns:

1. **Screen Classes** (`src/app/screens.py`):
   - `BaseScreen`: Base class for all screens
   - `MainScreen`: Main menu
   - `CardScanScreen`: Reusable card scanning screen
   - `OpenDoorsScreen`: Door access screen
   - `ReturnDrinkScreen`: Drink return screen
   - `AdminScreen`: Admin panel
   - `StockInventoryScreen`: Inventory view

2. **UI Manager** (`src/app/ui_pygame.py`):
   - Manages screen transitions
   - Handles database connection
   - Coordinates hardware interactions
   - Main game loop

3. **Database** (`src/database/user_db.py`):
   - SQLite database wrapper
   - User CRUD operations
   - Sample data population

4. **Hardware Abstraction** (`src/hardware/`):
   - Mock implementations for development
   - Easy to replace with real hardware drivers

### Button Widget

The `Button` class provides:
- Visual feedback (hover effects)
- Rounded corners
- Center-aligned text
- Click detection

### Screen Lifecycle

1. Screen is created with reference to UI manager
2. `handle_event()` processes user input
3. `update()` performs state updates (e.g., auto-scan)
4. `draw()` renders the screen
5. Returns screen transition commands as needed

## Customization

### Adding New Users

Users can be added programmatically:

```python
from database import UserDatabase

db = UserDatabase()
db.add_user("4", "New User Name")
db.close()
```

### Changing Colors

Edit color constants in `src/app/screens.py`:

```python
WHITE = (255, 255, 255)
BLUE = (100, 150, 255)
GREEN = (50, 200, 100)
RED = (255, 80, 80)
# etc.
```

### Adjusting Screen Resolution

The UI is optimized for **portrait orientation** (480×800). Edit `SCREEN_W` and `SCREEN_H` in `src/app/ui_pygame.py`:

```python
SCREEN_W, SCREEN_H = 480, 800  # Portrait orientation (change to your display resolution)
```

For landscape orientation, you may need to adjust button layouts in `screens.py`.

## Integration with Real Hardware

To use real RFID readers, QR scanners, or scales:

1. Create new classes in `src/hardware/` that match the mock interface
2. Update imports in `src/main.py`

Example for real RFID reader:

```python
# src/hardware/real_rfid.py
import serial

class RFIDReader:
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600):
        self.serial = serial.Serial(port, baudrate)
    
    def read(self):
        try:
            line = self.serial.readline().decode('ascii').strip()
            return line if line else None
        except Exception as e:
            print(f"RFID read error: {e}")
            return None
```

Then in `src/main.py`:

```python
from hardware.real_rfid import RFIDReader  # Changed from MockRFIDReader
```

## Known Limitations

- Mock RFID/QR inputs via console (expected for development)
- ALSA audio warnings can be ignored (no audio used)
- Database is local SQLite (suitable for single-device use)

## Future Enhancements

Potential improvements:
- User registration screen with name input
- Transaction logging
- Network sync for multi-device setups
- Touch keyboard for text input
- User photos/avatars
- Statistics dashboard
