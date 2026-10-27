#!/usr/bin/env bash
# worktree-remove.sh < audit.tsv: remove the worktrees in worktree-audit.sh output that are safe:
# state=ok or moved (repaired first), dirty=0, unpushed=0, active=no. Everything else is skipped. Each one is re-audited
# immediately before removal, and removed with plain `git worktree remove` (never --force), so git
# itself refuses anything dirty, untracked or locked. Prints one line per row: REMOVED | SKIP-* | FAILED.
set -uo pipefail
while IFS=$'\t' read -r repo p _branch dirty unpushed _last active state; do
  why=
  case $state in ok|moved) ;; *) why=$state ;; esac
  [ -z "$why" ] && [ "$dirty" != 0 ] && why=dirty
  [ -z "$why" ] && [ "$unpushed" != 0 ] && why=unpushed
  [ -z "$why" ] && [ "$active" != no ] && why=active
  if [ -n "$why" ]; then
    # a kept worktree of a moved repo must be repaired, or `git worktree prune` deletes its record
    [ "$state" = moved ] && [ -d "$p" ] && git -C "$repo" worktree repair "$p" >/dev/null 2>&1 && why="$why (repaired)"
    echo "SKIP-$why	$p"; continue
  fi
  [ -d "$p" ] || { echo "SKIP-missing	$p"; continue; }
  [ "$state" = moved ] && git -C "$repo" worktree repair "$p" >/dev/null 2>&1
  s=$(git -C "$p" status --porcelain 2>/dev/null) || { echo "SKIP-unreadable	$p"; continue; }
  [ -z "$s" ] || { echo "SKIP-dirty-now	$p"; continue; }
  [ "$(git -C "$p" rev-list HEAD --not --remotes 2>/dev/null | wc -l | tr -d ' ')" = 0 ] || { echo "SKIP-unpushed-now	$p"; continue; }
  if out=$(git -C "$repo" worktree remove "$p" 2>&1); then echo "REMOVED	$p"; else echo "FAILED	$p	$out"; fi
done
