# Simple Camera Application

A simple Python-based Pygame UI application with two buttons: Open Camera and Close Program.

## Features

- **Touch-friendly Pygame UI**: Optimized for touchscreen displays
- **Two Buttons**: Open Camera and Close Program
- **Mock Camera Support**: Develop and test without physical camera hardware

## File Structure

```
simple-camera/
├── requirements.txt              # Python dependencies
├── deploy.sh                    # Deployment script for Raspberry Pi
├── README.md                    # This file
├── src/                         # Main application code
│   ├── main.py                 # Entry point
│   ├── config.py               # Application configuration
│   ├── screen_manager.py       # Screen navigation
│   ├── screens/                # Screen classes
│   │   ├── __init__.py
│   │   ├── base_screen.py      # Base screen class
│   │   └── main_menu.py        # Main menu with 2 buttons
│   ├── ui/                     # UI components
│   │   ├── __init__.py
│   │   ├── buttons.py          # Button widget
│   │   └── theme.py            # Design system
│   └── hardware/               # Hardware abstraction
│       └── mock_camera.py      # Mock camera
├── tests/                       # Test suite
│   ├── test_integration.py     # Integration tests
│   ├── test_main_menu_imports.py
│   └── navigation_test.py      # Navigation tests
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Actions deployment workflow
└── linux/
    └── smart-cupboard.service  # Systemd service file
```

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
   - The main screen will show 2 buttons: "Open Camera" and "Close Program"
   - Click "Open Camera" to trigger the camera
   - Click "Close Program" to exit the application
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
   git clone https://github.com/BEST-Estonia/Sinine-kapp.git simple-camera
   cd simple-camera
   ```

5. **Create virtual environment and install dependencies**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

6. **Run the application**:
   ```bash
   cd src
   python main.py
   ```

## Configuration

Edit `src/config.py` to change:
- Screen resolution (SCREEN_WIDTH, SCREEN_HEIGHT)
- Frame rate (FPS)
- Fullscreen mode (FULLSCREEN)
- Borderless window (NOFRAME)

## License

This project is part of BEST Estonia's initiatives. See the repository for license details.

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

**Enjoy your Simple Camera Application! 🚀**
