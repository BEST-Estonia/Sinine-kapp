from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Drink:
    id: int
    name: str
    description: str
    unit_volume_ml: int
    unit_price: float
    quantity_on_hand: int


@dataclass(slots=True)
class User:
    id: int
    name: str
    rfid_tag: str
    email: Optional[str] = None


@dataclass(slots=True)
class Transaction:
    id: int
    user_name: str
    drink_name: str
    quantity: int
    action: str
    created_at: datetime


__all__ = ["Drink", "User", "Transaction"]
