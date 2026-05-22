"""Session search — invoked by /search command."""
import sys

from db import init_db, search_sessions, list_sessions


def main():
    init_db()
    args = sys.argv[1:]

    if "--recent" in args:
        try:
            idx = args.index("--recent")
            n = int(args[idx + 1]) if idx + 1 < len(args) else 5
        except (ValueError, IndexError):
            n = 5
        sessions = list_sessions(limit=n)
    elif args:
        query = " ".join(args)
        sessions = search_sessions(query)
    else:
        sessions = list_sessions(limit=10)

    if not sessions:
        print("No sessions found.")
        return

    print(f"Found {len(sessions)} session(s):\n")
    for s in sessions:
        sid = s["id"][:8] if isinstance(s["id"], str) else str(s["id"])[:8]
        date = (s.get("created_at") or "N/A")[:19]
        summary = (s.get("summary") or "No summary")[:80]
        tags = s.get("tags") or ""
        note = s.get("note") or ""
        print(f"  [{sid}] {date}")
        print(f"       {summary}")
        extras = []
        if tags:
            extras.append(f"tags: {tags}")
        if note:
            extras.append(f"note: {note}")
        if extras:
            print(f"       {', '.join(extras)}")
        print()


if __name__ == "__main__":
    main()
