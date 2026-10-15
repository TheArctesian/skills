# Test-pruning campaign

Campaign mode prunes one subsystem's whole test surface in one PR: an adapter
or provider family, one backend domain package, one app route tree or shared
library, or one native feature folder. The value bar, retention bar, candidate evidence, and
validation in [SKILL.md](SKILL.md) apply to every lane. This file adds the
order of work and the lessons of a full campaign. `workflows/test-audit.js`
with `mode: "campaign"` runs steps 1 to 6 as phases; steps 7 and 8 stay inline. Each step ends on its
completion criterion; do not start the next step early.

Keep a progress file in the scratchpad, not the repository. A campaign is
finished when every step is, not at the first lane that passes.

## 1. Baseline

Record the subsystem's test and support line counts and every test file's
pass/fail state at a pinned `main` SHA. Count code lines with the
repository's line counter (blanks and comments excluded), and count production separately. Keep baseline
failures in their own list: in an earlier campaign on a messaging subsystem,
all three were real delivery bugs, not stale tests. Rerun a lone failure
matching the profile's `flaky_signals` alone before listing it.

Done when every in-scope test file has a recorded baseline result.

## 2. Lanes and inventory

Split the surface into **lanes** along production owner boundaries, not file
prefixes. For an integration
family these are typically accounts, sync and scheduling, parsing,
normalisation, upload, health and errors, and the user-facing catalog and setup.
Include the subsystem's cases at shared boundaries (the shared platform layer,
shared packages), its cross-tree drift tests in other languages' trees, and its
evals and scripted scenarios.

Done when every test file, eval, and scenario the subsystem owns belongs to
exactly one lane.

## 3. Read-only ledger per lane

Give each lane to its own read-only agent (`Explore` or `general-purpose`
through the Agent tool). The agent reads every assigned test in full,
including parameter tables. It also reads the production owners and their
entry points, callers, history, and the CI routing that runs the test. Each test declaration goes into a written **ledger** with one mark.
A `pytest.mark.parametrize`, `it.each`, `test.each`, or XCTest case loop is one
declaration unless its rows need different marks; then mark each row.

- `R`: retain, naming the contract and the bug it catches; a retained test that
  only moves to a better-named file stays `R` with the move noted;
- `F`: retain the contract but repair the assertion, such as a vacuous negative
  that passes when only one of several items is missing;
- `C`: consolidate, naming the owner that absorbs the assertion first: a sibling
  table case, a stronger boundary suite, or the shared owner in another tree
  (the `source_of_truth` for a domain rule, the shared package for a shared contract);
- `D`: delete, naming the proof that remains, or why no contract exists.

Judge a test by its assertions, not its name. One test named for retiring a
progress window asserted the window was _not_ cleared.

Done when every declaration in the lane has a mark and an evidence line.

## 4. Layer plan per lane

Treat the per-test ledger as input, not as the edit list. A second read-only
pass, starting from the ledger, looks for the redundant **layer**. In the
earlier campaign, several dispatch suites replayed the same shared compositor
through one mocked preview, around stronger real-stream and HTTP-fixture
suites. Name the **keeper** suite for each contract. Prefer the real transport
boundary with a fake network (an in-process HTTP test client over a
throwaway database, a recorded provider response) over a mocked collaborator. Correct
any ledger errors this pass finds.

Done when each lane plan names its retired files, its keeper per contract, the
assertions to carry into keepers, and the test-only production seams unlocked.

## 5. Cutover

Edit lane by lane. Serialize changes to shared harnesses and support files
(the profile's `shared_support`: conftest
files, base test classes, shared fixtures)
through one owner. With each lane, remove the test-only production seams it
unlocks: injection parameters, getters, reset exports, barrel re-exports,
access widening, and indirection layers. Keep moved suites under the CI routes that ran
them, and run `generated_steps` after adding or removing test files. Shrink
`ratchets` where the campaign removes entries, and respect folder-size gates. Put durable test-ownership rules in the subsystem's
`AGENTS.md` or README, drawn from mistakes this campaign actually found.

Done when every lane plan is applied and each lane's keepers pass.

## 6. Preservation review

Before claiming completion, have independent reviewers compare deleted
coverage against the keepers, one fresh-context reviewer per boundary group.
They look for contracts that lost their only proof. They also look for new
assertions that cannot fail, such as a rejection row the production code never
reaches. The earlier campaign's review found nine real gaps and one
unreachable assertion.

For each restored contract, make one deliberate **mutation** of the production
owner and confirm the keeper goes red. Then restore the source byte for byte
and confirm `git diff` on that file is empty.

Done when every reported gap is restored or rejected with source evidence, and
every restored contract has a caught mutation.

## 7. Product defects

A baseline failure that survives into a keeper is a bug report. Fix it at its
owner as a separate commit, and prove it through the real user flow on the
local loop (the repository's dev script with seeded synthetic data, a
simulator, or a local client against the local backend), never production.
Include a **control** run that reverts the fix and shows the old behavior.
Record unrelated product discrepancies you find as follow-ups instead of
fixing them in the campaign.

Done when each repaired defect has a failing control and a passing candidate
on the same harness.

## 8. Reconcile and hand off

Campaigns outlive many `main` commits. Merge `origin/main` rather than
rebasing a long, many-commit campaign. When `main` modified a file the
campaign deleted, keep the deletion. Port the new contract into the keeper
instead, and confirm every new regression `main` added still has a home.
Rerun the whole subsystem suite, every required gate for each touched
component, and the local user-flow proof on the merged head.

Expect review tooling to see a truncated file list on a diff this large.
Record maintainer decisions for generic compatibility flags in the PR evidence
rather than editing gates.

Hand off with the [SKILL.md](SKILL.md#handoff) report, plus:

- baseline and final test/support line counts, with production counted separately;
- lanes, retired layers, and keepers;
- preservation gaps found and their mutations;
- product defects with control and candidate proof.
