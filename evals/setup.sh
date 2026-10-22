#!/bin/bash
# setup.sh <skill> [dest]: copy a fixture into a fresh git repo and print the Workflow call to run against it.
set -euo pipefail
skill=${1:?usage: setup.sh <skill> [dest]}
here=$(cd "$(dirname "$0")" && pwd)
src="$here/$skill/fixture"
[ -d "$src" ] || { echo "no fixture for $skill" >&2; exit 2; }
dest=${2:-$(mktemp -d "${TMPDIR:-/tmp}/eval-$skill.XXXXXX")}
cp -R "$src/." "$dest/"
git -C "$dest" init -q
git -C "$dest" add -A
git -C "$dest" -c user.email=eval@example.invalid -c user.name=eval commit -qm fixture
# Fixtures that pin their toolchain ship a lockfile; install it from the local Bun cache, never the network. A fixture
# with a package.json but no lockfile is read, not built, so there is nothing to install.
if [ -f "$dest/package.json" ] && [ -f "$dest/bun.lock" ]; then (cd "$dest" && bun install --offline --frozen-lockfile >/dev/null) || { echo "offline install failed" >&2; exit 3; }; fi
script=$(ls "$here/../$skill/workflows/"*.js)
extra='mode: "<audit|campaign|explore>"'
if [ "$skill" = ux-laws ]; then
  extra='mode: "audit", measure: false'
fi
if [ "$skill" = persona-test ]; then
  extra="target: \"http://127.0.0.1:8765/\", platforms: [\"web\"], max_personas: 3, tasks: $(python3 -c 'import json,sys; print(json.dumps(json.load(open(sys.argv[1]))["tasks"]))' "$here/$skill/expected.json")"
fi
cat <<EOF
Fixture ready: $dest
From any Claude Code session, run this first without and then with confirmed: true:

  Workflow({ scriptPath: "$script",
             args: { skill_dir: "$(cd "$here/../$skill" && pwd)", root: "$dest", $extra } })

Save the confirmed result to result.json, then score it:

  python3 $here/score.py $skill result.json            # add --tree $dest for apply runs
EOF
