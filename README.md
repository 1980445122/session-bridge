# Session Bridge — Never Lose Context Again

Session Bridge is the first Claude Code plugin that automatically saves and restores session context before compaction. One command to install. Zero configuration needed.

## Why Session Bridge?

Claude Code's #1 user pain point is **context loss after compaction**. You spend 30 minutes building context, then compaction hits and Claude forgets everything. Session Bridge solves this:

- **Auto-save** before every compaction (PreCompact hook)
- **One-click restore** — use `/restore` to bring back lost context
- **Full-text search** — find past sessions with `/search`
- **Context health** — monitor your context window with `/context`

## Quick Install

```bash
claude plugins install session-bridge@claude-plugins-official
```

Or manually:

```bash
git clone https://github.com/1980445122/session-bridge.git
cd session-bridge
python scripts/install.py
```

## Commands

| Command | Description |
|---------|-------------|
| `/save [note]` | Manually save current session |
| `/restore [id\|date]` | Restore a previous session's context |
| `/search <query>` | Full-text search across saved sessions |
| `/context` | View context window usage and storage stats |

## Pricing

| Feature | Free | Pro ($6/mo) | Team ($15/mo) |
|---------|------|-------------|---------------|
| Local auto-save/restore | 5 sessions | Unlimited | Unlimited |
| `/search` and `/context` | Yes | Yes | Yes |
| Cloud sync | No | Yes | Yes |
| Cross-machine restore | No | Yes | Yes |
| Shared team knowledge base | No | No | Yes |

## Requirements

- Python 3.10+
- DeepSeek API key (uses your existing key, no extra cost)
- Claude Code v2.1+

## Privacy

Session Bridge stores all data locally in SQLite. Cloud sync is opt-in (Pro/Team only). Your DeepSeek API key is never sent to our servers — all AI summarization happens through your own API key.
