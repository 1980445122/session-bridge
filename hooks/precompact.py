"""PreCompact hook — auto-save session context before compaction."""
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
        print(json.dumps({"additionalContext": ""}))
        return

    session_id = input_data.get("session_id", "unknown")
    transcript_path = input_data.get("transcript_path", "")
    project_path = os.getcwd()

    # Read the transcript
    transcript = ""
    if transcript_path and os.path.exists(transcript_path):
        try:
            with open(transcript_path, "r", encoding="utf-8") as f:
                transcript = f.read()
        except Exception:
            pass

    if not transcript:
        print(json.dumps({"additionalContext": ""}))
        return

    # Generate summary via DeepSeek
    result = summarize(transcript)

    if "error" in result:
        # Summarization failed — still save raw snippet
        summary_text = "Summary unavailable (API error)"
        decisions = ""
        tasks = ""
        key_files = ""
        tags = ""
    else:
        summary_text = result.get("summary", "")
        decisions = result.get("decisions", "")
        tasks = result.get("current_tasks", "")
        key_files = result.get("key_files", "")
        tags = result.get("tags", "")

    # Save to SQLite
    snippet = transcript[-3000:] if len(transcript) > 3000 else transcript
    save_session(
        session_id=session_id,
        project_path=project_path,
        summary=summary_text,
        decisions=decisions,
        current_tasks=tasks,
        key_files=key_files,
        tags=tags,
        raw_snippet=snippet
    )

    # Build context injection for compaction prompt
    context_block = build_context_block(summary_text, decisions, tasks, key_files)

    print(json.dumps({"additionalContext": context_block}))


def build_context_block(summary: str, decisions: str, tasks: str, files: str) -> str:
    parts = ["[Session Bridge: saved context from before compaction]"]
    if summary:
        parts.append(f"Summary: {summary}")
    if decisions:
        parts.append(f"Key decisions:\n{decisions}")
    if tasks:
        parts.append(f"Current tasks:\n{tasks}")
    if files:
        parts.append(f"Key files:\n{files}")
    return "\n\n".join(parts)


if __name__ == "__main__":
    main()
