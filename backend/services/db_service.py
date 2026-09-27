import sqlite3
from datetime import datetime
from pathlib import Path
from backend.config import Config
from backend.utils.logger import logger

DB_PATH = Config.BASE_DIR / "college_voice.db"

class DatabaseService:
    """Simple SQLite service for logging calls and conversations."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Table for call sessions
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS call_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        caller_number TEXT DEFAULT 'Unknown',
                        call_sid TEXT UNIQUE,
                        start_time TEXT,
                        status TEXT DEFAULT 'in-progress'
                    )
                """)
                # Table for conversation / IVR interactions
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS conversation_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        call_sid TEXT,
                        speaker TEXT,
                        message TEXT,
                        timestamp TEXT
                    )
                """)
                conn.commit()
        except Exception as e:
            logger.error(f"Error initializing SQLite database: {e}")

    def log_call(self, call_sid: str, caller_number: str = "Unknown") -> None:
        """Record or update a call session."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR IGNORE INTO call_logs (call_sid, caller_number, start_time, status)
                    VALUES (?, ?, ?, 'active')
                """, (call_sid, caller_number, datetime.now().isoformat()))
                conn.commit()
        except Exception as e:
            logger.error(f"Error logging call session: {e}")

    def log_interaction(self, call_sid: str, speaker: str, message: str) -> None:
        """Record an utterance (from caller, IVR, or AI assistant)."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO conversation_logs (call_sid, speaker, message, timestamp)
                    VALUES (?, ?, ?, ?)
                """, (call_sid, speaker, message, datetime.now().isoformat()))
                conn.commit()
        except Exception as e:
            logger.error(f"Error logging interaction: {e}")

    def get_recent_calls(self, limit: int = 20) -> list:
        """Fetch recent call logs."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM call_logs ORDER BY id DESC LIMIT ?", (limit,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error fetching calls: {e}")
            return []

db_service = DatabaseService()
