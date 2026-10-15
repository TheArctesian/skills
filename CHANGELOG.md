# Changelog

Workflow scripts return their `version`; bump it with any change to a skill's rules or script,
and record eval scores here.

## 2.1.0 — 2026-10-15

Every change below came from a failed eval run; see "Lessons from the evals" in the README.

Eval scores (audit/explore mode, latest fixtures)

| Skill | Recall | Keep / FP | Agents | Tokens | vs 2.0 |
|---|---|---|---|---|---|
| prune-comments | 1.0 | 1.0 keep, rule finding 1/1 | 13 | 0.5M | 2.0 failed the harder fixture (kept a hazard comment) |
| code-quality | 1.0 | 0 FP | 43 | 1.6M | 2.0: 209 agents, 7.7M tokens, 4 FP |
| test-audit | 1.0 | 1.0 keep | 17 | 0.66M | same score; now repairs a test that could not tell floor from round |
| app-optimisation | 1.0 | 0 decoys | 16 | 0.62M | 2.0: 31 agents, 1.1M tokens, confirmed the decoy |

All four skills
- Verifier verdicts combine by logic: necessary checks must all confirm (code-quality,
  app-optimisation); sufficient defences need only one (test-audit).
- Profiles describe current behaviour neutrally and never record a known smell or gap as a
  local idiom or contract.
- `args.root` points agents at a repository other than the session's directory.

prune-comments
- Hazard comments ("not thread-safe", "leaks") are defects for a "Rule needs a test" finding,
  not architectural rules; suppressions keep a short reason; verdicts use fixed class slugs.

code-quality
- Overlapping findings merge before verification, including across shard, system and critic
  lenses; polish is reported unverified; at most 6 findings per lens.

app-optimisation
- Small lanes (under 25 source files) get one combined sweep; the rank step reports up to 8
  gaps instead of exactly 8; a contract check never defers a checklist gap.

Evals
- Harder prune fixture (stale why, internal-helper doc, duplicated AGENTS.md rule, cited
  workaround, current hazard, suppression reason); realistic app-optimisation fixture (routes,
  schema, volumes, boot-time backfill); code-quality clean files made genuinely clean.
- Scorer: rule-needs-test findings, merged property lists, title-based gap matching, F counts
  as kept.

## 2.0.0 — 2026-10-15

Eval scores
- prune-comments (audit, 2026-10-15): recall 1.0, keep 1.0, false positives 0; 13 agents
  (4 for the estimate), ~490k subagent tokens, ~1.5 min. Reviewers overturned 0 of 19 samples.
- code-quality, test-audit, app-optimisation: not yet run.

All four skills
- Repo-agnostic: a Profile phase discovers components, gates, conventions and CI routing;
  nothing repository-specific is hard-coded.
- Every skill ships a workflow (`workflows/*.js`) with the same shape: profile, shard,
  pipeline, perspective-diverse verification, completeness critic, mechanical proof.
- Two-call launch: an estimate (agent count, every command to be run, suspicious commands
  flagged) before any expensive work; the confirmed run resumes from cache.
- Token-budget guard: new work stops near the user's target and skipped items are listed.
- Verifiers each run a different check and may answer `uncertain`; split verdicts go to
  `needs_human` instead of being silently kept or dropped.
- Repository content is treated as data in every agent prompt.
- Evals: fixture repos with planted answers and `evals/score.py`.

prune-comments
- Defaults to `audit` (per-comment proposals); `apply` is opt-in.
- Reviewers run serially and their edits are proven comment-only.
- `comments.ts` loads TypeScript lazily, rejects TypeScript 7 (no compiler API), honours
  `COMMENTS_TS_PATH`, and runs under Node `--experimental-strip-types` as well as Bun.

code-quality
- Rewritten around CUPID's five properties and their facets; limits are a backstop.
- must/should/could buckets replace invented numeric scores.
- Per-component plans merged into one, so no prompt holds every finding.
- Apply mode runs dependency waves; dependent items branch from their dependency.

test-audit
- Lanes edit only their own test files; production seams and shared support go through one
  serial owner; mutation checks run serially.

app-optimisation
- Lanes detected from the repository; four-angle sweep per lane; `execute` mode with
  independent benchmark reproduction.
