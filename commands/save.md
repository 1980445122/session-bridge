---
description: Manually save current session context with an optional note
argument-hint: "[optional note]"
---

# /save — Manual Session Save

Save the current session context immediately. This creates a snapshot of the current conversation state, including key decisions, current tasks, and important file references.

## Usage

```
/save                    # Save with auto-generated label
/save fixed login bug    # Save with custom note
```

## What Gets Saved

- Current task and progress
- Key decisions made in this session
- Files being worked on
- Conversation summary (last 2000 tokens)
- Timestamp and session duration

## What to Do

Read the current conversation transcript and generate a structured session summary. Call the helper script:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/save_session.py" "$ARGUMENTS"
```

After the script runs, report the result to the user: session ID, summary preview, and storage location.
