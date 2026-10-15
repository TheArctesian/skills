# Evals

A dry run proves a workflow's plumbing; these prove the skill makes the right calls. Each
skill has a small fixture repository with planted answers and a deterministic scorer.

| Skill | Fixture plants | Pass bar |
|---|---|---|
| prune-comments | 13 slop comments to delete (history, war story, eternal law, narration, agent-addressed, banner, commented-out code, signature echo); 6 to keep (shebang, `noqa`, `eslint-disable`, a public contract, a spec citation, a measured trade-off); a `//` inside a string | recall ≥ 0.8, keep ≥ 0.9, code untouched |
| code-quality | 7 CUPID problems across P, C, D and I; two clean files that must draw no finding | recall ≥ 0.8 with the right property, 0 findings on clean files |
| test-audit | 5 junk tests (duplicate, private predicate, assertion-free, self-comparison, source grep); 3 real contract tests | recall ≥ 0.8, all 3 kept |
| app-optimisation | 4 real gaps (oldest-N window, N+1, connection per call, migrations at boot); 1 decoy that is already cached | recall ≥ 0.8, decoy not confirmed |

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

Record each score with the skill `version` in `CHANGELOG.md` when it changes. Fixtures are
deliberately tiny so a run costs a few dozen agents; they measure judgement, not scale.
