#!/usr/bin/env bash
# scan.sh [ROOT...]: read-only disk report for a macOS developer machine.
# ROOTs are folders holding repositories (default: whichever of ~/Scripts ~/Projects ~/code ~/src
# ~/dev ~/Developer exist). Prints a report and writes TSVs (KB<TAB>path) to $OUT (default: a temp dir).
set -uo pipefail
here=$(cd "$(dirname "$0")" && pwd)
OUT=${OUT:-$(mktemp -d "${TMPDIR:-/tmp}/macos-cleanup.XXXXXX")}
P=${P:-12}
if [ $# -gt 0 ]; then roots=("$@"); else
  roots=(); for d in ~/Scripts ~/Projects ~/code ~/src ~/dev ~/Developer; do [ -d "$d" ] && roots+=("$d"); done
fi

gb() { awk -F'\t' '{printf "%7.1f GB  %s\n", $1/1048576, $2}'; }
# xargs -n1 rather than -I{}: BSD xargs -I caps the replaced argument at 255 bytes
sizes() { tr '\n' '\0' | xargs -0 -P "$P" -n1 sh -c 'printf "%s\t%s\n" "$(du -sk "$1" 2>/dev/null | cut -f1)" "$1"' _ | awk -F'\t' '$1!=""' | sort -rn; }
section() { printf '\n== %s\n' "$1"; }

section "Free space"
df -h /System/Volumes/Data 2>/dev/null | tail -1 || df -h / | tail -1
diskutil apfs list 2>/dev/null | awk -F': *' '/Name:/{n=$2; sub(/ \(Case-.*/,"",n)} /Capacity Consumed/{if (match($2,/\([^)]*\)/)) print "   " substr($2,RSTART+1,RLENGTH-2) "  " n}' | grep -v ' KB ' || true
snaps=$(tmutil listlocalsnapshots / 2>/dev/null | grep -c com.apple || true)
echo "   Time Machine local snapshots: ${snaps:-0}"

section "Home (top 20)"
ls -A ~ | grep -vx Library | sed "s|^|$HOME/|" | sizes > "$OUT/home.tsv"; head -20 "$OUT/home.tsv" | gb

section "~/Library (top 25, two levels)"
ls -d ~/Library/* ~/Library/Containers/* ~/Library/Group\ Containers/* ~/Library/Application\ Support/* \
  ~/Library/Caches/* ~/Library/Developer/* ~/Library/Developer/Xcode/* 2>/dev/null | sizes > "$OUT/library.tsv"
head -25 "$OUT/library.tsv" | gb

section "Catalogued locations over 0.5 GB (class and cleanup in references/targets.md)"
grep -oE '^\| `~/[^`]+`' "$here/../references/targets.md" | sed -E 's/^\| `~(.*)`/\1/' | sed "s|^|$HOME|" |
  while IFS= read -r p; do [ -e "$p" ] && echo "$p"; done | sizes | awk -F'\t' '$1>524288' > "$OUT/caches.tsv"
gb < "$OUT/caches.tsv"

section "Docker"
if docker info >/dev/null 2>&1; then
  docker system df
  echo "   volumes with 0 links (largest first):"
  docker system df -v 2>/dev/null | awk '/^Local Volumes/{f=1;getline;next} /^Build cache/{f=0} f&&NF>=3&&$2=="0"{print "     " $3 "  " $1}' | sort -rh | head -10
  docker ps -a --filter status=exited --filter status=created --format '   stopped: {{.Size}}  {{.Names}}  ({{.Status}})' | head -10
else echo "   docker not running (start it to size images/volumes; Docker.raw is in the Library list)"; fi

section "iOS simulators"
if command -v xcrun >/dev/null; then
  xcrun simctl list devices -j 2>/dev/null | python3 -I -c '
import json,sys,os
d=json.load(sys.stdin)["devices"]; base=os.path.expanduser("~/Library/Developer/CoreSimulator/Devices/")
stock=("iPhone","iPad","Apple Watch","Apple TV","Apple Vision")
c={"stock":0,"custom":0,"unavailable":0}
for r,v in d.items():
  for x in v:
    c["unavailable" if not x.get("isAvailable",True) else "stock" if x["name"].startswith(stock) else "custom"]+=1
print("   devices: %(stock)d stock, %(custom)d custom-named (usually agent-created), %(unavailable)d unavailable" % c)' 2>/dev/null
  xcrun simctl runtime list 2>/dev/null | grep -E '^(iOS|watchOS|tvOS|visionOS|Total)' | sed 's/^/   /'
fi

section "Worktree roots"
{ for r in "${roots[@]}"; do find "$r" -maxdepth 6 -type d -path '*/.claude/worktrees' -prune -not -path '*/node_modules/*' 2>/dev/null; done
  for d in ~/.codex/worktrees ~/.claude/worktrees ~/Documents/Codex ~/.cursor/worktrees ~/conductor/workspaces; do [ -d "$d" ] && echo "$d"; done
} | sizes > "$OUT/worktree-roots.tsv"
while IFS=$'\t' read -r kb p; do printf '%7.1f GB  %s  (%s entries)\n' "$(echo "$kb/1048576" | bc -l)" "$p" "$(ls "$p" | wc -l | tr -d ' ')"; done < "$OUT/worktree-roots.tsv"

section "Build artifacts under roots + worktree roots (by kind)"
scan_roots=("${roots[@]}")
while IFS=$'\t' read -r _ p; do
  inside=no; for r in "${roots[@]}"; do case "$p/" in "$r"/*) inside=yes;; esac; done
  [ $inside = no ] && scan_roots+=("$p")
done < "$OUT/worktree-roots.tsv"
bash "$here/artifacts.sh" list "${scan_roots[@]}" > "$OUT/artifacts.tsv" 2>/dev/null
awk -F'\t' '{t[$2]+=$1; n[$2]++} END{for(k in t) printf "%7.1f GB  %-14s %d dirs\n", t[k]/1048576, k, n[k]}' "$OUT/artifacts.tsv" | sort -rn
echo "   full list: $OUT/artifacts.tsv"

section "Downloads, Desktop: items over 500 MB"
find ~/Downloads ~/Desktop -mindepth 1 -maxdepth 1 2>/dev/null | sizes | awk -F'\t' '$1>512000' > "$OUT/downloads.tsv"; head -25 "$OUT/downloads.tsv" | gb
echo "   installers: $(find ~/Downloads -maxdepth 2 \( -iname '*.dmg' -o -iname '*.pkg' -o -iname '*.xip' \) 2>/dev/null | wc -l | tr -d ' ') .dmg/.pkg/.xip files"

section "Large single files over 4 GB (home, excluding Library and artifacts)"
find ~ -path ~/Library -prune -o \( -name node_modules -o -name target -o -name .git \) -prune -o -type f -size +4G -print 2>/dev/null |
  sizes | head -15 | gb

printf '\nTSVs: %s\n' "$OUT"
