#!/usr/bin/env python3
"""
AgentLog — Cross-platform AI Agent Action Tracker

Log, search, and replay what your AI agents did across all your tools.

Usage:
    agentlog init                  Initialize a tracking session
    agentlog track <action> [data] Record an action (file, command, api, note)
    agentlog status                Show current session status
    agentlog search <query>        Search past sessions and actions
    agentlog summary [session_id]  Generate context handoff document
    agentlog sessions              List all sessions
"""

import argparse
import json
import os
import sqlite3
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path


DB_PATH = os.path.expanduser("~/.agentlog.db")


def get_db():
    """Get or create SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            tool TEXT NOT NULL DEFAULT 'unknown',
            started_at REAL NOT NULL,
            ended_at REAL,
            project TEXT,
            summary TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            timestamp REAL NOT NULL,
            action_type TEXT NOT NULL,
            description TEXT,
            details TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            timestamp REAL NOT NULL,
            operation TEXT NOT NULL,
            file_path TEXT NOT NULL,
            diff_summary TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS git_commits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            timestamp REAL NOT NULL,
            hash TEXT,
            message TEXT,
            branch TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    """)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.commit()
    return conn


def get_active_session(conn):
    """Get active (unended) session or None."""
    cursor = conn.execute(
        "SELECT * FROM sessions WHERE ended_at IS NULL ORDER BY started_at DESC LIMIT 1"
    )
    return cursor.fetchone()


def format_timestamp(ts):
    """Format unix timestamp to human-readable."""
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


def format_duration(start, end=None):
    """Format duration between two timestamps."""
    end = end or time.time()
    seconds = int(end - start)
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    else:
        return f"{seconds // 3600}h {(seconds % 3600) // 60}m"


def cmd_init(args, conn):
    """Initialize a new tracking session."""
    session_id = str(uuid.uuid4())[:8]
    tool = args.tool or detect_tool()
    project = args.project or detect_project()
    
    conn.execute(
        "INSERT INTO sessions (id, tool, started_at, project) VALUES (?, ?, ?, ?)",
        (session_id, tool, time.time(), project)
    )
    conn.commit()
    
    print(f"✅ AgentLog session started")
    print(f"   ID:      {session_id}")
    print(f"   Tool:    {tool}")
    print(f"   Project: {project or '(none)'}")
    print(f"   Log:     {DB_PATH}")
    print()
    print(f"   Commands:")
    print(f"     agentlog track file /path/to/file.py      # Log a file change")
    print(f"     agentlog track command 'npm install'       # Log a command run")
    print(f"     agentlog track note 'Fixed auth bug'       # Add a note")
    print(f"     agentlog track api 'POST /api/users'       # Log an API call")
    print(f"     agentlog status                            # Check session")
    print(f"     agentlog search 'auth bug'                 # Search history")


def cmd_track(args, conn):
    """Record an action in the current session."""
    session = get_active_session(conn)
    if not session:
        print("❌ No active session. Run 'agentlog init' first.")
        return 1
    
    action_type = args.action_type
    data = args.data
    
    if action_type == "file":
        operation = args.operation or "modified"
        conn.execute(
            "INSERT INTO files (session_id, timestamp, operation, file_path, diff_summary) VALUES (?, ?, ?, ?, ?)",
            (session["id"], time.time(), operation, data, args.diff or "")
        )
        print(f"📁 File {operation}: {data}")
        
    elif action_type == "command":
        conn.execute(
            "INSERT INTO actions (session_id, timestamp, action_type, description) VALUES (?, ?, ?, ?)",
            (session["id"], time.time(), "command", data)
        )
        print(f"💻 Command: {data[:80]}{'...' if len(data) > 80 else ''}")
        
    elif action_type == "note":
        conn.execute(
            "INSERT INTO actions (session_id, timestamp, action_type, description) VALUES (?, ?, ?, ?)",
            (session["id"], time.time(), "note", data)
        )
        print(f"📝 Note: {data}")
        
    elif action_type == "api":
        conn.execute(
            "INSERT INTO actions (session_id, timestamp, action_type, description, details) VALUES (?, ?, ?, ?, ?)",
            (session["id"], time.time(), "api", data, args.details or "")
        )
        print(f"🔌 API: {data}")
        
    elif action_type == "git":
        conn.execute(
            "INSERT INTO git_commits (session_id, timestamp, hash, message, branch) VALUES (?, ?, ?, ?, ?)",
            (session["id"], time.time(), args.hash or "", data, args.branch or "")
        )
        hash_str = f" ({args.hash[:8]})" if args.hash else ""
        print(f"🔀 Commit{hash_str}: {data[:60]}")
    
    else:
        # Generic action
        conn.execute(
            "INSERT INTO actions (session_id, timestamp, action_type, description, details) VALUES (?, ?, ?, ?, ?)",
            (session["id"], time.time(), action_type, data, args.details or "")
        )
        print(f"📋 {action_type}: {data[:80]}")
    
    conn.commit()


def cmd_status(args, conn):
    """Show current session status."""
    session = get_active_session(conn)
    if not session:
        print("📭 No active session.")
        print("   Start one:  agentlog init")
        return
    
    # Count actions in this session
    action_count = conn.execute(
        "SELECT COUNT(*) as c FROM actions WHERE session_id = ?", (session["id"],)
    ).fetchone()["c"]
    
    file_count = conn.execute(
        "SELECT COUNT(*) as c FROM files WHERE session_id = ?", (session["id"],)
    ).fetchone()["c"]
    
    commit_count = conn.execute(
        "SELECT COUNT(*) as c FROM git_commits WHERE session_id = ?", (session["id"],)
    ).fetchone()["c"]
    
    print(f"📊 Session Status")
    print(f"   ID:       {session['id']}")
    print(f"   Tool:     {session['tool']}")
    print(f"   Project:  {session['project'] or '(none)'}")
    print(f"   Started:  {format_timestamp(session['started_at'])}")
    print(f"   Duration: {format_duration(session['started_at'])}")
    print(f"   Actions:  {action_count} commands/notes/API calls")
    print(f"   Files:    {file_count} changes")
    print(f"   Commits:  {commit_count} git commits")


def cmd_search(args, conn):
    """Search across all sessions and actions."""
    query = args.query
    if not query:
        print("❌ Provide a search query.")
        return 1
    
    search_term = f"%{query}%"
    
    # Search in actions
    actions = conn.execute(
        """SELECT a.*, s.tool, s.project 
           FROM actions a 
           JOIN sessions s ON a.session_id = s.id 
           WHERE a.description LIKE ? OR a.details LIKE ?
           ORDER BY a.timestamp DESC LIMIT 20""",
        (search_term, search_term)
    ).fetchall()
    
    # Search in files
    files = conn.execute(
        """SELECT f.*, s.tool, s.project 
           FROM files f 
           JOIN sessions s ON f.session_id = s.id 
           WHERE f.file_path LIKE ? OR f.diff_summary LIKE ?
           ORDER BY f.timestamp DESC LIMIT 10""",
        (search_term, search_term)
    ).fetchall()
    
    # Search in commits
    commits = conn.execute(
        """SELECT c.*, s.tool, s.project 
           FROM git_commits c 
           JOIN sessions s ON c.session_id = s.id 
           WHERE c.message LIKE ?
           ORDER BY c.timestamp DESC LIMIT 10""",
        (search_term,)
    ).fetchall()
    
    total = len(actions) + len(files) + len(commits)
    if total == 0:
        print(f"🔍 No results for '{query}'")
        return
    
    print(f"🔍 Found {total} results for '{query}'")
    print()
    
    if actions:
        print(f"── Actions ({len(actions)}) ──")
        for a in actions:
            tool_tag = f"[{a['tool']}]" if a['tool'] != 'unknown' else ""
            print(f"  {format_timestamp(a['timestamp'])} {tool_tag} {a['action_type']}: {a['description'][:100]}")
        print()
    
    if files:
        print(f"── Files ({len(files)}) ──")
        for f in files:
            print(f"  {format_timestamp(f['timestamp'])} {f['operation']}: {f['file_path']}")
        print()
    
    if commits:
        print(f"── Git Commits ({len(commits)}) ──")
        for c in commits:
            h = c['hash'][:8] if c['hash'] else "?"
            print(f"  {format_timestamp(c['timestamp'])} [{h}] {c['message'][:80]}")
        print()


def cmd_sessions(args, conn):
    """List all sessions."""
    limit = args.limit or 20
    sessions = conn.execute(
        "SELECT * FROM sessions ORDER BY started_at DESC LIMIT ?", (limit,)
    ).fetchall()
    
    if not sessions:
        print("📭 No sessions recorded yet.")
        return
    
    print(f"📋 Recent Sessions ({len(sessions)})")
    print()
    for s in sessions:
        ended = s['ended_at'] is not None
        duration = format_duration(s['started_at'], s['ended_at']) if ended else "🟢 active"
        
        action_count = conn.execute(
            "SELECT COUNT(*) as c FROM actions WHERE session_id = ?", (s['id'],)
        ).fetchone()["c"]
        
        print(f"  [{s['id']}] {s['tool']:15} {duration:12}  {action_count:3} actions  {s['project'] or ''}")
        print(f"         {format_timestamp(s['started_at'])}")
        if s['summary']:
            print(f"         {s['summary'][:80]}")
        print()


def cmd_summary(args, conn):
    """Generate a context handoff summary for a session."""
    session_id = args.session_id
    
    if session_id:
        session = conn.execute(
            "SELECT * FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
    else:
        session = get_active_session(conn)
    
    if not session:
        print("❌ No session found.")
        return 1
    
    actions = conn.execute(
        "SELECT * FROM actions WHERE session_id = ? ORDER BY timestamp", (session['id'],)
    ).fetchall()
    
    files = conn.execute(
        "SELECT * FROM files WHERE session_id = ? ORDER BY timestamp", (session['id'],)
    ).fetchall()
    
    commits = conn.execute(
        "SELECT * FROM git_commits WHERE session_id = ? ORDER BY timestamp", (session['id'],)
    ).fetchall()
    
    duration = format_duration(session['started_at'], session['ended_at'] or time.time())
    
    print("=" * 60)
    print(f"  AgentLog Session Summary")
    print(f"  Session: {session['id']}")
    print(f"  Tool:    {session['tool']}")
    print(f"  Project: {session['project'] or '(none)'}")
    print(f"  When:    {format_timestamp(session['started_at'])}")
    print(f"  Duration:{duration}")
    print("=" * 60)
    print()
    
    if commits:
        print("── Git History ──")
        for c in commits:
            h = c['hash'][:8] if c['hash'] else "?"
            print(f"  [{h}] {c['branch'] + ': ' if c['branch'] else ''}{c['message']}")
        print()
    
    if files:
        print("── Files Changed ──")
        for f in files:
            print(f"  {f['operation'].upper():8} {f['file_path']}")
        print()
    
    if actions:
        print("── Action Log ──")
        for a in actions:
            ts = format_timestamp(a['timestamp'])
            print(f"  [{a['action_type'].upper():7}] {a['description'][:120]}")
        print()
    
    print("=" * 60)
    print(f"  Session: {session['id']}")
    print(f"  Run: agentlog search '...'  to dive deeper")
    print("=" * 60)


def detect_tool():
    """Detect which AI tool is likely running."""
    # Check environment variables and processes
    if os.environ.get('CLAUDE_CODE'):
        return "claude-code"
    if os.environ.get('OPENCODE_ROOT'):
        return "opencode"
    if os.environ.get('CURSOR_TRACE'):
        return "cursor"
    
    # Check for Hermes
    if os.environ.get('HERMES_HOME'):
        return "hermes"
    
    return "unknown"


def detect_project():
    """Detect current project from working directory."""
    cwd = os.getcwd()
    # Check for git root
    try:
        result = os.popen("git rev-parse --show-toplevel 2>/dev/null").read().strip()
        if result:
            return os.path.basename(result)
    except:
        pass
    return os.path.basename(cwd)


def main():
    parser = argparse.ArgumentParser(
        description="AgentLog — Cross-platform AI Agent Action Tracker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  agentlog init                    Start a new session
  agentlog track file app.py       Log a file change
  agentlog track command 'npm test' Log a command
  agentlog track note 'Found bug'  Add a note
  agentlog track git 'Fix login' --hash abc123  Log a commit
  agentlog status                  Check current session
  agentlog search 'auth error'     Search history
  agentlog summary                 Generate handoff document
  agentlog sessions                List recent sessions
        """
    )
    
    subparsers = parser.add_subparsers(dest="command")
    
    # init
    p_init = subparsers.add_parser("init", help="Start a new tracking session")
    p_init.add_argument("--tool", "-t", help="AI tool name (auto-detected if omitted)")
    p_init.add_argument("--project", "-p", help="Project name (auto-detected if omitted)")
    
    # track
    p_track = subparsers.add_parser("track", help="Record an action")
    p_track.add_argument("action_type", help="Type: file, command, note, api, git")
    p_track.add_argument("data", help="Action description or path")
    p_track.add_argument("--diff", "-d", help="Diff summary (for file actions)")
    p_track.add_argument("--details", help="Extra details (for api actions)")
    p_track.add_argument("--hash", help="Git commit hash (for git actions)")
    p_track.add_argument("--branch", "-b", help="Git branch (for git actions)")
    p_track.add_argument("--operation", "-o", help="File operation: created/modified/deleted")
    
    # status
    subparsers.add_parser("status", help="Show current session status")
    
    # search
    p_search = subparsers.add_parser("search", help="Search across sessions")
    p_search.add_argument("query", help="Search term")
    
    # sessions
    p_sessions = subparsers.add_parser("sessions", help="List sessions")
    p_sessions.add_argument("--limit", "-l", type=int, default=20, help="Max sessions to show")
    
    # summary
    p_summary = subparsers.add_parser("summary", help="Generate session summary")
    p_summary.add_argument("session_id", nargs="?", help="Session ID (defaults to active)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    conn = get_db()
    
    commands = {
        "init": cmd_init,
        "track": cmd_track,
        "status": cmd_status,
        "search": cmd_search,
        "sessions": cmd_sessions,
        "summary": cmd_summary,
    }
    
    try:
        result = commands[args.command](args, conn)
        conn.close()
        sys.exit(result or 0)
    except KeyboardInterrupt:
        print("\nInterrupted.")
        conn.close()
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        conn.close()
        sys.exit(1)


if __name__ == "__main__":
    main()
