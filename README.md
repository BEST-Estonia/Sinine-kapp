# SININE KAPP - Smart Beverage Vending Cabinet
A modular Python application for automated drink dispensing with NFC authentication, barcode scanning, door detection, and touchscreen UI. This project demonstrates enterprise-grade architecture patterns suitable for embedded systems and IoT applications.

## QUICK START

### Installation
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   sudo apt install python3-rpi-lgpio python3-spidev
   ```

2. Configure fullscreen mode in `drawer.py` (optional):
   - Find in `run_touchscreen()` function:
     ```python
     screen = pygame.display.set_mode((800, 600))
     #screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
     ```
   - Replace with (for full display):
     ```python
     #screen = pygame.display.set_mode((800, 600))
     screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
     ```

3. Run the application:
   ```bash
   python3 main.py
   ```

### Shared Database Setup (Pi -> portaal MySQL)
Use this when you want the Raspberry Pi app and `portaal` web app to read/write the same Sinine Kapp tables.

1. Install one MySQL Python driver:
   ```bash
   pip install mysql-connector-python
   # or
   pip install pymysql
   ```
2. Create `Sinine-kapp/.env` (or set environment variables on the Pi):
   ```env
   DATABASE_URL=mysql://USER:PASSWORD@HOST:3306/laravel
   SININE_KAPP_DB_BACKEND=mysql
   ```
3. Keep `SININE_KAPP_DB_BACKEND=auto` (default) if you want fallback to local `database.db` when `DATABASE_URL` is missing.

`database_handler.py` now keeps the same function API for `main.py`, but chooses backend like this:
- `mysql` when `SININE_KAPP_DB_BACKEND=mysql` or when `DATABASE_URL` exists in `auto` mode
- `sqlite` when `SININE_KAPP_DB_BACKEND=sqlite` or when `DATABASE_URL` is missing in `auto` mode
## ARCHITECTURE OVERVIEW

### Design Philosophy
This project demonstrates a **modular, multi-process architecture** for embedded systems where:
- **Separation of Concerns:** Each module handles one responsibility (UI, hardware, database, business logic)
- **Readability:** Main logic (`main.py`) remains clean; complex operations are delegated to specialized modules
- **Maintainability:** Similar projects can reuse patterns for GPIO control, inter-process communication, and UI rendering
- **Scalability:** Easy to add new hardware sensors, database backends, or UI screens
- **Non-Blocking Operations:** Hardware operations don't freeze the UI

### Core Pattern: Producer-Consumer with Multiprocessing Queues

Two multiprocessing queues handle all communication between business logic and UI:

```python
command_queue = multiprocessing.Queue()  # Main → UI process
reply_queue = multiprocessing.Queue()    # UI process → Main
```

**Command Queue Flow:**
```python
# Main process sends commands (non-blocking)
command_queue.put(("SCREEN_NAME", data))
```

**Reply Queue Flow:**
```python
# UI process sends user input (non-blocking)
reply_queue.put(user_action)

# Main process receives (blocking or timeout)
response = reply_queue.get(timeout=30)
```

### Multiprocess Architecture Diagram

```
┌──────────────────────────────────────────────────────────┐
│ MAIN LOGIC PROCESS (main.py)                             │
│ ├─ User authentication (NFC reader)                      │
│ ├─ Drink selection logic                                 │
│ ├─ Hardware control (door, backlight, scale)             │
│ ├─ Database transactions                                 │
│ └─ Queue management                                      │
│                                                           │
│ Non-blocking: Sends commands, doesn't wait for UI       │
└────────────────────┬─────────────────────────────────────┘
                     │ command_queue.put(("SCREEN", data))
                     │ Returns IMMEDIATELY - doesn't block
                     ↓
┌──────────────────────────────────────────────────────────┐
│ UI RENDERING PROCESS (drawer.py)                         │
│ ├─ Pygame-based touchscreen rendering                    │
│ ├─ Button interactivity and event detection              │
│ ├─ User input capture                                    │
│ └─ Real-time screen updates                              │
│                                                           │
│ Non-blocking: Sends input, doesn't wait for logic       │
└────────────────────┬─────────────────────────────────────┘
                     │ reply_queue.put(user_input)
                     │ Returns IMMEDIATELY - doesn't block
                     ↓
              ┌─────────────────┐
              │ Main continues  │
              │ without waiting │
              └─────────────────┘
```

### Why Multiprocessing?
- **UI Responsiveness:** Hardware operations (NFC reading, door sensing) don't freeze touchscreen
- **Parallel Execution:** Main logic and UI rendering happen simultaneously
- **Clean Separation:** Business logic and presentation are completely decoupled

## MODULE REFERENCE

### 1. main.py - Business Logic
The heart of the application. Handles all user flows, authentication, and hardware coordination. Deliberately kept readable by delegating complex tasks to other modules.

**Key Functions:**
- `main_loop()` - Main control loop that manages the overall flow
  - Initializes hardware (door sensor)
  - Spawns UI process with queue communication
  - Listens for user actions from touchscreen
  - Orchestrates application logic

- `joogi_väljastus(nfc_input)` - Handle drink dispensing flow
  - Opens cabinet door
  - Displays live cart of scanned items
  - Monitors door sensor until closed
  - Processes transaction

- `joogi_tagastus(nfc_input)` - Handle drink return flow
  - Similar to dispensing but reverses the logic
  - Tracks returned items

- `GUI_*()` functions - Queue-based UI commands
  - Example: `GUI_live_cart(items)` sends cart data to UI
  - Pattern: `command_queue.put(("COMMAND_NAME", data))`
  - Returns immediately (non-blocking)

**Design Pattern:**
```python
# Example: Display a message and wait for user confirmation
GUI_message("Scan your item", show_button=True)
try:
    response = reply_queue.get(timeout=30)  # Wait max 30 seconds
except queue.Empty:
    # Handle timeout - user didn't respond in time
```

### 2. hardware_handler.py - Hardware Interface Layer
Isolates all hardware operations from main logic. Handles GPIO, NFC reader, door sensors, and scales. Returns simple Python values to keep main.py clean.

**Key Functions:**
- `init_door_sensor()` - Initialize GPIO 21 door detection
  - Sets up pull-up resistor
  - Called once at startup

- `is_door_open()` - Read door sensor state
  - Returns `True` if door is open (floating/HIGH)
  - Returns `False` if door closed (connected to GND/LOW)
  - Called in main loop to detect when door closes

- `get_nfc(cancel_check_callback)` - Block until NFC card is read
  - Returns card UID as integer
  - Supports cancellation via callback

- `get_wheight()` - Get scale reading
  - Mock implementation in demo

**Hardware Details:**
```
GPIO 21 with pull-up:
- Ground connection = Door CLOSED = LOW = is_door_open() → False
- Floating = Door OPEN = HIGH = is_door_open() → True
```

### 3. database_handler.py - Data Persistence
Manages all database operations. Uses SQLite for simplicity. Called by main.py for authentication, product lookup, and transaction recording.

**Key Functions:**
- `checkuser(nfc_uid)` - Verify user registration
  - Returns `(True/False, user_name)`

- `get_drink_info(barcode)` - Look up drink by barcode
  - Returns drink name or error status

- `create_new_user(nfc_uid, pin_code)` - Register new user

- `update_user_nfc(old_uid, new_uid)` - Update lost cards

### 4. drawer.py - UI Rendering Engine
Manages all touchscreen display and user input. Runs in separate process. Receives commands from main.py via queue and returns user input via reply queue.

**Architecture:**
- `run_touchscreen(command_q, reply_q)` - Main UI loop
  - Starts with DEFAULT screen
  - Polls command_q for new screens to display
  - Sends user input to reply_q
  - Runs continuously in separate process

**Screen Classes:**
Each screen (tervitus_kuva, Joogiväljastus_kuva, etc.) is a separate class that:
- Renders graphics using pygame
- Detects button clicks
- Sends input back to main process via reply_q

**Design Pattern:**
```python
# Main sends command
command_queue.put(("VALIKUVAADE", user_name))

# UI displays choice screen and waits for click
# User clicks button
# UI sends response
reply_queue.put("1")  # or "2"

# Main receives input
choice = reply_queue.get()
```

See `Front_end_juhend.txt` for detailed UI documentation.

### 5. ui_components.py - UI Component Library
Reusable GUI components (buttons, text fields, etc.). Acts as a "Toolbox" for drawer.py.

**Key Classes:**
- `Button` - Interactive button
  - Handles drawing and click detection
  - Returns command ID when clicked
  - Configurable position, text, color

### 6. styles.py - Design System
Centralized styling definitions (colors, fonts). Ensures consistent look across all screens.

**Key Classes:**
- `Colors` - Color definitions (e.g., `Colors.GREEN`, `Colors.RED`)
- `FontManager` - Font management (e.g., `fonts.header`, `fonts.body`)

### 7. lcd.py - Internal LCD Display
Manages the 1.9" ST7789 LCD display inside the cabinet. Works independently of touchscreen to show real-time status (e.g., "Scanning items..." or product names).

**Key Functions:**
- `show_message(text)` - Display text on internal LCD
  - Non-blocking operation
  - Can be called during drink scanning

- `set_backlight(True/False)` - Control LCD backlight
  - GPIO 26 controls power
  - Turns on when dispensing, off when idle

**Hardware Details:**
- Uses Adafruit library for ST7789 display
- SPI communication (shared with NFC reader)
- GPIO 26 for backlight control

---

# Hardware Pinout Configuration
## Device: Raspberry Pi 5
## Peripherals: 1.9" ST7789 TFT LCD, RC522 NFC Reader, Door Sensor Button

-----------------------------------------------------------------------
|   SIGNAL    |  RPI PIN (Physical) |   GPIO #  |  DEVICE CONNECTION  |
-----------------------------------------------------------------------
| 3.3V Power  |      Pin 01         |    N/A    |  Shared (All)       |
| Ground      |      Pin 06         |    N/A    |  Shared (All)       |
-----------------------------------------------------------------------
| SPI SCLK    |      Pin 23         |  GPIO 11  |  Shared (LCD+NFC)   |
| SPI MOSI    |      Pin 19         |  GPIO 10  |  Shared (LCD+NFC)   |
| SPI MISO    |      Pin 21         |  GPIO 09  |  RC522 Only         |
-----------------------------------------------------------------------
| NFC SDA     |      Pin 24         |  GPIO 08  |  NFC "SDA" (SS)     |
| NFC RST     |      Pin 22         |  GPIO 25  |  NFC "RST"          |
-----------------------------------------------------------------------
| LCD CS      |      Pin 18         |  GPIO 24  |  LCD "CS"           |
| LCD DC      |      Pin 13         |  GPIO 27  |  LCD "DC"           |
| LCD RST     |      Pin 15         |  GPIO 22  |  LCD "RES"          |
| LCD BLK     |      Pin 37         |  GPIO 26  |  LCD Backlight      |
-----------------------------------------------------------------------
| Door Sensor |      Pin 40         |  GPIO 21  |  Door Closed Button |
-----------------------------------------------------------------------

**Critical Setup Notes for Raspberry Pi 5:**

1. **SPI Multiplexing:** The NFC Reader uses standard kernel SPI pins (CE0), while the LCD uses GPIO 24 (Pin 18) for Chip Select. This prevents "GPIO busy" conflicts when sharing the SPI bus.

2. **Python 3 lgpio Library:** Required for legacy NFC library compatibility on Pi 5:
   ```bash
   sudo apt install python3-rpi-lgpio python3-spidev
   ```

3. **LCD Backlight Control:** 
   - Managed via GPIO 26 (Pin 37)
   - Turns ON when drinks are being dispensed (inside LCD class)
   - Turns OFF automatically after timeout or when cart closes
   - Prevents LED burnout during idle periods

4. **Door Sensor Button (NEW):**
   - GPIO 21 (Pin 40) with internal pull-up resistor
   - Circuit: [GPIO 21] ← Pull-Up to 3.3V---[Button]---[GND]
   - **Closed Cabinet:** Button connected to GND → GPIO reads LOW → `is_door_open()` returns `False`
   - **Open Cabinet:** Button floating → GPIO reads HIGH (pulled up) → `is_door_open()` returns `True`
   - Used in `joogi_väljastus()` to detect when user closes cabinet (triggers receipt/transaction finalization)

## Implementation Guide for Similar Projects

### Extending with New Hardware Sensor

**Example: Add a temperature sensor to GPIO 4**

1. **Add to hardware_handler.py:**
   ```python
   import board
   import adafruit_dht
   
   TEMP_PIN = 4
   _temp_sensor = None
   
   def init_temp_sensor():
       global _temp_sensor
       _temp_sensor = adafruit_dht.DHT22(board.D4)
   
   def get_temperature():
       try:
           return _temp_sensor.temperature
       except Exception as e:
           logging.error(f"Temp sensor error: {e}")
           return None
   ```

2. **Use in main.py:**
   ```python
   hardware_handler.init_temp_sensor()
   # Later...
   temp = hardware_handler.get_temperature()
   GUI_message(f"Temperature: {temp}°C")
   ```

### Adding a New Screen

1. **Create screen class in drawer.py:**
   ```python
   class TemperatureScreen:
       def handle(self, command_q, reply_q, data):
           # Render to screen
           # Detect button clicks
           reply_q.put(user_choice)
   ```

2. **Send command from main.py:**
   ```python
   command_queue.put(("TEMPERATURE_SCREEN", None))
   response = reply_queue.get(timeout=30)
   ```

### Testing Hardware Without Full UI

Use `gpio4test.py` as a template:
```python
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)
while True:
    state = GPIO.input(21)
    print("Closed" if state == GPIO.LOW else "Open")
    time.sleep(0.5)
GPIO.cleanup()
```

