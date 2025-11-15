from __future__ import annotations

import threading
import time
from typing import Callable, Optional

try:
    import serial  # type: ignore
except ImportError:  # pragma: no cover - optional dependency during dev
    serial = None  # type: ignore


TagCallback = Callable[[str], None]


class BaseRFIDReader:
    def __init__(self, callback: TagCallback) -> None:
        self._callback = callback

    def start(self) -> None:  # pragma: no cover - interface
        raise NotImplementedError

    def stop(self) -> None:  # pragma: no cover - interface
        raise NotImplementedError


class SerialRFIDReader(BaseRFIDReader):
    """Reads RFID tags from a serial-connected reader."""

    def __init__(self, port: str, baudrate: int, callback: TagCallback) -> None:
        if serial is None:
            raise RuntimeError("pyserial is required for SerialRFIDReader")

        super().__init__(callback)
        self._port = port
        self._baudrate = baudrate
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._serial: Optional[serial.Serial] = None  # type: ignore[attr-defined]

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._serial:
            try:
                self._serial.close()
            except Exception:
                pass
        if self._thread:
            self._thread.join(timeout=1.0)

    def _run(self) -> None:
        assert serial is not None  # for type checkers
        while not self._stop_event.is_set():
            try:
                self._ensure_serial(serial)
                assert self._serial is not None
                raw = self._serial.readline().decode("utf-8", errors="ignore").strip()
                if raw:
                    self._callback(raw)
            except serial.SerialException:
                time.sleep(1.0)
                self._close_serial()
            except Exception:
                time.sleep(0.2)

    def _ensure_serial(self, serial_module) -> None:
        if self._serial and self._serial.is_open:
            return
        self._serial = serial_module.Serial(
            self._port,
            self._baudrate,
            bytesize=serial_module.EIGHTBITS,
            timeout=0.2,
        )

    def _close_serial(self) -> None:
        if self._serial:
            try:
                self._serial.close()
            finally:
                self._serial = None


class MockRFIDReader(BaseRFIDReader):
    """Simple mock reader used on laptops without RFID hardware."""

    def start(self) -> None:
        # Nothing to do for the mock reader.
        return

    def stop(self) -> None:
        return

    def simulate_scan(self, tag: str) -> None:
        self._callback(tag)


__all__ = ["BaseRFIDReader", "SerialRFIDReader", "MockRFIDReader"]
