# Laptop Development Mode (Mock Mode)

This guide explains how to run Sinine Kapp on a laptop for development and testing.

## Setup

### 1. Enable Mock Mode

Open `hardware_handler.py` and set:

```python
MOCK_MODE = True
```

This allows the application to run without Raspberry Pi hardware (NFC reader, camera, GPIO).

### 2. Install Dependencies

```bash
# Install Python dependencies
pip install pygame Pillow

# Note: sqlite3 is included in Python's standard library - no need to install
```

**Note**: You don't need RPi.GPIO, mfrc522, opencv, or pyzbar when MOCK_MODE is enabled.

## Running the Application

```bash
python main.py
```

The application will start with a **1080x1920** vertical kiosk display. On most laptops, you may want to change this in `drawer.py`:

```python
# For windowed mode (easier on laptop):
screen = pygame.display.set_mode((1080, 1920))

# For fullscreen:
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
```

## Using Mock Hardware

### NFC/RFID Card Reader

When the application asks you to scan an NFC card, you'll see:

```
=== MOCK NFC READER ===
Enter NFC card ID (numbers only) and press Enter:
Example: 12345 or 67890
>
```

**How to use:**
- Type any numeric ID (e.g., `12345`)
- Press Enter

**Test IDs** (check database.db for registered users):
- Look in the `users` table for existing `nfcid` values
- Or register a new user with a PIN code

### Barcode Scanner

When scanning drinks, you'll see:

```
=== MOCK BARCODE SCANNER ===
Enter barcode and press Enter (timeout: 10s):
Example: 4740098000334
Press Enter without typing to skip
>
```

**How to use:**
- Type the barcode number (e.g., `4740098000334`)
- Press Enter
- Press Enter without typing to skip/timeout

**Test Barcodes** (check database.db):
- Look in the `Products` table for available barcodes
- Example: `4740098000334`, `4740098000341`, etc.

## Screen Resolution

The application now uses a **vertical kiosk layout** (1080x1920 pixels):
- Designed to look like a fast-food self-service kiosk
- Large, touch-friendly buttons
- Modern color scheme
- Clear typography

If your laptop screen is smaller, you can:
1. Run in windowed mode and scroll
2. Use a virtual desktop/workspace
3. Temporarily change resolution in `drawer.py` line 1179-1180

## Development Tips

### Testing Workflows

**User Registration:**
1. Click "Loo uus kasutaja" or "Login sisse, tahan juua"
2. Enter NFC ID when prompted (e.g., `99999`)
3. Enter PIN code from the `Pintable` (check database.db)
4. Complete registration

**Taking Drinks:**
1. Login with registered NFC ID
2. Select "VÕTA JOOK"
3. Enter barcodes when prompted
4. Close door (wait for timeout)

**Returning Drinks:**
1. Login with registered NFC ID that has unreturned drinks
2. Select "TOO TAGASI"
3. Enter barcodes when prompted
4. Close door (wait for timeout)

### Database

The SQLite database `database.db` contains:
- `users`: User accounts (nfcid, name)
- `Pintable`: PIN codes and names
- `Products`: Available drinks (barcode, name, stock)
- `Transactions`: Drink rental history

Use any SQLite browser to:
- View test data
- Add new products
- Add new users
- Check transaction history

### Common Issues

**"Raspberry Pi GPIO libraries not available"**
- This is expected in mock mode - it's automatically handled

**Screen too large for laptop**
- Edit `drawer.py` line 1180: `screen = pygame.display.set_mode((540, 960))`
- This creates a half-size window that's easier to view

**Door doesn't close**
- The mock door timer is set to 15 seconds in `hardware_handler.py`
- Wait for the timeout, or change `_DOOR_DURATION` to a shorter value

## Switching Back to Hardware Mode

When deploying to Raspberry Pi:

1. Set `MOCK_MODE = False` in `hardware_handler.py`
2. Uncomment fullscreen in `drawer.py`:
   ```python
   screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
   ```
3. Ensure hardware dependencies are installed:
   ```bash
   sudo apt install python3-rpi-lgpio python3-spidev
   pip install mfrc522 opencv-python pyzbar
   ```

## Features in Vertical Kiosk Mode

✅ Modern fast-food kiosk aesthetic  
✅ Large touch-friendly buttons (800px wide)  
✅ Bright, clean color scheme  
✅ Clear typography at 48-120pt  
✅ 1080x1920 vertical layout  
✅ Proper spacing for touch screens  
✅ Card icons and visual feedback  
✅ Live cart display while scanning  

Enjoy developing! 🎉
