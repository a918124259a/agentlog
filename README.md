# AgentLog 🕵️

**Cross-platform AI Agent Action Tracker**

Your AI agent forgets everything between sessions. **AgentLog doesn't.**

AgentLog is a local-first CLI tool that logs every action your AI agents take — files changed, commands run, git commits made, API calls sent — across **all** your AI tools. Searchable. Replayable. Portable.

```bash
# Install
pip install agentlog

# Start tracking
agentlog init

# Log actions naturally
agentlog track file src/app.py --operation modified
agentlog track command 'pytest tests/'
agentlog track note 'Fixed race condition in auth module'
agentlog track git 'feat: add rate limiting' --hash abc1234f

# Search everything
agentlog search 'auth bug'
# → Found 3 results...
#   2026-05-21  [hermes] note: Fixed auth bug in login flow
#   2026-05-20  [cursor] file: src/auth/login.ts
#   2026-05-19  [codex]  commit: fix: auth token refresh race

# Hand off context between sessions
agentlog summary
# → Generates a complete handoff document
```

## Why AgentLog?

Every AI coding tool **forgets what it did** between sessions:

- Claude Code: "I don't remember our last conversation"
- Codex: "Starting fresh"
- Cursor: New session, blank slate
- ChatGPT: "Sorry, I can't see previous conversations"

You lose context. You re-explain. You re-debug.

AgentLog is the **context bridge** — a persistent, searchable log that spans all your AI tools.

## Features

| Feature | Description |
|---------|-------------|
| 📁 **File Tracking** | Every file created, modified, or deleted |
| 💻 **Command Log** | Every command executed |
| 🔀 **Git Integration** | Commits with messages and branches |
| 🔌 **API Calls** | External API calls made |
| 🔍 **Full-Text Search** | Search across all sessions and tools |
| 📋 **Session Summary** | One-page handoff document |
| 🔄 **Cross-Platform** | Works with Claude Code, Codex, Cursor, Hermes, ChatGPT |

## Quick Start

### Installation

```bash
pip install agentlog
# OR from source:
git clone https://github.com/a918124259a/agentlog.git
cd agentlog && pip install -e .
```

### First Session

```bash
# Start tracking
agentlog init

# Work as usual, but log key actions:
agentlog track file src/feature.py --operation created
agentlog track command 'python manage.py test'
agentlog track note 'Found the root cause — null pointer in config parser'

# Check progress
agentlog status

# Search later
agentlog search 'root cause'
```

### Session Handoff

When switching between tools (e.g., Claude Code → Cursor → back to Claude):

```bash
# Before leaving, generate a summary:
agentlog summary
# Copy-paste this into your next AI session

# When you return, search for context:
agentlog search 'what was I working on'
```

## Integrations

### Claude Code

Add to your `CLAUDE.md`:

```markdown
## Session Logging
- Before ending each session, run: `agentlog summary`
- Log key changes with: `agentlog track file <path>`
- Track commands with: `agentlog track command '<cmd>'`
```

### Hermes Agent (auto-logging)

Add to your `.env` or cron setup:

```bash
alias track='agentlog track'
# Auto-log every command
preexec() { agentlog track command "$1"; }
```

## Commands

| Command | Description |
|---------|-------------|
| `agentlog init` | Start a new session |
| `agentlog track file <path>` | Log a file change |
| `agentlog track command <cmd>` | Log a command |
| `agentlog track note <text>` | Add a freeform note |
| `agentlog track git <msg> --hash <h>` | Log a git commit |
| `agentlog track api <url>` | Log an API call |
| `agentlog status` | Current session overview |
| `agentlog search <query>` | Search all history |
| `agentlog summary [session_id]` | Generate handoff doc |
| `agentlog sessions` | List all sessions |

## Data Storage

All data is stored locally in `~/.agentlog.db` (SQLite). Your data never leaves your machine.

```sql
-- Tables: sessions, actions, files, git_commits
-- Portable: just copy the .db file
```

## Roadmap

- [x] Core CLI with SQLite storage
- [x] Session init, track, status, search, summary
- [x] File, command, note, API, git action types
- [ ] Auto-detect AI tools via environment
- [ ] Web dashboard for browsing logs
- [ ] Cloud sync (Pro tier)
- [ ] Team sharing (Enterprise tier)
- [ ] SOC2/ISO audit export
- [ ] VS Code extension
- [ ] Claude Code MCP server

## Pricing

| Plan | Price | Features |
|------|-------|----------|
| **Free** | $0 | Local CLI, full search, unlimited sessions |
| **Pro** | $9/mo | Cloud sync, web dashboard, export to JSON/CSV |
| **Enterprise** | $49/mo | Team sharing, SOC2 export, RBAC, SSO |

## License

MIT — free to use, modify, and distribute.

---

<p align="center">
  <b>Built with ❤️ for developers tired of repeating themselves to AI</b><br>
  <a href="https://github.com/a918124259a/agentlog">GitHub</a> ·
  <a href="https://github.com/a918124259a/agentlog/issues">Issues</a>
</p>
