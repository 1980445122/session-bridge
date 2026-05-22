"""Context health dashboard — invoked by /context command."""
import sys
import json
import os

from db import init_db, get_storage_stats


def main():
    init_db()

    # Try to read context_window info from stdin (piped by Claude Code)
    context_info = {}
    try:
        input_data = json.loads(sys.stdin.read())
        context_info = input_data.get("context_window", {})
    except (json.JSONDecodeError, EOFError):
        pass

    stats = get_storage_stats()

    print("=" * 50)
    print("  Session Bridge — Context Health")
    print("=" * 50)

    # Context window section
    print("\n[Context Window]")
    used = context_info.get("used", 0)
    total = context_info.get("total", 200000)
    pct = round(used / total * 100, 1) if total > 0 else 0

    bar_len = 20
    filled = int(bar_len * pct / 100)
    bar = "#" * filled + "-" * (bar_len - filled)

    status = "OK"
    if pct >= 90:
        status = "CRITICAL — compaction imminent!"
    elif pct >= 70:
        status = "WARNING — approaching compaction"
    elif pct >= 50:
        status = "Caution"

    print(f"  Usage: {bar} {pct}%")
    print(f"  Tokens: {used:,} / {total:,}")
    print(f"  Status: {status}")

    # Storage section
    print("\n[Session Storage]")
    print(f"  Saved sessions: {stats['count']}")
    print(f"  Database size:  {stats['size_mb']} MB")
    if stats.get("oldest_session"):
        print(f"  Oldest session: {stats['oldest_session'][:19] if stats['oldest_session'] else 'N/A'}")
    if stats.get("newest_session"):
        print(f"  Newest session: {stats['newest_session'][:19] if stats['newest_session'] else 'N/A'}")
    print(f"  Cloud synced:   {stats.get('cloud_synced', 0)}/{stats['count']}")

    # Free tier info
    max_free = int(os.environ.get("SESSION_BRIDGE_MAX_SESSIONS", "50"))
    remaining = max(0, max_free - stats["count"])
    print(f"\n[Free Tier] {remaining} of {max_free} local slots remaining")

    print("=" * 50)


if __name__ == "__main__":
    main()
