import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "vr_recommender.db")

class Database:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_conn(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _init_db(self):
        """Initialize the database schema."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # Interaction Logs Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interaction_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                session_id TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                query_text TEXT,
                intent TEXT,
                response_text TEXT,
                recommended_apps TEXT, -- JSON string
                metadata TEXT -- JSON string for extra info like latency, source
            )
        """)
        
        # Indexes for faster filtering
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON interaction_logs(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON interaction_logs(timestamp)")
        
        conn.commit()
        conn.close()

    def log_interaction(self, 
                        user_id: str, 
                        query_text: str, 
                        response_text: str, 
                        intent: str = "unknown",
                        session_id: Optional[str] = None,
                        recommended_apps: list = None,
                        metadata: Dict[str, Any] = None):
        """Insert a new interaction log."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        apps_json = json.dumps(recommended_apps) if recommended_apps else "[]"
        meta_json = json.dumps(metadata) if metadata else "{}"
        
        cursor.execute("""
            INSERT INTO interaction_logs 
            (user_id, session_id, query_text, intent, response_text, recommended_apps, metadata, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, session_id, query_text, intent, response_text, apps_json, meta_json, datetime.now()))
        
        conn.commit()
        conn.close()

    def get_logs(self, limit: int = 50, offset: int = 0, user_id: str = None):
        """Retrieve logs with optional filtering."""
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row # Allow dict-like access
        cursor = conn.cursor()
        
        query = "SELECT * FROM interaction_logs"
        params = []
        
        if user_id:
            query += " WHERE user_id = ?"
            params.append(user_id)
            
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        conn.close()
        return [dict(row) for row in rows]

    def get_stats(self):
        """Get basic aggregation stats."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        stats = {}
        
        # Total interactions
        cursor.execute("SELECT COUNT(*) FROM interaction_logs")
        stats['total_interactions'] = cursor.fetchone()[0]
        
        # Unique users
        cursor.execute("SELECT COUNT(DISTINCT user_id) FROM interaction_logs")
        stats['unique_users'] = cursor.fetchone()[0]
        
        # Top intents (if we track them)
        cursor.execute("SELECT intent, COUNT(*) as c FROM interaction_logs GROUP BY intent ORDER BY c DESC LIMIT 5")
        stats['top_intents'] = cursor.fetchall()
        
        conn.close()
        return stats
