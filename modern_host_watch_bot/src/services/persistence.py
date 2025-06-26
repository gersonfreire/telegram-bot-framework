"""
Persistence service for storing bot data.
"""
import json
import sqlite3
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from pathlib import Path

from ..models.host import HostJob, HostConfig, HostStatus
from ..models.user import User, UserPreferences
from ..config.settings import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """SQLite database manager for bot data."""
    
    def __init__(self, db_path: str = "bot_data.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Users table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        is_admin BOOLEAN DEFAULT FALSE,
                        is_owner BOOLEAN DEFAULT FALSE,
                        preferences TEXT,
                        created_at TEXT,
                        last_activity TEXT,
                        is_active BOOLEAN DEFAULT TRUE
                    )
                """)
                
                # Host jobs table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS host_jobs (
                        job_id TEXT PRIMARY KEY,
                        user_id INTEGER,
                        host_config TEXT,
                        host_status TEXT,
                        created_at TEXT,
                        updated_at TEXT,
                        is_active BOOLEAN DEFAULT TRUE,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                """)
                
                # Bot settings table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS bot_settings (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        updated_at TEXT
                    )
                """)
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    async def save_user(self, user: User) -> bool:
        """Save user to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO users 
                    (user_id, username, first_name, last_name, is_admin, is_owner, 
                     preferences, created_at, last_activity, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user.user_id,
                    user.username,
                    user.first_name,
                    user.last_name,
                    user.is_admin,
                    user.is_owner,
                    json.dumps(user.preferences.dict()),
                    user.created_at.isoformat(),
                    user.last_activity.isoformat(),
                    user.is_active
                ))
                
                conn.commit()
                logger.debug(f"User {user.user_id} saved to database")
                return True
                
        except Exception as e:
            logger.error(f"Error saving user {user.user_id}: {e}")
            return False
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """Get user from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT user_id, username, first_name, last_name, is_admin, is_owner,
                           preferences, created_at, last_activity, is_active
                    FROM users WHERE user_id = ?
                """, (user_id,))
                
                row = cursor.fetchone()
                if row:
                    user_data = {
                        'user_id': row[0],
                        'username': row[1],
                        'first_name': row[2],
                        'last_name': row[3],
                        'is_admin': bool(row[4]),
                        'is_owner': bool(row[5]),
                        'preferences': UserPreferences(**json.loads(row[6])),
                        'created_at': datetime.fromisoformat(row[7]),
                        'last_activity': datetime.fromisoformat(row[8]),
                        'is_active': bool(row[9])
                    }
                    return User(**user_data)
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    async def get_all_users(self) -> List[User]:
        """Get all users from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT user_id, username, first_name, last_name, is_admin, is_owner,
                           preferences, created_at, last_activity, is_active
                    FROM users WHERE is_active = TRUE
                """)
                
                users = []
                for row in cursor.fetchall():
                    user_data = {
                        'user_id': row[0],
                        'username': row[1],
                        'first_name': row[2],
                        'last_name': row[3],
                        'is_admin': bool(row[4]),
                        'is_owner': bool(row[5]),
                        'preferences': UserPreferences(**json.loads(row[6])),
                        'created_at': datetime.fromisoformat(row[7]),
                        'last_activity': datetime.fromisoformat(row[8]),
                        'is_active': bool(row[9])
                    }
                    users.append(User(**user_data))
                
                return users
                
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    async def save_host_job(self, job: HostJob) -> bool:
        """Save host job to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO host_jobs 
                    (job_id, user_id, host_config, host_status, created_at, updated_at, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    job.job_id,
                    job.user_id,
                    json.dumps(job.host_config.dict()),
                    json.dumps(job.host_status.dict()),
                    job.created_at.isoformat(),
                    job.updated_at.isoformat(),
                    job.is_active
                ))
                
                conn.commit()
                logger.debug(f"Host job {job.job_id} saved to database")
                return True
                
        except Exception as e:
            logger.error(f"Error saving host job {job.job_id}: {e}")
            return False
    
    async def get_host_jobs(self, user_id: Optional[int] = None) -> List[HostJob]:
        """Get host jobs from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if user_id:
                    cursor.execute("""
                        SELECT job_id, user_id, host_config, host_status, 
                               created_at, updated_at, is_active
                        FROM host_jobs 
                        WHERE user_id = ? AND is_active = TRUE
                    """, (user_id,))
                else:
                    cursor.execute("""
                        SELECT job_id, user_id, host_config, host_status, 
                               created_at, updated_at, is_active
                        FROM host_jobs 
                        WHERE is_active = TRUE
                    """)
                
                jobs = []
                for row in cursor.fetchall():
                    job_data = {
                        'job_id': row[0],
                        'user_id': row[1],
                        'host_config': HostConfig(**json.loads(row[2])),
                        'host_status': HostStatus(**json.loads(row[3])),
                        'created_at': datetime.fromisoformat(row[4]),
                        'updated_at': datetime.fromisoformat(row[5]),
                        'is_active': bool(row[6])
                    }
                    jobs.append(HostJob(**job_data))
                
                return jobs
                
        except Exception as e:
            logger.error(f"Error getting host jobs: {e}")
            return []
    
    async def delete_host_job(self, job_id: str) -> bool:
        """Delete host job from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE host_jobs SET is_active = FALSE 
                    WHERE job_id = ?
                """, (job_id,))
                
                conn.commit()
                logger.debug(f"Host job {job_id} deleted from database")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting host job {job_id}: {e}")
            return False
    
    async def update_host_status(self, job_id: str, status: HostStatus) -> bool:
        """Update host status in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE host_jobs 
                    SET host_status = ?, updated_at = ?
                    WHERE job_id = ?
                """, (
                    json.dumps(status.dict()),
                    datetime.utcnow().isoformat(),
                    job_id
                ))
                
                conn.commit()
                logger.debug(f"Host status updated for job {job_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating host status for job {job_id}: {e}")
            return False
    
    async def save_bot_setting(self, key: str, value: Any) -> bool:
        """Save bot setting to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO bot_settings (key, value, updated_at)
                    VALUES (?, ?, ?)
                """, (key, json.dumps(value), datetime.utcnow().isoformat()))
                
                conn.commit()
                logger.debug(f"Bot setting {key} saved to database")
                return True
                
        except Exception as e:
            logger.error(f"Error saving bot setting {key}: {e}")
            return False
    
    async def get_bot_setting(self, key: str) -> Optional[Any]:
        """Get bot setting from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT value FROM bot_settings WHERE key = ?
                """, (key,))
                
                row = cursor.fetchone()
                if row:
                    return json.loads(row[0])
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting bot setting {key}: {e}")
            return None


# Global database instance
db_manager = DatabaseManager() 