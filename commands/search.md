---
description: Full-text search through saved session history
argument-hint: "<search query>"
---

# /search — Search Session History

Search through all saved sessions using full-text search (SQLite FTS5). Finds relevant past sessions based on keywords, decisions, file names, or task descriptions.

## Usage

```
/search database migration      # Search for sessions about database migration
/search --recent 5              # Show 5 most recent sessions
/search --tag bugfix            # Search sessions tagged "bugfix"
```

## What to Do

1. Execute full-text search on the SQLite FTS5 index
2. Return matching sessions ranked by relevance
3. Display session ID, date, summary snippet, and match context

Run the helper script:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/search_sessions.py" $ARGUMENTS
```
