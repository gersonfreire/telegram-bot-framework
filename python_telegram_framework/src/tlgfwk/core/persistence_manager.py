import pickle
import os
import json
import sqlite3
from ..utils.logger import get_logger

class PersistenceManager:
    """
    Manages data persistence, supporting pickle, json, and sqlite backends.
    """
    def __init__(self, config):
        self.config = config
        self.logger = get_logger(__name__)
        self.backend = self.config.persistence_backend
        self.storage_path = 'data/'
        self.db_connection = None

        if self.backend == 'sqlite':
            self._setup_sqlite()
        else:
            if not os.path.exists(self.storage_path):
                os.makedirs(self.storage_path)

    def _setup_sqlite(self):
        """Initializes the SQLite database and creates the table if needed."""
        db_path = os.path.join(self.storage_path, 'persistence.db')
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
        self.db_connection = sqlite3.connect(db_path, check_same_thread=False)
        cursor = self.db_connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS key_value_store (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        self.db_connection.commit()
        self.logger.info("SQLite backend initialized.")

    def _get_path(self, filename):
        """Constructs the full path for file-based backends."""
        return os.path.join(self.storage_path, filename)

    def save_data(self, key, data):
        """Saves data using the configured backend."""
        if self.backend == 'sqlite':
            try:
                json_data = json.dumps(data)
                cursor = self.db_connection.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO key_value_store (key, value) VALUES (?, ?)",
                    (key, json_data)
                )
                self.db_connection.commit()
                self.logger.debug(f"Data saved for key '{key}' in SQLite.")
            except (sqlite3.Error, json.JSONDecodeError) as e:
                self.logger.error(f"Error saving data to SQLite for key '{key}': {e}")
        else: # 'pickle' or 'json'
            path = self._get_path(f"{key}.{self.backend}")
            try:
                if self.backend == 'pickle':
                    with open(path, 'wb') as f:
                        pickle.dump(data, f)
                elif self.backend == 'json':
                    with open(path, 'w') as f:
                        json.dump(data, f, indent=4)
                self.logger.debug(f"Data saved to {path} using {self.backend}.")
            except (IOError, pickle.PicklingError, json.JSONDecodeError) as e:
                self.logger.error(f"Error saving data to {path}: {e}")

    def load_data(self, key, default=None):
        """Loads data using the configured backend."""
        if self.backend == 'sqlite':
            try:
                cursor = self.db_connection.cursor()
                cursor.execute("SELECT value FROM key_value_store WHERE key = ?", (key,))
                row = cursor.fetchone()
                if row:
                    return json.loads(row[0])
                return default
            except (sqlite3.Error, json.JSONDecodeError) as e:
                self.logger.error(f"Error loading data from SQLite for key '{key}': {e}")
                return default
        else: # 'pickle' or 'json'
            path = self._get_path(f"{key}.{self.backend}")
            if not os.path.exists(path):
                return default
            try:
                if self.backend == 'pickle':
                    with open(path, 'rb') as f:
                        return pickle.load(f)
                elif self.backend == 'json':
                    with open(path, 'r') as f:
                        return json.load(f)
            except (IOError, pickle.UnpicklingError, json.JSONDecodeError) as e:
                self.logger.error(f"Error loading data from {path}: {e}")
            return default

    def __del__(self):
        """Ensure the database connection is closed on object destruction."""
        if self.db_connection:
            self.db_connection.close()