from __future__ import annotations

import sqlite3
from typing import Iterable, List, Optional

from sinine_kapp.models import Drink


class InventoryService:
    """High-level helper for reading and mutating drink inventory."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def list_drinks(self) -> List[Drink]:
        cur = self._conn.execute(
            "SELECT id, name, description, unit_volume_ml, unit_price, quantity_on_hand"
            " FROM drinks ORDER BY name"
        )
        return [self._row_to_drink(row) for row in cur.fetchall()]

    def search_drinks(self, text: str) -> List[Drink]:
        like = f"%{text.lower()}%"
        cur = self._conn.execute(
            """
            SELECT id, name, description, unit_volume_ml, unit_price, quantity_on_hand
            FROM drinks
            WHERE lower(name) LIKE ? OR lower(description) LIKE ?
            ORDER BY name
            """,
            (like, like),
        )
        return [self._row_to_drink(row) for row in cur.fetchall()]

    def get_drink(self, drink_id: int) -> Optional[Drink]:
        cur = self._conn.execute(
            "SELECT id, name, description, unit_volume_ml, unit_price, quantity_on_hand"
            " FROM drinks WHERE id = ?",
            (drink_id,),
        )
        row = cur.fetchone()
        return self._row_to_drink(row) if row else None

    def adjust_stock(self, drink_id: int, delta: int) -> int:
        drink = self.get_drink(drink_id)
        if not drink:
            raise ValueError("Unknown drink")

        new_qty = drink.quantity_on_hand + delta
        if new_qty < 0:
            raise ValueError("Not enough stock available")

        with self._conn:
            self._conn.execute(
                "UPDATE drinks SET quantity_on_hand = ? WHERE id = ?",
                (new_qty, drink_id),
            )
        return new_qty

    @staticmethod
    def _row_to_drink(row: sqlite3.Row) -> Drink:
        return Drink(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            unit_volume_ml=row["unit_volume_ml"],
            unit_price=row["unit_price"],
            quantity_on_hand=row["quantity_on_hand"],
        )


__all__ = ["InventoryService"]
