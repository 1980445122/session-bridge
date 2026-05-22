"""Manual session save — invoked by /save command."""
import sys
import os
import json
import uuid
from datetime import datetime, timezone

from db import init_db, save_session

# Try to get transcript from environment or Claude's current session
TRANSCRIPT_PATHS = [
    os.path.expandvars(r"%TEMP%\claude_transcript.txt"),
    os.path.join(os.path.dirname(__file__), "..", "data", "current_transcript.txt"),
]


def main():
    init_db()
    note = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    session_id = str(uuid.uuid4())[:8]
    project_path = os.getcwd()

    # Read transcript if available
    transcript = ""
    for tp in TRANSCRIPT_PATHS:
        if os.path.exists(tp):
            try:
                with open(tp, "r", encoding="utf-8") as f:
                    transcript = f.read()
                break
            except Exception:
                continue

    from summarizer import summarize

    if transcript.strip():
        result = summarize(transcript)
    else:
        result = {"error": "No transcript available for summarization"}

    if "error" in result:
        print(f"Warning: Could not generate summary ({result['error']})")
        print(f"Session saved with ID: {session_id} (manual snapshot, no AI summary)")
        save_session(
            session_id=session_id,
            project_path=project_path,
            summary=f"Manual save{' — ' + note if note else ''}",
            note=note,
            raw_snippet=transcript[-2000:] if transcript else ""
        )
    else:
        save_session(
            session_id=session_id,
            project_path=project_path,
            summary=result.get("summary", ""),
            decisions=result.get("decisions", ""),
            current_tasks=result.get("current_tasks", ""),
            key_files=result.get("key_files", ""),
            tags=result.get("tags", ""),
            note=note,
            raw_snippet=transcript[-3000:] if transcript else ""
        )
        print(f"Session saved: {session_id}")
        print(f"Summary: {result.get('summary', 'N/A')}")
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        print(f"Timestamp: {now}")
        if note:
            print(f"Note: {note}")


if __name__ == "__main__":
    main()
