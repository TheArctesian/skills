---
name: app-optimisation
description: Measured performance programme for a whole application, split into domain lanes (infrastructure, API/backend, native or web clients) detected from the repository. A multi-agent workflow sweeps each lane from four angles, adversarially verifies every suspected gap, writes one self-contained lane prompt per domain to run in parallel sessions, enforces benchmark-before-and-after for every fix, and lands the resulting PRs one at a time behind deploy checks. Use when asked to make an app faster, improve startup, screen-open, content-load or scrolling performance, find where the real performance gap is, or turn a generic "make it faster" prompt into domain-specific work.
---

# App optimisation

A fix that was not measured before and after is a guess. This skill turns "make the
app faster" into a few domain lanes. Each lane builds a harness to find its own
bottleneck, proves every change with numbers and ships focused PRs.

## 1. Configuration

Fill what you know; empty fields are discovered by the workflow. Everything below reads from it.

```yaml
lanes:            []                    # empty = detect; else e.g. [infra, api, web, ios]
owners:           {}                    # path → lane; empty = detect. A lane edits only what it owns
synthetic_data:   ""                    # seed script or fixture for a heavy test user; empty = detect
gates:            []                    # commands every PR must pass; empty = detect from AGENTS.md / CI
votes:            3                     # verifiers per suspected gap, each a different check
deploy_on_merge:  true                  # does a merge to main roll production?
production_needs_approval: true         # cloud writes, manual index builds, scaling: always separate asks
```

## 2. Explore, verify, write prompts (workflow)

Invoking this skill is the opt-in. Run `workflows/lanes.js` from this skill's directory:

```
Workflow({
  scriptPath: "<this skill's base directory>/workflows/lanes.js",
  args: { skill_dir: "<this skill's base directory>", lanes: [...] /* optional */, votes: 3 }
})
```

### Estimate, confirm, run, save

Every launch is two calls. The first returns `stage: "estimate"` after only the cheap
discovery phases: components, shard counts, the expected number of agents, and every
command the run will execute, with `suspicious_commands` flagged. Show the person that
estimate and the commands, and ask before continuing; a suspicious command is removed or
approved explicitly. Then relaunch with the same `scriptPath` and args plus
`confirmed: true`, passing `resumeFromRunId` from the first call so discovery comes from
cache. If the person set a token target ("+2M"), the workflow stops starting new work
near it and lists what it skipped.

As soon as a run returns, write the returned object to
`<scratchpad>/<skill>-<runId>.json` before doing anything else, so a lost session does not
lose the report while the edits stay in the tree.


Leave `lanes` empty and the Profile phase detects them from the repository (manifests,
Dockerfiles, IaC, CI, deploy workflows), with non-overlapping owned paths, run commands,
gates, synthetic-data seeding and cross-lane contracts.

| Phase | Agents | Work |
|---|---|---|
| Profile | 1 | Lanes, owners, build/run, gates, deploy model, cross-lane contracts. |
| Sweep | 4 per lane | Separate angles, blind to each other: startup path; hot screens/endpoints (pagination order, caching, N+1, unbounded reads, "older content loads slowly"); existing perf tooling and how to run locally; the lane's checklist in [references/lanes.md](references/lanes.md). |
| Rank | 1 per lane | Merges the sweeps into the top 8 gaps by user-noticeable impact, the metric each moves, the harness the lane needs, handoffs. |
| Verify | `votes` per gap | Each verifier runs a different check: does the cited code really do this (evidence), is it on a user-noticeable path (hot), is it already absorbed by a cache, index or job (mitigated)? Explore agents sometimes report something that isn't so. Confirmed gaps become candidates, uncertain ones go under "measure before believing", refuted ones are listed and dropped. |
| Prompt | 1 per lane | Fills [references/lane-prompt.md](references/lane-prompt.md) with confirmed gaps only, so it stands alone. |

## 3. Hand the prompts over

Every prompt must hold up for a reader who has not seen this conversation:

- Name the files and the evidence from exploration, framed as candidates the lane must
  confirm with numbers, not as conclusions.
- **Harness first.** Build a reproducible benchmark and a heavy synthetic dataset
  before changing anything. Run against the production-like engine (Postgres, not
  SQLite; a release build, not debug).
- One fix at a time, measured in isolation. Record a table: metric, baseline, after,
  kept or reverted, why. Revert anything that doesn't move the number.
- Ownership boundaries. When a fix belongs to another lane, write a handoff note
  instead of editing that lane's files. Things that span two lanes get exactly one
  owner: scheduler placement, migrations at boot, API contracts the clients consume.
- Behaviour tests for each fix, not timing assertions.
- Production changes are a list for the person to approve, never done by the lane.

Offer the prompts as separate sessions (cards the person starts), and give the full
text in chat as well so they can be copied. Suggest an order from the `order_note`s:
backend contract changes (new cursors, newest-first windows) land before the clients
that consume them.

**Or execute them as a workflow.** If the person approves the prompts and wants them
run unattended, rerun `workflows/lanes.js` with `mode: "execute"` and
`prompts: [{lane, prompt}]`. Each lane runs harness-first in its own git worktree on a
`perf/<lane>` branch, committing each kept fix with its table row; then, for every kept
fix, an independent agent checks out the fix and its parent and reruns the harness at
least three times. A fix whose improvement does not reproduce beyond noise is flagged
before any PR opens. Nothing is pushed, merged or deployed.

## 4. Approvals do not relay

Approval to merge, deploy or touch production must come from the person, in the
session that acts. A sub-session will rightly refuse a merge approval forwarded by
another session. Choose one of these:

- Ask once, with the full PR list, whether you should merge from the coordinating
  session (recommended).
- Have the person approve in each lane's session directly.

Any PR that opens after the approval was given needs its own yes. Tell the lane
sessions that you are merging, so they don't push to those branches meanwhile.

## 5. Land one PR at a time

Use [scripts/merge-one.sh](scripts/merge-one.sh): `merge-one.sh <pr>`. It does three
things:

1. Refuses the PR unless every check on the current head has finished with none
   failing.
2. Waits out any deploy already running.
3. Squash-merges, then waits for that merge's deploy and exits non-zero if the deploy
   fails.

Chain PRs with `for pr in …; do merge-one.sh $pr || break; done` in the background.
Don't poll with `sleep` loops in the foreground.

- **Order:** harness and benchmark PRs first, then fixes in dependency order, then
  index builds and other operator steps. The operator steps run only with explicit
  approval.
- **Stacked PRs:** after the base squash-merges, retarget the child to main. Expect
  conflicts, because the squash replaced the commits the child was built on. The
  owning lane merges main in, re-runs its gates and reports the new head commit.
  Merge only on checks for that commit.
- **Pushes during the queue:** a lane that pushes while you are merging tells you the
  new head. Judge the PR only on that head's checks.
- **Flakes:** a single red check in code the PR doesn't touch, with no assertion
  message, is re-run once without a new commit. A second red is real.
- **Network blips:** a GitHub timeout is not a failure. The script retries status
  reads, so never let a blip skip a wait.

## 6. Report

When every PR has landed, report:

- the merged PRs, with deploy results
- the before/after tables, or links to them
- the PRs still open and why
- production steps still owed, such as manual index builds, scaling, a pooler or CDN
  changes, each needing its own approval
