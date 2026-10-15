# Changelog

Workflow scripts return their `version`; bump it with any change to a skill's rules or script,
and record eval scores here.

## 2.0.0 — 2026-10-15

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
