# AgentLog Development Guide

## Auto-Logging

AgentLog tracks its own development. Every session, git commit, and file change is logged automatically.

### Before starting work
1. `agentlog init --tool hermes --project agentlog`
2. The git post-commit hook auto-logs every commit
3. Use `agentlog track note '...'` for important decisions

### Before ending session
1. `agentlog summary` — generates handoff document
2. Copy the summary to the next session prompt

### Searching
- `agentlog search 'feature name'` — find related work
- `agentlog status` — check current progress

## Development

### Install for development
```bash
pip install -e .
```

### Test
```bash
agentlog init --tool test
agentlog track file test.py --operation created
agentlog track command 'pytest'
agentlog search test
agentlog summary
agentlog sessions
```

### Release
```bash
python setup.py sdist bdist_wheel
twine upload dist/*
```

## Key Design Decisions

1. **SQLite local first** — no cloud dependency, portable
2. **Cross-platform** — works with any AI tool, not tied to one
3. **CLI-native** — works in terminal, no GUI needed
4. **Auto-logging via hooks** — shell hooks + git hooks
5. **MIT license** — maximum adoption, donations for sustainability

## Current Status

- Core CLI: ✅ sessions, track, search, summary, export
- Auto-logging: ✅ shell hooks, git hooks
- Dashboard: ✅ tui, watch
- Monetization: ❌ open source, donation-based
