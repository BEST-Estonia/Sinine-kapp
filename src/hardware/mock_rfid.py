# src/hardware/mock_rfid.py
class MockRFIDReader:
    def read(self):
        # on a Pi with a real rfid, replace this method
        try:
            uid = input("MOCK: enter RFID UID (or blank to cancel): ").strip()
            return uid if uid else None
        except Exception:
            return None
