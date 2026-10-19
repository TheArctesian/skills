#!/bin/bash
# install.sh [--remove]: symlink every skill in this checkout into ~/.claude/skills and the persona-test agents into
# ~/.claude/agents, so edits here are live in Claude Code. Start a new session afterwards.
set -euo pipefail
repo=$(cd "$(dirname "$0")" && pwd)
dest="$HOME/.claude/skills"
mkdir -p "$dest"
for skill in "$repo"/*/SKILL.md; do
  dir=$(dirname "$skill"); name=$(basename "$dir"); link="$dest/$name"
  if [ "${1:-}" = "--remove" ]; then
    [ -L "$link" ] && rm "$link" && echo "removed $link"
  elif [ -e "$link" ] && [ ! -L "$link" ]; then
    echo "skip $link: a real directory is there" >&2
  else
    ln -sfn "$dir" "$link" && echo "linked $link"
  fi
done
"$repo/persona-test/scripts/install-agents.sh" ${1:-}
if [ "${1:-}" != "--remove" ] && ! grep -qF "\"$repo\"" "$HOME/.claude/settings.json" 2>/dev/null; then
  cat <<MSG

Workflow scripts load only from directories the session can read. Add this checkout once, in
~/.claude/settings.json (or run /permissions → Additional directories):

  "permissions": { "additionalDirectories": ["$repo"] }
MSG
fi
