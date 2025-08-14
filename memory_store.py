# memory_store.py
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional

SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  role TEXT CHECK(role IN ('user','assistant')) NOT NULL,
  content TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_messages_session_time ON messages(session_id, created_at);
CREATE INDEX IF NOT EXISTS idx_messages_session_role_time ON messages(session_id, role, created_at);
"""

class MemoryStore:
    def __init__(self, db_path: str = "data/memory.sqlite"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute(SCHEMA)
        self.conn.commit()

    def add_message(self, session_id: str, user_id: str, role: str, content: str, ts: Optional[datetime]=None):
        ts = ts or datetime.utcnow()
        self.conn.execute(
            "INSERT INTO messages (session_id, user_id, role, content, created_at) VALUES (?,?,?,?,?)",
            (session_id, user_id, role, content, ts.isoformat())
        )
        self.conn.commit()

    def get_messages(
        self, session_id: str, since: Optional[datetime]=None, until: Optional[datetime]=None,
        role: Optional[str]=None, limit: Optional[int]=None
    ) -> List[Dict]:
        q = "SELECT role, content, created_at FROM messages WHERE session_id=?"
        args = [session_id]
        if role:
            q += " AND role=?"; args.append(role)
        if since:
            q += " AND created_at>=?"; args.append(since.isoformat())
        if until:
            q += " AND created_at<?"; args.append(until.isoformat())
        q += " ORDER BY created_at ASC"
        if limit:
            q += f" LIMIT {int(limit)}"
        cur = self.conn.execute(q, args)
        rows = cur.fetchall()
        return [{"role": r[0], "content": r[1], "created_at": r[2]} for r in rows]

    def yesterday_window(self, tz_offset_hours: int = 0):
        # crude “yesterday” window; adjust offset if you want local time semantics
        now = datetime.utcnow()
        start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end   = start + timedelta(days=1)
        # If you prefer local (Europe/Lisbon) semantics, compute start/end in local tz and convert to UTC.
        return start, end
