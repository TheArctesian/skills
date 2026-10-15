---
name: test-audit
description: "Invoke whenever writing, changing, reviewing, or sweeping tests in any repository. Authoring gate for new tests, audit workflow for low-value, implementation-coupled or duplicative tests and the test-only production seams they demand, and a multi-agent campaign workflow that prunes a whole subsystem's test surface with ledgers, adversarial verification and mutation-checked preservation review."
---

# Test Audit

Three modes, one value bar. **Authoring** gates every new or changed test at write time.
**Audit** runs focused sweeps for tests that re-assert source, duplicate stronger proof,
couple behaviour to implementation, or keep test-only production seams alive; it finds a
few high-confidence candidates per batch. **Campaign** prunes one owner's whole test
surface (a backend domain package, an app route tree, a library, a native feature folder);
read [CAMPAIGN.md](CAMPAIGN.md) before starting one. Optimise for confidence, not deletion
count.

Read the root `AGENTS.md`/`CLAUDE.md` and the owning component's docs first. Tests use
synthetic data only; a fixture never carries real user records, credentials or live
hostnames, and an audit never "fixes" one by pasting real data in.

## Repo profile

Audit and campaign work starts by filling this profile from the repository; the
workflows' Profile phase does it for you. Every later section reads from it.

```yaml
components:        # each: paths, test dirs, test runner command, formatter, gates
source_of_truth:   # the layer that owns domain rules (usually the backend/API); others don't replay them
ci_routing:        # how CI picks tests: workflow path filters, a changed-path classifier, a monorepo tool graph
cross_tree_tests:  # tests that hold one language/tree to another's source of truth (drift tests)
gate_suites:       # structure, architecture, style and policy tests that are the repo's gates
ratchets:          # shrink-only baseline files tests read (size, clock reads, comment prose)
generated_steps:   # commands to rerun after adding/removing test files (xcodegen, gradle sync, codegen)
retention_extra:   # repo-specific contract classes to keep (ownership, permission, member-facing copy)
flaky_signals:     # red results that are usually machine load (date/zone, simulator kill, render tests)
```

## Authoring gate

Before adding any test, answer four questions; a missing answer means do not add it yet:

1. What observable behaviour, invariant, or independent contract does it protect?
2. What credible regression makes it fail?
3. Why does existing coverage not already catch that failure? Each contract has one
   primary test owner at the strongest boundary; another layer needs its own distinct
   risk, such as a transport or lifecycle failure the owner cannot reach. A domain rule is
   owned by `source_of_truth`, not replayed in every client. Prefer extending a
   parametrized or table-driven case or a shared fixture over a near-duplicate test;
   consolidate duplicated setup in the same change.
4. Does it need a production seam (export, barrel re-export, `internal`/`@testable`/
   `@VisibleForTesting` widening, flag, wrapper, injection hook) that no production caller
   needs? If yes, move the test to the real boundary instead.

Then check the test against every [junk pattern](#junk-patterns); a match fails the gate
unless the [retention bar](#retention-bar) names the contract it independently guards. A
test that would break under behaviour-preserving refactoring is asserting implementation;
rewrite it at the owning boundary before landing it.

Bug regression tests must fail on the pre-fix code for the intended reason and pass after
the owner-boundary repair. A regression test that never demonstrably failed proves the
mock, not the fix. One regression at the owner boundary covers the bug; do not replay the
same scenario at every layer it crosses.

New test files obey the repository's file-size limit and mirror source ownership
(`tests/billing/` mirrors `src/billing/`). Split a growing test file on a natural seam, not
by line count.

## Junk patterns

The shared checklist: the authoring gate rejects a new test that matches one, and audits
hunt for existing tests that do.

- assertion-free coverage probes;
- self-comparisons and identity copiers;
- copied fixtures, inventories, manifests, catalogs, or export lists;
- exact source, import, or string greps that pin one file's spelling of an expression
  rather than a rule every file must obey;
- private predicate or call-shape tests duplicated at real boundaries;
- duplicate invocations of the same contract;
- provider-local replays of shared helpers (an adapter re-testing the shared platform
  mechanics it only calls);
- tests whose only purpose is preserving test-only exports, globals, barrel entries, or
  wrappers;
- dead production code whose only callers are tests;
- expected values produced by the helper, formatter, or renderer under test;
- mocks that implement the asserted behaviour, or one identical mock standing in for
  different APIs;
- fixtures that supply the receipt, admission, or callback ordering the owner should
  produce, or persistence asserted against a store the path never writes;
- capability tests that restate declared flags or scopes instead of exercising the
  delivery, rejection, or acknowledgement the flag promises;
- negative controls that pass for an unrelated reason, such as a 401 from a different
  guard or a rejection the production path never reaches;
- names or fixtures that promise more than the input exercises, such as a "retires the
  window" test asserting the window was not cleared.

## Value bar

Tests justify their maintenance cost by protecting behaviour, a credible regression, or an
independently meaningful contract. In an audit, an existing test that must change for
behaviour-preserving reorganisation is suspect, not automatically deletable.

Before judging a candidate, read the complete test and production owner, its entry point,
callers, callees, sibling implementations, overlapping tests, CI routing, and relevant
history (`git log -L` or `git log --follow` on both files). When the test claims
dependency-backed behaviour, inspect the dependency source or types directly (the
installed package, the virtualenv, the vendored checkout).

Find which CI job runs the test and which source paths trigger it (`ci_routing`). Jobs that
trigger on files in other trees mark cross-tree drift tests; moving a test or its source
out from under a filter silently stops it running.

## Retention bar

Keep a test when it independently enforces a public API, wire, protocol, adapter, config,
migration, storage, security, ownership, capability, platform-permission, default,
prompt-byte, user-facing copy, generated cross-language, package, release, or architecture
contract, plus anything in `retention_extra`. That explicitly includes:

- `cross_tree_tests` that hold one language to another's source of truth;
- `gate_suites`: the repository's structure, architecture and style gates;
- vocabulary and copy tests that enforce the repository's content design;
- call ordering when order is observable behaviour (dispatch pipelines, migrations);
- regressions with a credible failure mode;
- source inspection when it is the cheapest independent guard: it fails when the contract
  changes (the user-facing key, byte, path, or a rule every file must obey) and survives an
  identifier-only refactor. A source test that pins one file's exact expression and was
  rewritten at the last refactor fails this bar; rewrite it as the rule it stands for or as
  a behaviour test;
- a retained test that fails on the baseline: treat it as a possible product bug, reproduce
  it, and repair the owner rather than deleting it.

Static or slow is not a deletion reason. A test that resembles implementation may still be
the independent contract; prove otherwise before removing it. Shrinking a `ratchets` file
is welcome; growing one to make an edit pass is not.

## Candidate evidence

Record every field before editing. A missing field means the candidate is not ready:

- exact test name and location;
- what failure it can actually detect;
- non-test callers of the covered production or support seam;
- stronger remaining owner-boundary proof, or why no proof is needed;
- the CI job and path entries that route it;
- relevant history and the reason the test or seam exists;
- production or test-support deletion unlocked;
- risk and the focused validation command.

## Running it as a workflow

Invoking this skill for an audit or campaign is the opt-in. Use
`workflows/test-audit.js` from this skill's directory:

```
Workflow({
  scriptPath: "<this skill's base directory>/workflows/test-audit.js",
  args: { skill_dir: "<this skill's base directory>", mode: "audit" | "campaign",
          scope: ["<owner paths>"], apply: false, votes: 3 }
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


| Phase | Agents | Work |
|---|---|---|
| Profile | 1 | Fills the repo profile above. |
| Baseline | 1 per component | Runs in-scope test files at the pinned SHA; records pass/fail and test vs production line counts. |
| Lanes | 1 | Splits the surface along production owner boundaries; every test file, eval and scenario in exactly one lane. The estimate returns here. |
| Ledger | 1 per shard of ~8 test files | Reads each test and its owners in full; marks every declaration `R`/`F`/`C`/`D` with evidence. Audit mode marks only junk-pattern hits. |
| Challenge | `votes` per `D`/`C` mark | Each skeptic defends the test a different way: a contract only it catches, a CI route the absorber lacks, a retention-bar class. Each check is a sufficient defence, so a mark survives only if every skeptic says it stands; one defence reverts it to `R`, and uncertain verdicts go to `needs_human`. |
| Layer | 1 per lane | Names the keeper suite per contract, the retired layers, the assertions to carry, the seams unlocked. |
| Cutover | 1 per lane, then 1 serial owner | Only with `apply: true`. Lanes edit only their own test files, in parallel. Every production seam removal and shared-support edit goes through one serial agent afterwards, so two lanes never edit the same file. |
| Preserve | 1 per lane + 1 mutation per restored contract, serially | Fresh reviewers compare deleted coverage to keepers; each restored contract and every keeper contract gets a mutation that must turn its keeper red, then a byte-for-byte restore. Mutations edit production, so they run one at a time. |
| Critic | 1 | Unmarked files, lanes without keepers, uncaught mutations, baseline failures without a follow-up. |

Without `apply`, the result is the ledger and layer plans for the person to approve.

## Edit shape

Choose one coherent owner-boundary batch in one component. Delete obsolete test-only
exports, barrel re-exports, access widening, globals, wrappers, and dead production paths
instead of preserving aliases. Move retained regressions to their canonical owners.
Consolidate repeated package or dependency assertions into one generic contract.

Prefer net-negative production LOC. Do not add replacement tests that restate the same
implementation, and do not convert uncertain candidates into cleanup to increase deletion
counts. Run `generated_steps` after adding or removing test files.

## Validation

Never edit source or tests while a watch-mode runner or long native test run is using the
checkout. Run gates in the foreground with a generous timeout; commit before a full suite.

1. Run the smallest owner and sibling tests with the component's runner. For runners that
   can silently select zero tests (XCTest `-only-testing`, `--tests` patterns), read the
   executed-count line; zero is not a pass. Run one simulator or device suite at a time.
2. For removed source greps or copied inventories, run the gate, script, or drift test that
   owns the real contract and confirm it still fails when the contract is broken.
3. Run the component formatter, then `git diff --check`.
4. Run every required gate for each component the patch touches.
5. Inspect `git diff --numstat`; report production and tooling separately from tests and
   test support.
6. After final audit edits, run `/code-review` over the diff.

A single red matching `flaky_signals` with zero assertion failures is usually load or
another run on the machine. Rerun it alone before treating it as a retained test failing on
the baseline.

## Landing and continuation

Commit, push, or open a PR only when authorised; merging is a separate authorisation. Work
on a branch in a linked worktree, merge `origin/main` into it before opening the PR, and
open one focused PR per owner batch. If the repository has no required checks, auto-merge
lands at once; confirm checks are green by hand. After a batch lands, refresh from current
`main` and rerun read-only discovery for the next high-confidence batch.

## Handoff

Report:

- root cause and removed low-value categories;
- production owner simplifications;
- retained false positives and why they remain valuable;
- focused and full proof actually run, and any toolchain that was unavailable stated
  separately from a failed check;
- production versus test LOC;
- PR and merge state;
- named follow-ups.
