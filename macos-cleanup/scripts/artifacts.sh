#!/usr/bin/env bash
# artifacts.sh list ROOT...      -> TSV: KB  kind  path   for build output a manifest proves is regenerable
# artifacts.sh delete FILE.tsv   -> deletes each listed path after re-checking its kind and manifest
# A directory counts only beside the manifest that generates it (kondo's rule), so a source folder
# that happens to be called "target" or "build" is never listed.
set -uo pipefail
P=${P:-12}

kind_of() { # path -> kind, or nothing when the manifest check fails
  local d=$1 parent; parent=$(dirname "$d")
  case $(basename "$d") in
    target)       [ -f "$parent/Cargo.toml" ] && echo cargo-target ;;
    node_modules) [ -f "$parent/package.json" ] && echo node_modules ;;
    .build)       [ -f "$parent/Package.swift" ] && echo swift-build ;;
    DerivedData)  echo xcode-derived ;;
    .next)        [ -f "$parent/package.json" ] && echo next ;;
    .turbo)       echo turbo ;;
    .parcel-cache) echo parcel ;;
    .svelte-kit)  [ -f "$parent/package.json" ] && echo svelte-kit ;;
    .gradle)      ls "$parent"/build.gradle* "$parent"/settings.gradle* >/dev/null 2>&1 && echo gradle ;;
    .dart_tool)   [ -f "$parent/pubspec.yaml" ] && echo dart-tool ;;
    zig-cache|.zig-cache) [ -f "$parent/build.zig" ] && echo zig-cache ;;
  esac
}

case ${1:-} in
  list)
    shift
    for root in "$@"; do
      find "$root" -type d \( -name .git -o -name Library \) -prune -o -type d \( -name target -o -name node_modules \
        -o -name .build -o -name DerivedData -o -name .next -o -name .turbo -o -name .parcel-cache -o -name .svelte-kit \
        -o -name .gradle -o -name .dart_tool -o -name zig-cache -o -name .zig-cache \) -print -prune 2>/dev/null
    done | while IFS= read -r d; do k=$(kind_of "$d"); [ -n "$k" ] && printf '%s\t%s\n' "$k" "$d"; done |
      tr '\n' '\0' | xargs -0 -P "$P" -n1 sh -c 'k=${1%%	*}; p=${1#*	}; printf "%s\t%s\t%s\n" "$(du -sk "$p" 2>/dev/null | cut -f1)" "$k" "$p"' _ |
      sort -rn ;;
  delete)
    [ -f "${2:-}" ] || { echo "usage: $0 delete FILE.tsv" >&2; exit 2; }
    freed=0; n=0
    while IFS=$'\t' read -r kb kind p; do
      [ -d "$p" ] || continue
      case $p in /*/*) ;; *) echo "REFUSED $p (not an absolute nested path)" >&2; continue;; esac
      now=$(kind_of "$p")
      [ "$now" = "$kind" ] || { echo "REFUSED $p (kind now '${now:-none}', listed '$kind')" >&2; continue; }
      rm -rf -- "$p" && { freed=$((freed + kb)); n=$((n + 1)); }
    done < "$2"
    printf 'deleted %d dirs, ~%.1f GB\n' "$n" "$(echo "$freed/1048576" | bc -l)" ;;
  *) echo "usage: $0 list ROOT... | delete FILE.tsv" >&2; exit 2 ;;
esac
