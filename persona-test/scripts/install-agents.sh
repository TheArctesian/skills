#!/bin/bash
# install-agents.sh [--remove]: symlink the persona agents into ~/.claude/agents.
# Plugin agents ignore mcpServers, so each persona's private browser or device server only works from a user agent file.
set -euo pipefail
src=$(cd "$(dirname "$0")/../agents" && pwd)
dest="$HOME/.claude/agents"
mkdir -p "$dest"
for f in "$src"/persona-*.md; do
  link="$dest/$(basename "$f")"
  if [ "${1:-}" = "--remove" ]; then
    [ -L "$link" ] && rm "$link" && echo "removed $link"
  elif [ -e "$link" ] && [ ! -L "$link" ]; then
    echo "skip $link: a real file is there" >&2
  else
    ln -sfn "$f" "$link" && echo "linked $link"
  fi
done
[ "${1:-}" = "--remove" ] || echo "Start a new Claude Code session so the agents are registered."
