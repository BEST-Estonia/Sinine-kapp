# src/database.py
"""
Comprehensive Database Manager for Smart Cupboard
Manages users, items, stock, and borrow/return transactions
"""
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import calendar


class DatabaseManager:
    """Manages all database operations for the smart cupboard system"""
    
    def __init__(self, db_path=None):
        if db_path is None:
            # Store in src/database directory
            db_dir = Path(__file__).parent / "database"
            db_dir.mkdir(exist_ok=True)
            db_path = db_dir / "cupboard.db"
        
        self.db_path = db_path
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row  # Enable dict-like access
        self.cursor = self.conn.cursor()
        self._create_tables()
        self._populate_sample_data()
    
    def _create_tables(self):
        """Create all required tables"""
        # Users table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                card_id TEXT UNIQUE NOT NULL,
                is_admin BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Items table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                qr_code TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Stock table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock (
                qr_code TEXT PRIMARY KEY,
                quantity INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (qr_code) REFERENCES items(qr_code)
            )
        ''')
        
        # Borrows table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS borrows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                qr_code TEXT NOT NULL,
                timestamp_out TEXT NOT NULL,
                timestamp_returned TEXT NULL,
                due_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (qr_code) REFERENCES items(qr_code)
            )
        ''')
        
        self.conn.commit()
    
    def _populate_sample_data(self):
        """Populate with sample data for testing"""
        # Check if data already exists
        self.cursor.execute("SELECT COUNT(*) FROM users")
        if self.cursor.fetchone()[0] == 0:
            # Add sample users (user_id=1 is admin)
            sample_users = [
                ("Admin User", "1", 1),
                ("Alice Johnson", "2", 0),
                ("Bob Smith", "3", 0),
            ]
            self.cursor.executemany(
                "INSERT INTO users (name, card_id, is_admin) VALUES (?, ?, ?)",
                sample_users
            )
            
            # Add sample items
            sample_items = [
                ("DRINK001", "Coca Cola"),
                ("DRINK002", "Sprite"),
                ("DRINK003", "Orange Juice"),
                ("DRINK004", "Water"),
                ("DRINK005", "Energy Drink"),
                ("DRINK006", "Iced Tea"),
                ("DRINK007", "Lemonade"),
            ]
            self.cursor.executemany(
                "INSERT INTO items (qr_code, name) VALUES (?, ?)",
                sample_items
            )
            
            # Add sample stock
            sample_stock = [
                ("DRINK001", 12),
                ("DRINK002", 8),
                ("DRINK003", 5),
                ("DRINK004", 20),
                ("DRINK005", 3),
                ("DRINK006", 10),
                ("DRINK007", 6),
            ]
            self.cursor.executemany(
                "INSERT INTO stock (qr_code, quantity) VALUES (?, ?)",
                sample_stock
            )
            
            self.conn.commit()
    
    # ===== User Management =====
    
    def get_user_by_card(self, card_id):
        """Get user by card ID"""
        self.cursor.execute(
            "SELECT * FROM users WHERE card_id = ?",
            (card_id,)
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        self.cursor.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def add_user(self, name, card_id, is_admin=False):
        """Add a new user"""
        try:
            self.cursor.execute(
                "INSERT INTO users (name, card_id, is_admin) VALUES (?, ?, ?)",
                (name, card_id, int(is_admin))
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_all_users(self):
        """Get all users"""
        self.cursor.execute("SELECT * FROM users ORDER BY name")
        return [dict(row) for row in self.cursor.fetchall()]
    
    def delete_user(self, user_id):
        """Delete a user"""
        self.cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    # ===== Item Management =====
    
    def get_item(self, qr_code):
        """Get item by QR code"""
        self.cursor.execute(
            "SELECT * FROM items WHERE qr_code = ?",
            (qr_code,)
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def add_item(self, qr_code, name):
        """Add a new item"""
        try:
            self.cursor.execute(
                "INSERT INTO items (qr_code, name) VALUES (?, ?)",
                (qr_code, name)
            )
            # Also add to stock with 0 quantity
            self.cursor.execute(
                "INSERT INTO stock (qr_code, quantity) VALUES (?, 0)",
                (qr_code,)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_all_items(self):
        """Get all items with stock information"""
        self.cursor.execute("""
            SELECT i.qr_code, i.name, COALESCE(s.quantity, 0) as quantity
            FROM items i
            LEFT JOIN stock s ON i.qr_code = s.qr_code
            ORDER BY i.name
        """)
        return [dict(row) for row in self.cursor.fetchall()]
    
    # ===== Stock Management =====
    
    def get_stock(self, qr_code):
        """Get stock quantity for an item"""
        self.cursor.execute(
            "SELECT quantity FROM stock WHERE qr_code = ?",
            (qr_code,)
        )
        row = self.cursor.fetchone()
        return row[0] if row else 0
    
    def update_stock(self, qr_code, quantity):
        """Update stock quantity"""
        self.cursor.execute(
            "UPDATE stock SET quantity = ?, updated_at = CURRENT_TIMESTAMP WHERE qr_code = ?",
            (quantity, qr_code)
        )
        if self.cursor.rowcount == 0:
            # Insert if doesn't exist
            self.cursor.execute(
                "INSERT INTO stock (qr_code, quantity) VALUES (?, ?)",
                (qr_code, quantity)
            )
        self.conn.commit()
    
    def adjust_stock(self, qr_code, delta):
        """Adjust stock by delta (positive or negative)"""
        current = self.get_stock(qr_code)
        new_quantity = max(0, current + delta)
        self.update_stock(qr_code, new_quantity)
        return new_quantity
    
    # ===== Borrow/Return Management =====
    
    def calculate_due_date(self, borrow_date=None):
        """Calculate due date: first Wednesday of next month"""
        if borrow_date is None:
            borrow_date = datetime.now()
        
        # Get next month
        if borrow_date.month == 12:
            next_month = datetime(borrow_date.year + 1, 1, 1)
        else:
            next_month = datetime(borrow_date.year, borrow_date.month + 1, 1)
        
        # Find first Wednesday (weekday() returns 0=Monday, 2=Wednesday)
        c = calendar.monthcalendar(next_month.year, next_month.month)
        first_week = c[0]
        second_week = c[1]
        
        if first_week[calendar.WEDNESDAY] != 0:
            # Wednesday is in first week
            day = first_week[calendar.WEDNESDAY]
        else:
            # Wednesday is in second week
            day = second_week[calendar.WEDNESDAY]
        
        due_date = datetime(next_month.year, next_month.month, day)
        return due_date.strftime("%Y-%m-%d")
    
    def borrow_item(self, user_id, qr_code):
        """Record a borrow transaction"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        due_date = self.calculate_due_date()
        
        self.cursor.execute(
            "INSERT INTO borrows (user_id, qr_code, timestamp_out, due_date) VALUES (?, ?, ?, ?)",
            (user_id, qr_code, timestamp, due_date)
        )
        # Decrease stock
        self.adjust_stock(qr_code, -1)
        self.conn.commit()
        return self.cursor.lastrowid
    
    def return_item(self, user_id, qr_code):
        """Record a return transaction"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Find the most recent unreturned borrow for this user and item
        self.cursor.execute(
            """SELECT id FROM borrows 
               WHERE user_id = ? AND qr_code = ? AND timestamp_returned IS NULL
               ORDER BY timestamp_out DESC LIMIT 1""",
            (user_id, qr_code)
        )
        row = self.cursor.fetchone()
        
        if row:
            # Update existing borrow record
            self.cursor.execute(
                "UPDATE borrows SET timestamp_returned = ? WHERE id = ?",
                (timestamp, row[0])
            )
        else:
            # Create new return record (item borrowed before system was tracking)
            self.cursor.execute(
                "INSERT INTO borrows (user_id, qr_code, timestamp_out, timestamp_returned) VALUES (?, ?, ?, ?)",
                (user_id, qr_code, timestamp, timestamp)
            )
        
        # Increase stock
        self.adjust_stock(qr_code, 1)
        self.conn.commit()
    
    def get_user_borrows(self, user_id, include_returned=False):
        """Get all borrows for a user"""
        if include_returned:
            query = """
                SELECT b.*, i.name as item_name
                FROM borrows b
                JOIN items i ON b.qr_code = i.qr_code
                WHERE b.user_id = ?
                ORDER BY b.timestamp_out DESC
            """
        else:
            query = """
                SELECT b.*, i.name as item_name
                FROM borrows b
                JOIN items i ON b.qr_code = i.qr_code
                WHERE b.user_id = ? AND b.timestamp_returned IS NULL
                ORDER BY b.timestamp_out DESC
            """
        self.cursor.execute(query, (user_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_overdue_items(self, user_id):
        """Get overdue items for a user"""
        today = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute(
            """SELECT b.*, i.name as item_name
               FROM borrows b
               JOIN items i ON b.qr_code = i.qr_code
               WHERE b.user_id = ? AND b.timestamp_returned IS NULL AND b.due_date < ?
               ORDER BY b.due_date""",
            (user_id, today)
        )
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_all_borrows(self, limit=100):
        """Get all borrow transactions (system log)"""
        self.cursor.execute(
            """SELECT b.*, u.name as user_name, i.name as item_name
               FROM borrows b
               JOIN users u ON b.user_id = u.id
               JOIN items i ON b.qr_code = i.qr_code
               ORDER BY b.timestamp_out DESC
               LIMIT ?""",
            (limit,)
        )
        return [dict(row) for row in self.cursor.fetchall()]
    
    # ===== Utility =====
    
    def close(self):
        """Close database connection"""
        self.conn.close()
    
    def __del__(self):
        """Ensure database is closed"""
        try:
            self.close()
        except:
            pass
