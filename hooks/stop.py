"""Stop hook — save final session state when Claude Code stops."""
import sys
import json
import os

HOOK_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HOOK_ROOT, "scripts"))

from db import init_db, save_session
from summarizer import summarize


def main():
    init_db()

    try:
        input_data = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        return

    session_id = input_data.get("session_id", "")
    transcript_path = input_data.get("transcript_path", "")
    project_path = os.getcwd()

    if not session_id or not transcript_path:
        return

    if not os.path.exists(transcript_path):
        return

    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            transcript = f.read()
    except Exception:
        return

    if not transcript.strip():
        return

    result = summarize(transcript)

    if "error" in result:
        return

    snippet = transcript[-3000:] if len(transcript) > 3000 else transcript
    save_session(
        session_id=session_id,
        project_path=project_path,
        summary=result.get("summary", ""),
        decisions=result.get("decisions", ""),
        current_tasks=result.get("current_tasks", ""),
        key_files=result.get("key_files", ""),
        tags=result.get("tags", ""),
        note="[auto-saved on stop]",
        raw_snippet=snippet
    )


if __name__ == "__main__":
    main()
