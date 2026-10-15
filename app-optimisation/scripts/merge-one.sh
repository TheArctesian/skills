#!/bin/bash
# merge-one.sh <pr> [deploy-workflow]
# Refuse unless every check on the PR's head finished without failure, wait out any
# deploy already running on main, squash-merge, then wait for the merge's deploy run.
# Exit codes: 0 deployed, 2 not ready, 3 merge failed, 4 no deploy run found, 1 deploy failed.
set -u
pr=$1
workflow=${2:-deploy.yml}

# wait_run <id>: poll until completed, tolerating network blips; prints the conclusion.
wait_run() {
  while :; do
    st=$(gh run view "$1" --json status,conclusion --jq '"\(.status) \(.conclusion)"' 2>/dev/null) || { sleep 30; continue; }
    case $st in completed*) echo "${st#completed }"; return ;; esac
    sleep 60
  done
}

rollup=$(gh pr view "$pr" --json statusCheckRollup) || { echo "PR $pr: cannot read checks"; exit 2; }
pending=$(jq '[.statusCheckRollup[] | select((.status // "COMPLETED") != "COMPLETED")] | length' <<<"$rollup")
failed=$(jq '[.statusCheckRollup[] | select(.conclusion=="FAILURE" or .conclusion=="CANCELLED" or .conclusion=="TIMED_OUT" or .conclusion=="ACTION_REQUIRED" or .state=="FAILURE" or .state=="ERROR")] | length' <<<"$rollup")
if [ "$pending" != 0 ] || [ "$failed" != 0 ]; then
  echo "PR $pr NOT READY: pending=$pending failed=$failed"; exit 2
fi
[ "$(gh pr view "$pr" --json mergeable --jq .mergeable)" = CONFLICTING ] && { echo "PR $pr NOT READY: conflicts"; exit 2; }

while :; do
  ids=$(gh run list --branch main --workflow "$workflow" --limit 10 --json databaseId,status \
    --jq '.[] | select(.status!="completed") | .databaseId' 2>/dev/null) || { sleep 30; continue; }
  [ -z "$ids" ] && break
  for id in $ids; do echo "prior deploy $id: $(wait_run "$id")"; done
done

if [ "$(gh pr view "$pr" --json state --jq .state)" = MERGED ]; then
  echo "PR $pr was already merged"
else
  gh pr merge "$pr" --squash || { echo "PR $pr merge failed"; exit 3; }
fi
sha=$(gh pr view "$pr" --json mergeCommit --jq .mergeCommit.oid)
echo "PR $pr merged as $sha"

run=
for _ in $(seq 1 60); do
  run=$(gh run list --branch main --workflow "$workflow" --commit "$sha" --json databaseId --jq '.[0].databaseId // empty' 2>/dev/null)
  [ -n "$run" ] && break
  sleep 10
done
[ -z "$run" ] && { echo "no deploy run found for $sha"; exit 4; }
c=$(wait_run "$run")
echo "deploy run $run for PR $pr: $c"
[ "$c" = success ]
