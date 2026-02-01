# Sinine Kapp - Smart Beverage Cabinet 🍺

A Raspberry Pi-based smart beverage cabinet with NFC authentication, barcode tracking, and touchscreen interface. Now with **vertical kiosk mode** and **laptop development mode**!

## 🆕 What's New

### Vertical Kiosk Display (1080x1920)
- Modern fast-food kiosk aesthetic
- Large touch-friendly buttons (800px wide)
- Bright, clean iOS-style color scheme
- Portrait orientation optimized layout
- Professional typography (28pt - 120pt)

### Mock Mode for Laptop Development
- No Raspberry Pi hardware required
- Keyboard input for NFC cards (just type the ID)
- Keyboard input for barcodes (just type the barcode)
- Mock LCD display (console output)
- Easy development and testing on any laptop

## 🚀 Quick Start

### Option 1: Raspberry Pi (Hardware Mode)

1. **Install dependencies:**
```bash
sudo apt install python3-rpi-lgpio python3-spidev
pip install pygame Pillow mfrc522 opencv-python pyzbar
```

2. **Configure for hardware:**
- Set `MOCK_MODE = False` in `hardware_handler.py`
- Uncomment fullscreen in `drawer.py` line 1181

3. **Run:**
```bash
python main.py
```

### Option 2: Laptop (Development Mode) 💻

1. **Install dependencies:**
```bash
pip install pygame Pillow
```

2. **Enable mock mode:**
- Set `MOCK_MODE = True` in `hardware_handler.py` (already set by default)
- Or check the auto-detection works (it should!)

3. **Run:**
```bash
python main.py
```

4. **Use keyboard input:**
   - When prompted for NFC: Type any number (e.g., `12345`) and press Enter
   - When prompted for barcode: Type the barcode (e.g., `4740098000334`) and press Enter

📖 **See [LAPTOP_MODE.md](LAPTOP_MODE.md) for detailed development instructions**

## 📁 Project Structure

### Core Files

- **`main.py`** - Main application logic and workflow orchestration
- **`drawer.py`** - All UI screens and touchscreen handling (1080x1920 vertical)
- **`hardware_handler.py`** - Hardware abstraction (NFC, barcode, GPIO) with mock mode
- **`database_handler.py`** - SQLite database operations
- **`styles.py`** - Modern color scheme and typography
- **`ui_components.py`** - Reusable UI components (buttons, etc.)
- **`lcd.py`** - Small LCD display driver (inside cabinet)

### Configuration & Docs

- **`config.ini`** - Configuration file for easy settings
- **`LAPTOP_MODE.md`** - Complete guide for laptop development
- **`test_mock_mode.py`** - Automated testing for mock mode
- **`requirements-dev.txt`** - Development dependencies

### Database

- **`database.db`** - SQLite database with:
  - `users` - User accounts (NFC ID, name)
  - `Pintable` - PIN codes and names
  - `Products` - Available drinks (barcode, name, stock)
  - `Transactions` - Rental history

## 🎨 UI Design

### Color Scheme (Modern Kiosk Style)
```python
PRIMARY    = (0, 122, 255)    # iOS blue
SUCCESS    = (52, 199, 89)    # Bright green
DANGER     = (255, 59, 48)    # Red
WARNING    = (255, 149, 0)    # Orange
BACKGROUND = (255, 255, 255)  # Clean white
```

### Screen Layout (1080x1920)
- **Top section** (y=200-400): Titles and headers
- **Content area** (y=500-1400): Main content
- **Bottom section** (y=1600-1800): Action buttons

## 🖥️ How It Works

### User Flow

1. **Welcome Screen** → User taps "Login sisse"
2. **NFC Authentication** → User scans their NFC card
3. **Choice Screen** → Take drinks or Return drinks
4. **Door Opens** → User takes/returns beverages
5. **Live Scanning** → Barcodes scanned in real-time
6. **Door Closes** → Transaction saved to database
7. **Summary Screen** → Shows what was taken/returned
8. **Back to Welcome** → Ready for next user

### Multiprocessing Architecture

The application uses two processes:
- **Main Process** (`main.py`): Business logic and hardware control
- **GUI Process** (`drawer.py`): Display rendering and touch input

Communication via two queues:
- **command_queue**: Main → GUI (what to display)
- **reply_queue**: GUI → Main (user input)

## 🔧 Development

### Mock Mode Features

**NFC Card Input:**
```
=== MOCK NFC READER ===
Enter NFC card ID: 12345
```

**Barcode Scanner:**
```
=== MOCK BARCODE SCANNER ===
Enter barcode: 4740098000334
```

**LCD Display:**
```
[LCD Mock] Display: Skaneeri tooted...
[LCD Mock] Screen cleared
```

### Testing

Run the test suite:
```bash
python test_mock_mode.py
```

All modules should import successfully and report:
```
✓ All core modules import successfully
✓ Mock mode is configured and ready
✓ Application structure is valid
```

### Screen Resolution Options

For laptop development, you can change the resolution in `drawer.py`:

```python
# Full vertical kiosk (may not fit on laptop):
screen = pygame.display.set_mode((1080, 1920))

# Half size for easier viewing:
screen = pygame.display.set_mode((540, 960))

# Fullscreen (for actual kiosk):
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
```

## 📋 Requirements

### Raspberry Pi Hardware Mode
- Raspberry Pi 5 (or compatible)
- 1.9" ST7789 TFT LCD display
- RC522 NFC/RFID reader
- Raspberry Pi Camera (for barcode scanning)
- Door lock mechanism (GPIO controlled)
- Touchscreen display (1080x1920 recommended)

### Laptop Development Mode
- Any computer with Python 3.8+
- Pygame installed
- That's it! No hardware needed.

## 🔐 Hardware Pinout (Raspberry Pi)

See README.md lines 84-110 for detailed pinout configuration.

Key connections:
- **NFC Reader**: SPI (CE0), GPIO 08 (SDA), GPIO 25 (RST)
- **LCD Display**: SPI, GPIO 24 (CS), GPIO 27 (DC), GPIO 22 (RST)
- **Camera**: Camera connector
- **Door**: GPIO (configurable)

## 🐛 Troubleshooting

**"Raspberry Pi GPIO libraries not available"**
- This is normal in mock mode - the application auto-detects and switches to keyboard input

**Screen too large for laptop**
- Edit `drawer.py` line 1180: Change to `(540, 960)` for half-size window

**Door doesn't close**
- Mock door timer is 15 seconds - wait or change `_DOOR_DURATION` in `hardware_handler.py`

**"Module not found" errors**
- Make sure you've installed dependencies: `pip install pygame Pillow`

## 📝 License

This is an educational project. Check with the repository owner for usage rights.

## 🤝 Contributing

The project is now easier to develop thanks to mock mode! To contribute:

1. Fork the repository
2. Enable mock mode (`MOCK_MODE = True`)
3. Make your changes and test with `test_mock_mode.py`
4. Create a pull request

## 🎯 Features

✅ NFC card authentication  
✅ Barcode scanning for drink tracking  
✅ Real-time inventory management  
✅ User account system with PIN codes  
✅ Transaction history logging  
✅ Modern vertical kiosk UI (1080x1920)  
✅ Touch-friendly interface  
✅ Mock mode for laptop development  
✅ Keyboard input simulation  
✅ Automatic hardware detection  

## 📞 Support

- For setup help, see [LAPTOP_MODE.md](LAPTOP_MODE.md)
- For hardware pinout, see the Hardware section above
- For code structure, see the original README comments (lines 12-111)

---

**Sinine Kapp** - Making beverage management smart and easy! 🍻
