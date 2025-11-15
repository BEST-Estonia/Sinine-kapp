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
