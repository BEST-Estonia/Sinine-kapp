from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AppConfig:
    """Holds runtime configuration for the kiosk application."""

    display_width: int = 1024
    display_height: int = 600
    database_path: Path = Path("data") / "sinine_kapp.db"
    rfid_port: str | None = None
    rfid_baudrate: int = 9600
    mock_rfid_reader: bool = True


def load_config() -> AppConfig:
    """Load configuration from environment variables with sensible defaults."""

    width = int(os.getenv("SININE_DISPLAY_WIDTH", "1024"))
    height = int(os.getenv("SININE_DISPLAY_HEIGHT", "600"))
    db_path = Path(os.getenv("SININE_DB_PATH", "data/sinine_kapp.db"))

    port = os.getenv("SININE_RFID_PORT")
    baudrate = int(os.getenv("SININE_RFID_BAUD", "9600"))
    mock_reader = os.getenv("SININE_MOCK_RFID", "true").lower() == "true"

    return AppConfig(
        display_width=width,
        display_height=height,
        database_path=db_path,
        rfid_port=port,
        rfid_baudrate=baudrate,
        mock_rfid_reader=mock_reader,
    )


__all__ = ["AppConfig", "load_config"]
