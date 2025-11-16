# Smart Cupboard - Complete Pygame Touchscreen Application

A comprehensive Python-based touchscreen UI application for managing a smart drink cupboard with RFID authentication, QR code scanning, and inventory management. This system runs on a Raspberry Pi with a touchscreen display (600×1024 portrait) and provides a complete, production-ready interface for lending and returning beverages.

## Features

### Core Functionality
- **Touch-Optimized Pygame UI**: Full-screen 600×1024 portrait mode with multi-screen navigation
- **User Authentication**: RFID card scanning with user registration
- **Inventory Management**: QR code scanning for borrowing and returning items
- **Multi-Item Basket**: Scan multiple items at once with quantity management
- **Transaction Logging**: Complete history of all borrows and returns
- **Due Date Tracking**: Automatic due date calculation (first Wednesday of next month)
- **Admin Panel**: Comprehensive admin tools for managing users, inventory, and viewing logs

### UI Components
- **On-Screen Keyboard**: Touch-friendly keyboard for user registration
- **Modern Button Design**: Rounded corners, shadows, hover effects, and press animations
- **Sneaky Character**: Friendly monkey mascot appearing on every screen
- **Professional Color Scheme**: Teal primary, soft red secondary, gradient backgrounds
- **Responsive Layouts**: All screens optimized for 600×1024 portrait touchscreen

### Screens
1. **Main Menu**: 4 main options (Open Doors, Return Drink, Admin, Stock/Inventory)
2. **Card Scan**: RFID authentication with visual feedback
3. **User Registration**: New user registration with on-screen keyboard
4. **QR Scan**: Multi-item scanning with basket management
5. **Basket Review**: View, adjust quantities, remove items before confirming
6. **Thank You**: Transaction confirmation with due date display
7. **Admin Main**: Admin panel dashboard
8. **Admin Users**: View all registered users, tap for details
9. **Admin User Details**: View user's borrowed items and overdue status
10. **Admin Inventory**: Adjust stock levels with +/− buttons
11. **Admin Logs**: Chronological transaction history

## Project Structure

```
Sinine-kapp/
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── test_new_app.py              # Comprehensive test suite
├── assets/                       # Images and resources
│   └── sneaky.png               # Character mascot image
├── src/                         # Main application code
│   ├── main.py                  # Entry point (NEW modular version)
│   ├── screen_manager.py        # Centralized screen navigation
│   ├── database/                # Database layer
│   │   ├── __init__.py
│   │   ├── manager.py           # DatabaseManager (comprehensive CRUD)
│   │   ├── user_db.py           # Legacy user database (kept for compatibility)
│   │   └── cupboard.db          # SQLite database (auto-generated)
│   ├── ui/                      # Reusable UI components
│   │   ├── __init__.py
│   │   ├── buttons.py           # Enhanced button widget
│   │   ├── input_box.py         # Text input widget
│   │   └── keyboard.py          # On-screen keyboard
│   ├── screens/                 # Screen classes
│   │   ├── __init__.py
│   │   ├── base_screen.py       # Base class and utilities
│   │   ├── main_menu.py         # Main menu screen
│   │   ├── card_scan.py         # Card scanning screen
│   │   ├── register_user.py     # User registration screen
│   │   ├── qr_scan.py           # QR code scanning with basket
│   │   ├── basket.py            # Basket confirmation screen
│   │   ├── thank_you.py         # Thank you/completion screen
│   │   ├── admin_main.py        # Admin panel main
│   │   ├── admin_users.py       # Admin users list
│   │   ├── admin_user_details.py # Admin user details
│   │   ├── admin_inventory.py   # Admin inventory manager
│   │   └── admin_logs.py        # Admin system logs
│   └── hardware/                # Hardware abstraction layer
│       ├── mock_rfid.py         # Mock RFID reader
│       ├── mock_qr.py           # Mock QR scanner
│       ├── mock_scales.py       # Mock weight scales
│       └── mock_camera.py       # Mock camera
├── tests/                       # Test suite
│   └── test_integration.py      # Integration tests (legacy)
├── .github/
│   └── workflows/
│       └── deploy.yml           # GitHub Actions deployment
└── linux/
    └── smart-cupboard.service  # Systemd service file
```

## Database Schema

### Users Table
- `id`: INTEGER PRIMARY KEY
- `name`: TEXT (user's name)
- `card_id`: TEXT UNIQUE (RFID card number)
- `is_admin`: BOOLEAN (admin flag)
- `created_at`: TIMESTAMP

### Items Table
- `qr_code`: TEXT PRIMARY KEY (unique item identifier)
- `name`: TEXT (item name)
- `created_at`: TIMESTAMP

### Stock Table
- `qr_code`: TEXT PRIMARY KEY (references items)
- `quantity`: INTEGER (current stock level)
- `updated_at`: TIMESTAMP

### Borrows Table
- `id`: INTEGER PRIMARY KEY
- `user_id`: INTEGER (references users)
- `qr_code`: TEXT (references items)
- `timestamp_out`: TEXT (when borrowed)
- `timestamp_returned`: TEXT NULL (when returned, if applicable)
- `due_date`: TEXT (calculated due date)

## Setup Instructions

### Local Development (Windows/Linux/Mac)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/BEST-Estonia/Sinine-kapp.git
   cd Sinine-kapp
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   cd src
   python main.py
   ```

5. **Run tests**:
   ```bash
   python test_new_app.py
   ```

### Testing the Application

**Sample Users** (for card scanning):
- Card `1` → Admin User (admin privileges) ✓
- Card `2` → Alice Johnson ✓
- Card `3` → Bob Smith ✓
- Card `999` → Not registered (will prompt for registration)

**Sample Items** (for QR scanning):
- `DRINK001` → Coca Cola
- `DRINK002` → Sprite
- `DRINK003` → Orange Juice
- `DRINK004` → Water
- `DRINK005` → Energy Drink
- `DRINK006` → Iced Tea
- `DRINK007` → Lemonade

**Mock Hardware**:
- When prompted for RFID, enter card number in console
- When prompted for QR code, enter item code in console
- All hardware interactions are simulated

### Raspberry Pi Setup

1. **Install Raspberry Pi OS** (with desktop) on your SD card

2. **Update the system**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

3. **Install Python dependencies**:
   ```bash
   sudo apt install -y python3-pip python3-venv
   ```

4. **Clone the repository on the Pi**:
   ```bash
   cd /home/pi
   git clone https://github.com/BEST-Estonia/Sinine-kapp.git smart-cupboard
   cd smart-cupboard
   ```

5. **Create virtual environment and install dependencies**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

6. **Test the application manually**:
   ```bash
   cd src
   python main.py
   ```

7. **Set up automatic startup with systemd**:
   ```bash
   sudo cp linux/smart-cupboard.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable smart-cupboard.service
   sudo systemctl start smart-cupboard.service
   ```

## Configuration

### Display Resolution

The default resolution is **600×1024 (portrait mode)**. To change this, edit `src/main.py`:

```python
SCREEN_W, SCREEN_H = 600, 1024  # Portrait orientation
```

Common resolutions:
- 600×1024 (portrait mode for 7" displays) - **current default**
- 480×800 (portrait mode for smaller 7" touchscreens)
- 800×480 (landscape mode for 7" Pi touchscreen)
- 1080×1920 (full HD portrait)

### Mock Hardware vs Real Hardware

To integrate real hardware, replace the mock modules in `src/hardware/`:

```python
# Example: Real RFID reader
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

Then update `src/main.py` imports.

## Architecture

### Modular Design

The application follows a clean, modular architecture:

- **UI Components** (`ui/`): Reusable widgets (buttons, input boxes, keyboard)
- **Screens** (`screens/`): Individual screen classes with specific functionality
- **Database** (`database/`): Centralized data management with CRUD operations
- **Hardware** (`hardware/`): Hardware abstraction layer for easy device swapping

### Screen Navigation Flow

```
Main Menu
├── Open Doors → Card Scan → QR Scan → Basket → Thank You
├── Return Drink → Card Scan → QR Scan → Basket → Thank You
├── Admin Panel → Card Scan (admin only) → Admin Main
│   ├── Users List → User Details
│   ├── Inventory Manager
│   └── System Logs
└── Stock/Inventory → View stock levels
```

### Key Features Implementation

**Due Date Calculation**: Automatically calculated as the first Wednesday of the next month
```python
db.calculate_due_date()  # Returns: "2025-12-03"
```

**Transaction Logging**: Every borrow/return is logged with timestamps
```python
db.borrow_item(user_id, qr_code)  # Creates transaction, updates stock
db.return_item(user_id, qr_code)  # Updates transaction, restores stock
```

**Multi-Item Basket**: Scan multiple items before confirming
```python
# In QR scan screen, items are added to basket
basket = [
    {'qr_code': 'DRINK001', 'name': 'Coca Cola', 'quantity': 2},
    {'qr_code': 'DRINK002', 'name': 'Sprite', 'quantity': 1}
]
```

## Development

### Adding New Screens

1. Create a new file in `src/screens/`
2. Inherit from `BaseScreen`
3. Implement `draw()`, `handle_event()`, and `update()` methods
4. Add to `src/screens/__init__.py`
5. Add screen routing in `src/main.py`

Example:
```python
from screens.base_screen import BaseScreen, TEAL, WHITE
from ui.buttons import Button

class NewScreen(BaseScreen):
    def __init__(self, ui_manager):
        super().__init__(ui_manager)
        self.buttons = [
            Button((30, 400, 540, 80), "Click Me", TEAL, WHITE)
        ]
    
    def on_button_click(self, button):
        return "main"  # Navigate to main menu
    
    def draw(self, surface):
        self.draw_common_elements(surface)  # Background + Sneaky
        # Draw your UI here
        for btn in self.buttons:
            btn.draw(surface)
```

### Testing

Run the comprehensive test suite:
```bash
python test_new_app.py
```

This tests:
- All imports
- Database operations (CRUD, transactions, due dates)
- Screen instantiation
- UI components

## License

This project is part of BEST Estonia's initiatives.

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

---

**Enjoy your Smart Cupboard with Sneaky! 🐵🚀**
