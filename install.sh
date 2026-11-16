#!/bin/bash
set -euo pipefail
repo=$(cd -- "$(dirname -- "$0")" && pwd -P)
exec python3 "$repo/scripts/install-skills.py" "$@"
