#!/usr/bin/env bash
# worktree-audit.sh ROOT...: read-only audit of every linked git worktree of every repo under ROOTs,
# plus orphaned worktree folders in the usual agent locations.
# TSV: repo  path  branch  dirty  unpushed  last_commit  active  state
#   state: ok | locked | moved (repo or worktree moved; audited through the stale record, fix with
#          `git worktree repair`) | missing (registered, folder gone) | error | orphan (no repo knows it)
#   active: yes when the last commit or any working file (outside .git and build output) is under $ACTIVE_DAYS old
# Each worktree is read through its repo's own .git/worktrees/<name> admin dir, so a stale .git file
# (repo renamed or moved) cannot make a worktree look clean.
set -uo pipefail
ACTIVE_DAYS=${ACTIVE_DAYS:-2}
AGENT_ROOTS=("$HOME/.codex/worktrees" "$HOME/.claude/worktrees" "$HOME/Documents/Codex" "$HOME/.cursor/worktrees" "$HOME/conductor/workspaces")
cutoff=$(date -v-"${ACTIVE_DAYS}"d +%Y-%m-%d)

is_active() { # worktree path, last commit date
  [[ "$2" > "$cutoff" || "$2" == "$cutoff" ]] && { echo yes; return; }
  local hit
  hit=$(find "$1" \( -name .git -o -name node_modules -o -name target -o -name .build -o -name DerivedData \) -prune \
        -o -type f -mtime -"${ACTIVE_DAYS}" -print -quit 2>/dev/null)
  [ -n "$hit" ] && echo yes || echo no
}

audit() { # repo admin_dir worktree_path state_if_ok
  local repo=$1 adm=$2 p=$3 st=$4 s d u l b
  if [ ! -d "$p" ]; then printf '%s\t%s\t-\t-\t-\t-\t-\tmissing\n' "$repo" "$p"; return; fi
  local G=(git --git-dir="$adm" --work-tree="$p")
  if ! "${G[@]}" rev-parse -q --verify HEAD >/dev/null 2>&1 || ! s=$("${G[@]}" status --porcelain 2>/dev/null); then
    printf '%s\t%s\t-\tERR\tERR\t-\t-\terror\n' "$repo" "$p"; return
  fi
  d=$(printf '%s' "$s" | grep -c .)
  u=$("${G[@]}" rev-list HEAD --not --remotes 2>/dev/null | wc -l | tr -d ' ')
  l=$("${G[@]}" log -1 --format=%cs)
  b=$("${G[@]}" rev-parse --abbrev-ref HEAD)
  [ -f "$adm/locked" ] && st=locked
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$repo" "$p" "$b" "$d" "$u" "$l" "$(is_active "$p" "$l")" "$st"
}

repos=$(for r in "$@"; do find "$r" -maxdepth 5 -name .git -type d -not -path '*/node_modules/*' -not -path '*/.claude/*' -not -path '*/worktrees/*' 2>/dev/null; done | xargs -n1 dirname 2>/dev/null | sort -u)
seen=$(mktemp); lost=$(mktemp); claimed=$(mktemp); trap 'rm -f "$seen" "$lost" "$claimed"' EXIT

while IFS= read -r repo; do
  [ -n "$repo" ] || continue
  common=$(git -C "$repo" rev-parse --git-common-dir 2>/dev/null) || continue
  case $common in /*) ;; *) common="$repo/$common";; esac
  for adm in "$common"/worktrees/*/; do
    adm=${adm%/}; [ -f "$adm/gitdir" ] || continue
    p=$(dirname "$(cat "$adm/gitdir")")
    echo "$p" >> "$seen"
    if [ -d "$p" ]; then audit "$repo" "$adm" "$p" ok
    else printf '%s\t%s\t%s\t%s\n' "$(basename "$adm")" "$repo" "$adm" "$(basename "$p")" >> "$lost"; fi
  done
done <<< "$repos"

# Orphans: a folder with a .git *file* that no repo above registers. If a repo holds a record of the
# same name whose folder is missing, the repo or worktree moved: audit through that record ("moved").
# Otherwise the record is gone (renamed and pruned): git cannot audit it, only its build output is safe.
orphan_dirs() {
  for r in "${AGENT_ROOTS[@]}"; do [ -d "$r" ] && find "$r" -maxdepth 4 -name .git -type f 2>/dev/null; done
  for r in "$@"; do find "$r" -maxdepth 7 -path '*/.claude/worktrees/*/.git' -type f 2>/dev/null; done
}
orphan_dirs "$@" | sort -u | while IFS= read -r f; do
  p=$(dirname "$f")
  grep -qxF "$p" "$seen" && continue
  name=$(basename "$(sed -n 's/^gitdir: //p' "$f")")
  # pair only on a unique match of both the record name and the worktree folder name
  match=$(awk -F'\t' -v n="$name" -v b="$(basename "$p")" '$1==n && $4==b' "$lost")
  if [ -n "$match" ] && [ "$(printf '%s\n' "$match" | wc -l)" -eq 1 ]; then
    IFS=$'\t' read -r _ repo adm _ <<< "$match"; echo "$adm" >> "$claimed"
    audit "$repo" "$adm" "$p" moved
  else printf -- '-\t%s\t-\t?\t?\t-\t-\torphan\n' "$p"; fi
done
# Records whose folder is gone and that no orphan claimed: `git worktree prune` clears them.
while IFS=$'\t' read -r _ repo adm _; do
  grep -qxF "$adm" "$claimed" || printf '%s\t%s\t-\t-\t-\t-\t-\tmissing\n' "$repo" "$(dirname "$(cat "$adm/gitdir")")"
done < "$lost"
