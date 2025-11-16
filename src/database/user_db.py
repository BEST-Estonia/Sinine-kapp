# src/database/user_db.py
import sqlite3
from pathlib import Path

class UserDatabase:
    """Mock SQL database for storing user information (RFID/card number → name)"""
    
    def __init__(self, db_path=None):
        if db_path is None:
            # Store in src/database directory
            db_dir = Path(__file__).parent
            db_path = db_dir / "users.db"
        
        self.db_path = db_path
        self.conn = sqlite3.connect(str(db_path))
        self.cursor = self.conn.cursor()
        self._create_table()
        self._populate_sample_data()
    
    def _create_table(self):
        """Create users table if it doesn't exist"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                rfid_number TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
    
    def _populate_sample_data(self):
        """Populate with sample RFID numbers for testing"""
        sample_users = [
            ("1", "Alice Johnson"),
            ("2", "Bob Smith"),
            ("3", "Charlie Brown"),
        ]
        
        # Check if data already exists
        self.cursor.execute("SELECT COUNT(*) FROM users")
        count = self.cursor.fetchone()[0]
        
        if count == 0:
            self.cursor.executemany(
                "INSERT OR IGNORE INTO users (rfid_number, name) VALUES (?, ?)",
                sample_users
            )
            self.conn.commit()
    
    def get_user_by_rfid(self, rfid_number):
        """
        Get user by RFID number
        
        Args:
            rfid_number: The RFID card number (string)
        
        Returns:
            Dictionary with user info or None if not found
        """
        self.cursor.execute(
            "SELECT rfid_number, name FROM users WHERE rfid_number = ?",
            (rfid_number,)
        )
        result = self.cursor.fetchone()
        
        if result:
            return {
                "rfid_number": result[0],
                "name": result[1]
            }
        return None
    
    def add_user(self, rfid_number, name):
        """
        Add a new user to the database
        
        Args:
            rfid_number: The RFID card number (string)
            name: User's name (string)
        
        Returns:
            True if successful, False if user already exists
        """
        try:
            self.cursor.execute(
                "INSERT INTO users (rfid_number, name) VALUES (?, ?)",
                (rfid_number, name)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # User already exists
            return False
    
    def get_all_users(self):
        """Get all users in the database"""
        self.cursor.execute("SELECT rfid_number, name FROM users ORDER BY name")
        results = self.cursor.fetchall()
        return [{"rfid_number": r[0], "name": r[1]} for r in results]
    
    def delete_user(self, rfid_number):
        """
        Delete a user from the database
        
        Args:
            rfid_number: The RFID card number to delete
        
        Returns:
            True if deleted, False if not found
        """
        self.cursor.execute(
            "DELETE FROM users WHERE rfid_number = ?",
            (rfid_number,)
        )
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def close(self):
        """Close the database connection"""
        self.conn.close()
    
    def __del__(self):
        """Ensure database is closed when object is destroyed"""
        try:
            self.close()
        except:
            pass
