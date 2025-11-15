from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

Connection = sqlite3.Connection

SCHEMA_SQL = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    rfid_tag TEXT UNIQUE NOT NULL,
    email TEXT
);

CREATE TABLE IF NOT EXISTS drinks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    unit_volume_ml INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    quantity_on_hand INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    drink_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    action TEXT NOT NULL CHECK(action IN ('lend', 'return')),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(drink_id) REFERENCES drinks(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_transactions_created_at
    ON transactions(created_at DESC);
"""

SAMPLE_USERS = [
    ("Alice", "04A1B2C3D4", "alice@example.com"),
    ("Bob", "05B1C2D3E4", "bob@example.com"),
]

SAMPLE_DRINKS = [
    ("Club Mate", "Classic yerba mate soda", 500, 2.5, 24),
    ("Kombucha", "Rotating flavors", 330, 3.0, 18),
    ("Mineral Water", "Sparkling", 500, 1.0, 32),
]


def initialize_database(db_path: Path | str) -> Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row

    with conn:
        conn.executescript(SCHEMA_SQL)

    seed_default_records(conn)
    return conn


def seed_default_records(conn: Connection) -> None:
    if _is_table_empty(conn, "users"):
        with conn:
            conn.executemany(
                "INSERT INTO users(name, rfid_tag, email) VALUES(?,?,?)",
                SAMPLE_USERS,
            )

    if _is_table_empty(conn, "drinks"):
        with conn:
            conn.executemany(
                (
                    "INSERT INTO drinks(name, description, unit_volume_ml, unit_price, quantity_on_hand)"
                    " VALUES(?,?,?,?,?)"
                ),
                SAMPLE_DRINKS,
            )


def _is_table_empty(conn: Connection, table_name: str) -> bool:
    cur = conn.execute(f"SELECT COUNT(1) AS count FROM {table_name}")
    row = cur.fetchone()
    return bool(row) and row[0] == 0


__all__ = ["initialize_database", "seed_default_records"]
