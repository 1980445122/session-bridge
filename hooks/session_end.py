"""SessionEnd hook — cleanup and final persistence."""
import sys
import json
import os

HOOK_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HOOK_ROOT, "scripts"))

from db import init_db, get_storage_stats


def main():
    init_db()

    try:
        input_data = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        input_data = {}

    session_id = input_data.get("session_id", "unknown")

    # Cleanup old sessions (keep max N for free tier)
    max_sessions = int(os.environ.get("SESSION_BRIDGE_MAX_SESSIONS", "50"))
    try:
        import sqlite3
        conn = sqlite3.connect(os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data", "sessions.db"))
        conn.execute("PRAGMA journal_mode=WAL")
        count = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
        if count > max_sessions:
            excess = count - max_sessions
            conn.execute(
                "DELETE FROM sessions WHERE id IN "
                "(SELECT id FROM sessions ORDER BY created_at ASC LIMIT ?)",
                (excess,))
            conn.execute("INSERT OR REPLACE INTO meta (key, value) VALUES ('last_cleanup', ?)",
                         (f"Deleted {excess} old sessions",))
            conn.commit()
        conn.close()
    except Exception:
        pass

    stats = get_storage_stats()
    print(json.dumps({
        "session_id": session_id,
        "storage_stats": stats
    }))


if __name__ == "__main__":
    main()
