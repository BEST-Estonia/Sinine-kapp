from __future__ import annotations

import sqlite3
from typing import Callable, Optional

from sinine_kapp.config import AppConfig
from sinine_kapp.hardware.rfid_reader import BaseRFIDReader, MockRFIDReader, SerialRFIDReader
from sinine_kapp.models import User

UserCallback = Callable[[str, Optional[User]], None]


class RFIDService:
    def __init__(self, conn: sqlite3.Connection, config: AppConfig, on_user_detected: UserCallback) -> None:
        self._conn = conn
        self._config = config
        self._on_user_detected = on_user_detected
        self._reader: BaseRFIDReader = self._build_reader()

    def _build_reader(self) -> BaseRFIDReader:
        if self._config.mock_rfid_reader or not self._config.rfid_port:
            return MockRFIDReader(self._handle_tag)
        return SerialRFIDReader(
            port=self._config.rfid_port,
            baudrate=self._config.rfid_baudrate,
            callback=self._handle_tag,
        )

    def start(self) -> None:
        self._reader.start()

    def stop(self) -> None:
        self._reader.stop()

    def _handle_tag(self, tag: str) -> None:
        user = self.lookup_user(tag)
        self._on_user_detected(tag, user)

    def lookup_user(self, tag: str) -> Optional[User]:
        row = self._conn.execute(
            "SELECT id, name, rfid_tag, email FROM users WHERE rfid_tag = ?",
            (tag,),
        ).fetchone()
        if not row:
            return None
        return User(
            id=row["id"],
            name=row["name"],
            rfid_tag=row["rfid_tag"],
            email=row["email"],
        )

    def simulate_scan(self, tag: str) -> None:
        mock = getattr(self._reader, "simulate_scan", None)
        if callable(mock):
            mock(tag)


__all__ = ["RFIDService"]
