"""Local SQLite cache layer for Notion data."""

import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional, List


class LocalCache:
    """SQLite-based cache for Notion API responses."""
    
    def __init__(self, db_path: str = ".notion_cache.db"):
        """Initialize cache database.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._create_tables()
    
    def _create_tables(self):
        """Create cache tables if they don't exist."""
        cursor = self.conn.cursor()
        
        # Main cache table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )
        """)
        
        # Estimation learning table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS estimation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                task_name TEXT,
                category TEXT,
                complexity TEXT,
                estimated_hours REAL,
                actual_hours REAL,
                accuracy REAL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Task completion history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                task_name TEXT,
                status TEXT,
                priority TEXT,
                category TEXT,
                sprint TEXT,
                completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Analytics snapshots
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_date DATE NOT NULL,
                total_tasks INTEGER,
                completed_tasks INTEGER,
                in_progress_tasks INTEGER,
                blocked_tasks INTEGER,
                velocity REAL,
                health_score REAL,
                data JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.commit()
    
    @staticmethod
    def generate_key(*args) -> str:
        """Generate cache key from arguments."""
        key_str = ":".join(str(arg) for arg in args if arg is not None)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, key: str, max_age: Optional[int] = None) -> Optional[Any]:
        """Get value from cache.
        
        Args:
            key: Cache key
            max_age: Maximum age in seconds (None = no expiration check)
            
        Returns:
            Cached value or None if not found/expired
        """
        cursor = self.conn.cursor()
        
        if max_age:
            min_time = datetime.now() - timedelta(seconds=max_age)
            cursor.execute(
                "SELECT value FROM cache WHERE key = ? AND created_at > ?",
                (key, min_time)
            )
        else:
            cursor.execute("SELECT value FROM cache WHERE key = ?", (key,))
        
        row = cursor.fetchone()
        if row:
            return json.loads(row[0])
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time-to-live in seconds (None = no expiration)
        """
        cursor = self.conn.cursor()
        
        value_json = json.dumps(value)
        expires_at = None
        if ttl:
            expires_at = datetime.now() + timedelta(seconds=ttl)
        
        cursor.execute(
            "INSERT OR REPLACE INTO cache (key, value, created_at, expires_at) VALUES (?, ?, ?, ?)",
            (key, value_json, datetime.now(), expires_at)
        )
        self.conn.commit()
    
    def invalidate(self, key: str):
        """Remove specific key from cache."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM cache WHERE key = ?", (key,))
        self.conn.commit()
    
    def invalidate_pattern(self, pattern: str):
        """Remove all keys matching pattern (SQL LIKE syntax)."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM cache WHERE key LIKE ?", (pattern,))
        self.conn.commit()
    
    def clear(self):
        """Clear all cached data."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM cache")
        self.conn.commit()
    
    def cleanup_expired(self):
        """Remove expired entries."""
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM cache WHERE expires_at IS NOT NULL AND expires_at < ?",
            (datetime.now(),)
        )
        self.conn.commit()
    
    def record_task_completion(self, task_data: dict):
        """Record task completion for learning."""
        cursor = self.conn.cursor()
        
        # Record in estimation history if we have hour data
        if task_data.get("estimated_hours") and task_data.get("actual_hours"):
            accuracy = task_data["actual_hours"] / task_data["estimated_hours"]
            cursor.execute("""
                INSERT INTO estimation_history 
                (task_id, task_name, category, complexity, estimated_hours, actual_hours, accuracy)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                task_data["task_id"],
                task_data.get("task_name"),
                task_data.get("category"),
                task_data.get("complexity"),
                task_data["estimated_hours"],
                task_data["actual_hours"],
                accuracy
            ))
        
        # Record in task history
        cursor.execute("""
            INSERT INTO task_history 
            (task_id, task_name, status, priority, category, sprint, completed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            task_data["task_id"],
            task_data.get("task_name"),
            task_data.get("status"),
            task_data.get("priority"),
            task_data.get("category"),
            task_data.get("sprint"),
            datetime.now()
        ))
        
        self.conn.commit()
    
    def get_estimation_patterns(self, category: Optional[str] = None, complexity: Optional[str] = None) -> List[dict]:
        """Get historical estimation patterns for learning."""
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM estimation_history WHERE 1=1"
        params = []
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if complexity:
            query += " AND complexity = ?"
            params.append(complexity)
        
        query += " ORDER BY completed_at DESC LIMIT 50"
        
        cursor.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def close(self):
        """Close database connection."""
        self.conn.close()
