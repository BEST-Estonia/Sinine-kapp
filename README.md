# Sinine Kapp

A modern KivyMD-based camera application for Raspberry Pi kiosk mode.

## Description

Sinine Kapp (Blue Cabinet in Estonian) is a full-screen camera application built with Kivy and KivyMD. It's designed to run on Raspberry Pi devices with a camera in kiosk mode.

## Features

- Full-screen kiosk mode
- Live camera feed (640x480 resolution optimized for Raspberry Pi)
- Blue Material Design theme
- Touch-friendly interface
- Close button to exit the application

## Requirements

- Python 3.7+
- Raspberry Pi with camera module (or compatible camera device)
- Touchscreen display (optional but recommended)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/BEST-Estonia/Sinine-kapp.git
cd Sinine-kapp
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python main.py
```

The application will start in full-screen mode. The camera feed will be displayed in the center of the screen with a header at the top and a close button at the bottom.

To exit the application, press the red "SULGE PROGRAMM" (Close Program) button.

## Configuration

The application is configured to run in full-screen mode by default. The camera resolution is set to 640x480 for optimal performance on Raspberry Pi devices.

You can modify these settings in the `main.py` file:
- `Window.fullscreen = 'auto'` - Control full-screen mode
- `Camera(play=True, resolution=(640, 480))` - Adjust camera resolution

## Running on Startup (Kiosk Mode)

To run the application automatically on startup in kiosk mode on Raspberry Pi:

1. Create a systemd service file:
```bash
sudo nano /etc/systemd/system/sinine-kapp.service
```

2. Add the following content:
```ini
[Unit]
Description=Sinine Kapp Camera Application
After=graphical.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Sinine-kapp
ExecStart=/usr/bin/python3 /home/pi/Sinine-kapp/main.py
Restart=on-failure

[Install]
WantedBy=graphical.target
```

3. Enable and start the service:
```bash
sudo systemctl enable sinine-kapp.service
sudo systemctl start sinine-kapp.service
```

## License

This project is open source and available for use.
