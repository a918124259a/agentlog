#!/usr/bin/env python3
"""
AgentLog Shell Integration — Auto-log terminal commands and file changes.

Usage:
    source <(agentlog-hook bash)   # Activate in current shell
    # Now every command is auto-logged
    agentlog-hook zsh              # For zsh
"""

import argparse
import sys
import os


HOOKS = {
    "bash": """
# AgentLog Shell Hook — auto-log commands
# Source this file:  source <(agentlog-hook bash)

_agentlog_preexec() {
    # Don't log AgentLog's own commands
    local cmd="$1"
    case "$cmd" in
        agentlog*|agentlog-hook*) return ;;
    esac
    
    # Check if there's an active session
    if agentlog status &>/dev/null; then
        agentlog track command "$cmd"
    fi
}

_agentlog_precmd() {
    # Show session status every 20 commands
    local count_file="/tmp/agentlog_cmd_count"
    local count=0
    if [[ -f "$count_file" ]]; then
        count=$(cat "$count_file")
    fi
    count=$((count + 1))
    echo "$count" > "$count_file"
    
    if [[ $count -ge 20 ]]; then
        echo "0" > "$count_file"
        agentlog status
    fi
}

# Install hooks
if [[ "$(type -t preexec)" != "function" ]]; then
    preexec() { _agentlog_preexec "$_"; }
else
    _agentlog_old_preexec=$(declare -f preexec)
    preexec() { _agentlog_preexec "$_"; eval "$_agentlog_old_preexec"; }
fi

if [[ "$(type -t precmd)" != "function" ]]; then
    precmd() { _agentlog_precmd; }
else
    _agentlog_old_precmd=$(declare -f precmd)
    precmd() { _agentlog_precmd; eval "$_agentlog_old_precmd"; }
fi

echo "🔌 AgentLog shell hook active — commands will be auto-logged"
""",
    
    "zsh": """
# AgentLog Shell Hook for Zsh — auto-log commands
# Add to ~/.zshrc:  source <(agentlog-hook zsh)

_agentlog_preexec() {
    local cmd="$1"
    case "$cmd" in
        agentlog*|agentlog-hook*) return ;;
    esac
    
    if agentlog status &>/dev/null; then
        agentlog track command "$cmd"
    fi
}

_agentlog_precmd() {
    local count_file="/tmp/agentlog_cmd_count"
    local count=0
    [[ -f "$count_file" ]] && count=$(<"$count_file")
    count=$((count + 1))
    echo "$count" > "$count_file"
    
    if (( count >= 20 )); then
        echo "0" > "$count_file"
        agentlog status | head -8
    fi
}

autoload -Uz add-zsh-hook
add-zsh-hook preexec _agentlog_preexec
add-zsh-hook precmd _agentlog_precmd

echo "🔌 AgentLog shell hook active — commands will be auto-logged"
""",

    "fish": """
# AgentLog Shell Hook for Fish — auto-log commands
# Add to ~/.config/fish/config.fish:  agentlog-hook fish | source

function _agentlog_preexec --on-event fish_preexec
    set cmd $argv[1]
    switch $cmd
        case 'agentlog*' 'agentlog-hook*'
            return
    end
    
    if agentlog status &>/dev/null
        agentlog track command $cmd
    end
end

echo "🔌 AgentLog shell hook active — commands will be auto-logged"
"""
}


def main():
    parser = argparse.ArgumentParser(description="AgentLog shell integration hooks")
    parser.add_argument("shell", nargs="?", choices=["bash", "zsh", "fish"], 
                        default="bash", help="Shell type")
    
    args = parser.parse_args()
    
    hook = HOOKS.get(args.shell)
    if hook:
        print(hook.strip())
    else:
        print(f"Unsupported shell: {args.shell}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
