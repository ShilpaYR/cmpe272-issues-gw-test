import sqlite3, os, time
from typing import List, Dict, Any

DB_PATH = os.getenv("EVENTS_DB", "events.db")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS events(
            id TEXT PRIMARY KEY,
            event TEXT NOT NULL,
            action TEXT,
            issue_number INTEGER,
            timestamp TEXT NOT NULL
        )
        """)

def save_event(e: Dict[str, Any]):
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        # ignore conflicts (idempotent)
        conn.execute("INSERT OR IGNORE INTO events(id,event,action,issue_number,timestamp) VALUES(?,?,?,?,?)",
                     (e["id"], e["event"], e.get("action"), e.get("issue_number"), e["timestamp"]))

def last_events(limit: int=50) -> List[Dict[str, Any]]:
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("SELECT id,event,action,issue_number,timestamp FROM events ORDER BY timestamp DESC LIMIT ?",
                            (limit,)).fetchall()
        return [{"id":r[0],"event":r[1],"action":r[2],"issue_number":r[3],"timestamp":r[4]} for r in rows]
