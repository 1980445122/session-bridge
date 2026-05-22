---
description: Restore session context from a previous save
argument-hint: "[session_id or date]"
---

# /restore — Restore Session Context

Restore the context from a previously saved session. This injects the saved summary, decisions, task progress, and file references back into the current conversation.

## Usage

```
/restore                  # Restore most recent session
/restore abc123           # Restore specific session by ID
/restore 2026-05-22      # Restore sessions from a specific date
/restore --cloud          # Restore from cloud (Pro/Team only)
/restore --list           # List available sessions to restore
```

## What to Do

1. If `--list` is passed, list available saved sessions
2. Otherwise, query the SQLite database for the matching session(s)
3. Display the restored context to the user

Run the helper script:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/restore_session.py" $ARGUMENTS
```
