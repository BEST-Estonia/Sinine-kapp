# src/main.py
from app.ui_pygame import TouchUI
from hardware.mock_rfid import MockRFIDReader
from hardware.mock_scales import MockScale
from hardware.mock_qr import MockQRScanner
from hardware.mock_camera import MockCamera

def main():
    # instantiate mock hardware
    rfid = MockRFIDReader()
    qr = MockQRScanner()
    cam = MockCamera()
    scale_top = MockScale(level="top")
    scale_bottom = MockScale(level="bottom")

    ui = TouchUI(rfid=rfid, qr=qr, camera=cam, scale_top=scale_top, scale_bottom=scale_bottom)
    ui.run()

if __name__ == "__main__":
    main()
