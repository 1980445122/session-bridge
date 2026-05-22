---
description: Display context window usage and session storage statistics
---

# /context — Context Health Dashboard

Display the current state of your context window, session storage usage, and any warnings about approaching compaction thresholds.

## What Gets Displayed

- **Context Window**: Current usage percentage, token count, warning thresholds
- **Session Storage**: Number of saved sessions, database size, oldest/newest session
- **Cloud Status**: Sync state (Pro/Team only)
- **Health Alerts**: Warnings if context is near compaction, or if storage is full

## What to Do

Run the context health script and display the results in a formatted way:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/context_health.py"
```

Present the output clearly to the user with any relevant warnings or recommendations.
