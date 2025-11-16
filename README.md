# Smart Cupboard

A Python-based touchscreen UI application for managing a smart drink cupboard with RFID authentication, QR code scanning, and weight monitoring. This system runs on a Raspberry Pi with a 7" touchscreen display and provides a friendly interface for lending and returning beverages.

## Features

- **Touch-friendly Pygame UI**: Optimized for 800×480 touchscreen displays with multi-screen navigation
- **User Database**: SQLite database for RFID card → user name mapping
- **RFID Authentication**: User identification and verification via RFID cards
- **QR Code Scanning**: Track drink returns with QR codes
- **Weight Monitoring**: Dual-scale system for top and bottom shelves
- **Admin Panel**: View and manage registered users
- **Stock Inventory**: Visual inventory management with quantity indicators
- **Mock Hardware Support**: Develop and test without physical hardware
- **Automated Deployment**: GitHub Actions CI/CD for seamless updates
- **Character Mascot**: Meet "Cupby", your friendly cupboard assistant!

## New UI Implementation

This repository now includes a completely redesigned Pygame UI with:
- **Full-screen separate windows** for each function (not just status updates)
- **4 main options**: Open doors, Return drink, Admin, Stock/Inventory
- **Card verification** with registered/denied messages
- **Navigation buttons** on all screens to return to main menu
- **Visual inventory display** with color-coded quantity bars

For detailed documentation on the new UI, see **[PYGAME_GUIDE.md](PYGAME_GUIDE.md)**.

## File Structure

```
smart-cupboard/
├── requirements.txt              # Python dependencies
├── deploy.sh                    # Deployment script for Raspberry Pi
├── README.md                    # This file
├── PYGAME_GUIDE.md              # Detailed UI implementation guide
├── MANUAL_TEST_GUIDE.txt        # Manual testing instructions
├── assets/                      # Images and resources
│   └── character.png            # Character mascot image
├── src/                         # Main application code
│   ├── main.py                 # Entry point
│   ├── app/
│   │   ├── ui_pygame.py        # Main UI manager
│   │   └── screens.py          # Screen classes
│   ├── database/               # Database layer
│   │   ├── __init__.py
│   │   ├── user_db.py          # User database manager
│   │   └── users.db            # SQLite database (auto-generated)
│   └── hardware/               # Hardware abstraction layer
│       ├── mock_rfid.py        # Mock RFID reader
│       ├── mock_qr.py          # Mock QR scanner
│       ├── mock_scales.py      # Mock weight scales
│       └── mock_camera.py      # Mock camera
├── tests/                       # Test suite
│   └── test_integration.py     # Integration tests
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Actions deployment workflow
└── linux/
    └── smart-cupboard.service  # Systemd service file
```
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Actions deployment workflow
└── linux/
    └── smart-cupboard.service  # Systemd service file
```

## Hardware Requirements

### Required Components
- **Raspberry Pi** (3B+ or newer recommended)
- **7" Touchscreen Display** (800×480 resolution, official Pi touchscreen or compatible)
- **Power Supply** (5V 3A for Pi + display)
- **MicroSD Card** (16GB+ with Raspberry Pi OS)

### Optional Hardware (for production use)
- **RFID Reader** (USB/UART compatible, outputs ASCII tag IDs)
- **QR Code Scanner** (USB or camera-based)
- **Load Cells/Scales** (HX711-based for weight monitoring)
- **Camera Module** (Pi Camera or USB webcam)
- **Solenoid Lock** (12V for cupboard door)
- **Relay Module** (for controlling the lock)

## Mock Hardware Explanation

The application includes mock hardware modules that simulate real devices for development and testing:

- **MockRFIDReader**: Prompts for RFID input via console
- **MockQRScanner**: Accepts QR codes through console input
- **MockScale**: Generates random weight values (0.5-5.0 kg)
- **MockCamera**: Simulates image capture

These mock modules allow you to:
- Develop and test the UI without physical hardware
- Prototype features before hardware arrives
- Debug application logic independently

To use real hardware, replace the mock classes with actual hardware drivers while maintaining the same interface.

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

5. **Testing the UI**:
   - The main screen will show 4 options with a character mascot
   - When prompted in console for RFID, enter: `1`, `2`, or `3` for registered users
   - For QR codes, enter any text
   - See [MANUAL_TEST_GUIDE.txt](MANUAL_TEST_GUIDE.txt) for complete testing instructions
   - Run integration tests: `python tests/test_integration.py`

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
   # Copy the service file
   sudo cp linux/smart-cupboard.service /etc/systemd/system/
   
   # Enable and start the service
   sudo systemctl daemon-reload
   sudo systemctl enable smart-cupboard.service
   sudo systemctl start smart-cupboard.service
   
   # Check status
   sudo systemctl status smart-cupboard.service
   ```

8. **Configure touchscreen (if needed)**:
   - The official Pi touchscreen should work out of the box
   - For HDMI displays, you may need to configure resolution in `/boot/config.txt`

## GitHub Actions Deployment

The repository includes automated deployment via GitHub Actions that deploys code to your Raspberry Pi on every push to the `main` branch.

### Setup GitHub Secrets

Configure these secrets in your GitHub repository (Settings → Secrets and variables → Actions):

- **`SSH_PRIVATE_KEY`**: Private SSH key for authenticating to the Pi
- **`TARGET_HOST`**: Raspberry Pi IP address or hostname (e.g., `192.168.1.100`)
- **`TARGET_USER`**: SSH user (default: `pi`)
- **`TARGET_DIR`**: Target directory on Pi (default: `/home/pi/smart-cupboard`)
- **`SERVICE_NAME`**: Systemd service name (default: `smart-cupboard.service`)

### Generate SSH Key Pair

On your local machine:

```bash
# Generate a new SSH key pair
ssh-keygen -t ed25519 -f ~/.ssh/smart-cupboard-deploy -N ""

# Copy the public key to your Raspberry Pi
ssh-copy-id -i ~/.ssh/smart-cupboard-deploy.pub pi@YOUR_PI_IP

# Display the private key (copy this to GitHub secrets)
cat ~/.ssh/smart-cupboard-deploy
```

### Manual Deployment

You can also deploy manually using the deployment script:

```bash
# Set environment variables
export TARGET_HOST=192.168.1.100
export TARGET_USER=pi
export TARGET_DIR=/home/pi/smart-cupboard
export SERVICE_NAME=smart-cupboard.service

# Run the deployment script
./deploy.sh
```

## Configuration

### Display Resolution

Edit `src/app/ui_pygame.py` to change screen resolution:

```python
SCREEN_W, SCREEN_H = 480, 800  # Portrait orientation (change to your display resolution)
```

Common resolutions:
- 480×800 (portrait mode for 7" Pi touchscreen - **current default**)
- 800×480 (landscape mode for 7" Pi touchscreen)
- 600×1024 (portrait mode for larger 7" displays)
- 1920×1080 (full HD landscape)
- 1080×1920 (full HD portrait)

**Note:** The UI is optimized for portrait orientation with vertically stacked buttons.

### Service Configuration

Edit `linux/smart-cupboard.service` to customize:
- Working directory
- Python interpreter path
- Service restart behavior
- Environment variables

## Development

### Project Architecture

- **`src/main.py`**: Application entry point, instantiates hardware and UI
- **`src/app/ui_pygame.py`**: Pygame-based touchscreen interface with button handling
- **`src/hardware/`**: Hardware abstraction layer for easy device swapping

### Adding Real Hardware

To integrate real hardware:

1. Create a new module (e.g., `src/hardware/real_rfid.py`)
2. Implement the same interface as the mock version
3. Update imports in `src/main.py`

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

Then update `src/main.py`:
```python
from hardware.real_rfid import RFIDReader  # Changed from MockRFIDReader
```

### Extending the UI

The button-based UI can be easily extended:

```python
# Add new button to the buttons list in TouchUI.__init__
self.buttons.append(
    Button((x, y, width, height), "New Action", self.new_action)
)

# Implement the action method
def new_action(self):
    self.status = "Performing new action..."
    # Your code here
```

## Troubleshooting

### Application won't start
- Check Python version: `python3 --version` (requires 3.7+)
- Verify dependencies: `pip list | grep pygame`
- Check logs: `journalctl -u smart-cupboard.service -f`

### Touchscreen not responding
- Test touch input: `evtest` (install with `sudo apt install evtest`)
- Calibrate screen: `sudo apt install xinput-calibrator`
- Verify display detection: `DISPLAY=:0 xrandr`

### Deployment fails
- Verify SSH connection: `ssh pi@YOUR_PI_IP`
- Check GitHub secrets are set correctly
- Review GitHub Actions logs in the Actions tab

### Display issues
- Ensure X server is running: `echo $DISPLAY`
- Set display: `export DISPLAY=:0`
- Check for multiple displays: `xrandr --listmonitors`

## License

This project is part of BEST Estonia's initiatives. See the repository for license details.

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues and questions:
- Open an issue on GitHub
- Contact BEST Estonia

---

**Enjoy your Smart Cupboard! 🚀**
