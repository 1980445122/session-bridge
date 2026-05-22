"""Session restore — invoked by /restore command."""
import sys
import os

from db import init_db, list_sessions, get_session, search_sessions


def main():
    init_db()
    args = sys.argv[1:]

    if "--list" in args:
        sessions = list_sessions(limit=20)
        if not sessions:
            print("No saved sessions found.")
            return
        print(f"{'ID':<10} {'Date':<22} {'Summary':<60}")
        print("-" * 92)
        for s in sessions:
            sid = s["id"][:8]
            date = s["created_at"][:19] if s["created_at"] else "N/A"
            summary = (s.get("summary") or "No summary")[:58]
            print(f"{sid:<10} {date:<22} {summary:<60}")
        return

    target = args[0] if args else None

    if not target:
        # Restore most recent session
        sessions = list_sessions(limit=1)
        if not sessions:
            print("No saved sessions to restore.")
            return
        target = sessions[0]["id"]

    session = get_session(target)
    if not session:
        # Try date search
        sessions = list_sessions(limit=50)
        matches = [s for s in sessions if target in s.get("created_at", "")]
        if matches:
            session = get_session(matches[0]["id"])
        else:
            # Try FTS search
            results = search_sessions(target, limit=1)
            if results:
                session = get_session(results[0]["id"])

    if not session:
        print(f"No session found matching: {target}")
        return

    # Output restored context in a format Claude Code can use
    print("--- Restored Session Context ---")
    print(f"Session ID: {session['id'][:8]}")
    print(f"Date: {session.get('created_at', 'N/A')[:19]}")
    print(f"Project: {session.get('project_path', 'N/A')}")
    print()
    if session.get("summary"):
        print(f"Summary: {session['summary']}")
    if session.get("decisions"):
        print(f"\nKey Decisions:\n{session['decisions']}")
    if session.get("current_tasks"):
        print(f"\nCurrent Tasks:\n{session['current_tasks']}")
    if session.get("key_files"):
        print(f"\nKey Files:\n{session['key_files']}")
    if session.get("note"):
        print(f"\nNote: {session['note']}")


if __name__ == "__main__":
    main()
