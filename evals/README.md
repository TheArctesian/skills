# Evals

A dry run proves a workflow's plumbing; these prove the skill makes the right calls. Each
skill has a small fixture repository with planted answers and a deterministic scorer.

| Skill | Fixture plants | Pass bar |
|---|---|---|
| prune-comments | 13 slop comments to delete (history, war story, eternal law, narration, agent-addressed, banner, commented-out code, signature echo); 6 to keep (shebang, `noqa`, `eslint-disable`, a public contract, a spec citation, a measured trade-off); a `//` inside a string | recall ≥ 0.8, keep ≥ 0.9, code untouched |
| code-quality | 7 CUPID problems across P, C, D and I; two clean files that must draw no finding | recall ≥ 0.8 with the right property, 0 findings on clean files |
| test-audit | 5 junk tests (duplicate, private predicate, assertion-free, self-comparison, source grep); 3 real contract tests | recall ≥ 0.8, all 3 kept |
| app-optimisation | 4 real gaps (oldest-N window, N+1, connection per call, migrations at boot); 1 decoy that is already cached | recall ≥ 0.8, decoy not confirmed |
| ux-laws | A clinic booking app with 14 planted violations (a 20px shared icon button flush against a destructive one, 11 flat clinic options, no step indicator, no draft persistence, a strict phone regex, placeholder-only labels, a form wiped on error, a silent booking button, a confirm step that hides what it confirms, a raw transport error and table name, 14 flat toggles, a label gap wider than the field gap, no error boundary); 5 decoys (five grouped nav links, an ISO-only date whose rejection is documented and research-cited, a legacy toolbar imported but behind an off flag, a Storybook-only variant, a clickable div the repo's own enabled lint rule already fails on) and one clean screen | recall ≥ 0.8 with the right law and, for computed plants, the right numbers shown; no decoy confirmed; 0 findings on the clean screen; every grade carrying its proof; no padding against a cap measured from the fixture's own defect count; report free of population claims |
| persona-test | A static shop with 5 usability problems (unlabelled icon-only cart, checkout form wiped on error, delivery address under "Fulfilment profile", silent Save, promo bar covering "Place order" on phones); 3 decoys (a long country select only an agent struggles with, correctly hidden decorative icons, a labelled switch) | recall ≥ 0.8, no decoy confirmed, report free of population claims |

## Run one

```sh
evals/setup.sh prune-comments          # copies the fixture into a fresh git repo, prints the Workflow call
# in a Claude Code session inside that repo: run the call, then again with confirmed: true
# save the confirmed result to result.json
python3 evals/score.py prune-comments result.json                 # audit run: scores the proposals
python3 evals/score.py prune-comments result.json --tree <repo>   # apply run: scores the edited files
```

The scorer prints recall, keep rate, false positives, what was missed or wrongly flagged,
and the workflow `version`; it exits non-zero below the bar.

## Apply runs

Score an apply run with `--tree <fixture copy>`: the scorer reads the edited files and also
fails the run for any untracked file left behind (gate caches, build output). Re-run
`comments.ts verify HEAD $(git diff --name-only)` yourself as an independent proof.

## Second-run check

Run an apply-mode workflow, then run it again on the result and pass that second result
with `--second-run`. A converged skill changes little the second time: `second_run_changes`
near zero for prune-comments, few new findings for the others. A large number means the
skill's judgement is unstable, not that the code got worse.

## When to run

- Before committing a change to a skill's rules or its workflow script.
- After a model upgrade.
- When a real run surprised you: add the surprising case to the fixture and `expected.json`
  first, then fix the skill until it passes.

ux-laws runs static by default (`measure: false`), so nothing is served and no toolchain is installed; its fixture
ships a package.json but no lockfile deliberately. Its decoys test the verifiers rather than the lenses: `legacy-bar`
is imported by a route but behind a compiled-off flag, so the reach check has to trace the flag rather than the import,
and `tooling-covered` is a real problem the repo's own enabled lint rule already fails on, so reporting it by hand is
the error. `decoys_refuted` and `unreachable_traced` are reported but do not gate the run: a workflow that excludes
unreachable UI at the Map phase never reasons about them, and the fixture cannot tell that apart from reasoning well.
Add `measure: true` only against a fixture you have built and served yourself.

The fixture is one web app, so it exercises none of `ai-legibility`, the iOS, Android, CLI, API or email surfaces,
the WCAG 2.2 authentication and dragging bars, `mode: "apply"`, or the rendered lane. Those are untested, not passing.

The scorer is built against its own attacks. One finding may satisfy at most one plant, keywords match the reviewer's
prose rather than the whole finding JSON, and a computed plant scores only when the finding shows the numbers — without
those, a single blob naming every law and every file scored full recall.

persona-test drives a browser, so its fixture is served rather than read: the setup output says how, and the
tasks to pass are in `persona-test/expected.json`. Install its agents first (`persona-test/scripts/install-agents.sh`).

Record each score with the skill `version` in `CHANGELOG.md` when it changes. Fixtures are
deliberately tiny so a run costs a few dozen agents; they measure judgement, not scale.
