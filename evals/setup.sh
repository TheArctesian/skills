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
script=$(ls "$here/../$skill/workflows/"*.js)
cat <<EOF
Fixture ready: $dest
From any Claude Code session, run this first without and then with confirmed: true:

  Workflow({ scriptPath: "$script",
             args: { skill_dir: "$(cd "$here/../$skill" && pwd)", root: "$dest", mode: "<audit|campaign|explore>" } })

Save the confirmed result to result.json, then score it:

  python3 $here/score.py $skill result.json            # add --tree $dest for apply runs
EOF
