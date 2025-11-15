from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import List

from sinine_kapp.models import Transaction


class TransactionService:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def recent_transactions(self, limit: int = 25) -> List[Transaction]:
        cur = self._conn.execute(
            """
            SELECT t.id, u.name as user_name, d.name as drink_name, t.quantity, t.action, t.created_at
            FROM transactions t
            JOIN users u ON t.user_id = u.id
            JOIN drinks d ON t.drink_id = d.id
            ORDER BY t.created_at DESC
            LIMIT ?
            """,
            (limit,),
        )
        items: List[Transaction] = []
        for row in cur.fetchall():
            created_at = datetime.fromisoformat(row["created_at"])
            items.append(
                Transaction(
                    id=row["id"],
                    user_name=row["user_name"],
                    drink_name=row["drink_name"],
                    quantity=row["quantity"],
                    action=row["action"],
                    created_at=created_at,
                )
            )
        return items


__all__ = ["TransactionService"]
