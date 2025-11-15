# src/hardware/mock_qr.py
class MockQRScanner:
    def scan(self):
        try:
            code = input("MOCK: enter QR code (or blank to cancel): ").strip()
            return code if code else None
        except Exception:
            return None
