import sqlite3
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, db_path: str, schema_path: str = "data/schema.sql"):
        self.db_path = Path(db_path)
        self.schema_path = Path(schema_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_database()

    def _ensure_database(self):
        """Create the database file and initialize schema if missing."""
        if not self.db_path.exists():
            logger.info(f"Creating new database at {self.db_path}")
            self._run_schema()
        else:
            # If schema file exists and DB is empty, try to run schema
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='students'")
                    if cursor.fetchone() is None and self.schema_path.exists():
                        logger.info("Database appears uninitialized; applying schema.sql")
                        self._run_schema()
            except Exception:
                logger.exception("Error checking database schema; attempting to apply schema")
                self._run_schema()

    def _run_schema(self):
        if not self.schema_path.exists():
            logger.warning(f"Schema file not found at {self.schema_path}; skipping schema creation")
            # create empty DB file
            with sqlite3.connect(self.db_path) as conn:
                pass
            return

        try:
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                sql = f.read()

            with sqlite3.connect(self.db_path) as conn:
                conn.executescript(sql)
            logger.info("Database schema applied successfully")
        except Exception:
            logger.exception("Failed to apply database schema")

    def get_connection(self):
        return sqlite3.connect(self.db_path)
