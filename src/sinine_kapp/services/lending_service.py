from __future__ import annotations

import sqlite3


class LendingService:
    """Encapsulates lend/return operations with inventory bookkeeping."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def lend(self, user_id: int, drink_id: int, quantity: int) -> int:
        return self._record_transaction(user_id, drink_id, quantity, action="lend", delta=-quantity)

    def return_drink(self, user_id: int, drink_id: int, quantity: int) -> int:
        return self._record_transaction(user_id, drink_id, quantity, action="return", delta=quantity)

    def _record_transaction(self, user_id: int, drink_id: int, quantity: int, *, action: str, delta: int) -> int:
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")

        self._ensure_user_exists(user_id)
        drink_row = self._conn.execute(
            "SELECT quantity_on_hand FROM drinks WHERE id = ?",
            (drink_id,),
        ).fetchone()
        if not drink_row:
            raise ValueError("Unknown drink")

        new_quantity = drink_row["quantity_on_hand"] + delta
        if new_quantity < 0:
            raise ValueError("Not enough stock to lend that many units")

        with self._conn:
            self._conn.execute(
                "UPDATE drinks SET quantity_on_hand = ? WHERE id = ?",
                (new_quantity, drink_id),
            )
            self._conn.execute(
                "INSERT INTO transactions(user_id, drink_id, quantity, action) VALUES(?,?,?,?)",
                (user_id, drink_id, quantity, action),
            )
        return new_quantity

    def _ensure_user_exists(self, user_id: int) -> None:
        row = self._conn.execute("SELECT id FROM users WHERE id = ?", (user_id,)).fetchone()
        if not row:
            raise ValueError("Unknown user")


__all__ = ["LendingService"]
