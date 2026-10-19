#!/bin/bash
# device-pool.sh: iOS simulators for one persona-test run, named persona-test-<tag>-<n> so leftovers can be swept.
#   up <tag> <count> [device type]   create and boot simulators, print one UDID per line
#   prep <udid> <app> <bundle id> [text size] [appearance] [locale]   clean install and apply settings
#   down <tag>                       shut down and delete this run's simulators
#   sweep                            delete every persona-test-* simulator
set -euo pipefail
ours() { xcrun simctl list devices -j | python3 -c "import json,sys; p=sys.argv[1]; [print(d['udid']) for r in json.load(sys.stdin)['devices'].values() for d in r if d['name'].startswith(p)]" "$1"; }
case "${1:-}" in
  up)
    tag=${2:?tag}; n=${3:?count}; type=${4:-iPhone 17}
    for i in $(seq 1 "$n"); do
      udid=$(xcrun simctl create "persona-test-$tag-$i" "$type")
      xcrun simctl boot "$udid"
      echo "$udid"
    done
    for udid in $(ours "persona-test-$tag-"); do xcrun simctl bootstatus "$udid" -b >/dev/null; done ;;
  prep)
    udid=${2:?udid}; app=${3:?app path}; bundle=${4:?bundle id}; size=${5:-large}; look=${6:-light}; locale=${7:-}
    xcrun simctl terminate "$udid" "$bundle" 2>/dev/null || true
    xcrun simctl uninstall "$udid" "$bundle" 2>/dev/null || true
    xcrun simctl install "$udid" "$app"
    xcrun simctl ui "$udid" content_size "$size"
    xcrun simctl ui "$udid" appearance "$look"
    if [ -n "$locale" ]; then
      xcrun simctl spawn "$udid" defaults write -g AppleLanguages -array "${locale%%_*}"
      xcrun simctl spawn "$udid" defaults write -g AppleLocale "$locale"
    fi ;;
  down)
    tag=${2:?tag}
    for udid in $(ours "persona-test-$tag-"); do xcrun simctl shutdown "$udid" 2>/dev/null || true; xcrun simctl delete "$udid"; echo "deleted $udid"; done ;;
  sweep)
    for udid in $(ours "persona-test-"); do xcrun simctl shutdown "$udid" 2>/dev/null || true; xcrun simctl delete "$udid"; echo "deleted $udid"; done ;;
  *) sed -n '2,7p' "$0" >&2; exit 2 ;;
esac
