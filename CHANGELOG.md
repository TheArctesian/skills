# Changelog

Workflow scripts return their `version`; bump it with any change to a skill's rules or script,
and record eval scores here.

## 2.5.0 — unreleased

New skill: ux-laws. Audits an interface against 35 laws — 28 of the 30 on lawsofux.com (Cognitive Bias and Flow are
framing rather than checks), plus visual hierarchy, progressive disclosure, recognition over recall, feedback loops and
error prevention from Nielsen's heuristics, asymmetric choice for the deceptive-pattern class the others only point at,
and ai-legibility from Microsoft's HAX guidelines and Google's PAIR guidebook for surfaces whose output is generated
rather than authored. Grouped into five lenses so one reviewer holds one lens per shard; A–D run per shard of screens, E per flow. Two things shape it. First, a
repository is not an interface, so every finding carries an evidence grade — `certain`, `computed` with the arithmetic
shown, or `needs_measurement` with the one measurement that would settle it — and a verifier refutes rather than
downgrades a claim stated above its grade. Second, the laws are the favourite weapon of bad design review, so each law
entry carries its overcorrection and every finding must survive its law's name being deleted from the sentence.
Verification runs three necessary checks: evidence, **reach** (does a person actually meet this, or is it dead code, a
story or a flagged-off variant) and fit (right law, right fix, and section 4's conflict order). Shards are screens and
flows rather than directories, because that is the unit every law is about; lens E runs per flow. An opt-in rendered
lane (`measure: true`) measures geometry, contrast and timing against a locally served build, serially against one
server, and promotes or refutes static claims.

The five criteria new in WCAG 2.2 are reported under the laws that already own their mechanism rather than as new ids,
which converts several bars from convention into conformance: SC 3.3.7 Redundant Entry (A) makes re-keying a value the
system already holds a Level A failure under `teslers`/`recognition-recall`; SC 3.2.6 Consistent Help (A) sits under
`jakobs`; SC 2.5.7 Dragging Movements and SC 2.4.11 Focus Not Obscured (both AA) under `fitts`; SC 3.3.8 Accessible
Authentication (AA) under `recognition-recall`, which makes a blocked paste or a defeated password manager a
conformance failure rather than an opinion.

Run against its eval twice. **First run**: 381 agents, 14.4M tokens, 109 findings — recall 13/13 with the right law,
no decoy confirmed, every cited line verbatim, all 12 computed arithmetics correct on independent recomputation, and
all three fixture traps caught (the flagged-off component excluded by tracing the flag rather than the import, the
clickable div suppressed as already failing a named enabled lint rule, the documented clinical-safety decision upheld
against three separate findings). Three defects that run exposed, all since fixed:

- **80 of 114 findings were duplicates.** Clustering keyed on exact screen-string equality, and the map labelled one
  screen `settings-list` in a shard and `Settings (/account/settings)` in a flow, so one problem drew three independent
  juries — three times the verification cost, the same finding shipped at two different evidence grades, and once
  refuted by one jury while another reported it as a `must`. Four candidate keys were measured rather than guessed; the
  one that merges on law plus `file:line` removes the duplicates and keeps recall at 1.0, while the lens-based key that
  deduplicated hardest collapsed three distinct journey problems into one and dropped recall to 0.85.
- **The estimate understated the run 18.9×** — 23 agents shown against 381 spent, because verification (90% of the run)
  appeared only as a prose note and the critic's gap round was uncapped. The estimate now reports `already_spent`,
  `before_verify`, `verify_max` and `total_max`, and gap passes are capped.
- **A refutation did not bind the deliverable.** Verification caught the documented-decision trap three times and the
  plan merge put the refuted fix back as a step inside an otherwise-sound item, so report and plan told an implementer
  opposite things about a change the fixture records as having mis-booked three clinical appointments. Refutations are
  now passed to the plan as a do-not-resurrect list, and a later lens re-raising a refuted claim goes to `needs_human`
  rather than getting a second jury. `needs_human` itself was unreachable by construction (0 of 342 verdicts were ever
  `uncertain`); it is now a verdict that outranks refutation.

**Second run**, with the clustering fix, resumed from cache: 198 agents, 6.7M tokens, 56 findings over 56 distinct
screen+element pairs with 2 residual duplicate pairs. **Passes**: recall 14/14, 0 decoys confirmed, 0 findings on the
clean screen, 0 grades without their proof, no population claims. Caveats: this run predates the single global
verify barrier, and its plan and report agents hit a session limit, so plan and report quality were scored from the
first run only.

Reviewed before release by a four-agent council (UX substance, repository conventions, workflow engineering, eval
adversary) and corrected: the WCAG 2.5.8 Spacing exception was missing, so undersized-but-separated targets would have
been reported as AA failures at `must`; heading order and reduced motion were cited as conformance when they are best
practice and AAA; Parkinson's Law claimed an effect it does not predict; the choice-overload entry cited Iyengar &
Lepper without Scheibehenne's near-zero meta-analytic replication; the clustering key merged every finding naming the
same shared component into one, so the second was never verified or reported; `claim` mutated findings already
returned; the rendered lane never promoted or refuted the measurements it exists to take; and `measure: true` would
have driven a clicking browser against any `target`, production included. The eval was rebuilt after the adversarial
reviewer scored a single padded finding at recall 1.0 and showed six ways a correct audit failed. Not yet run.

New skill: persona-test. Synthetic-persona usability testing for web (Playwright MCP) and iOS (mobile-mcp on
simulators). Persona agents are custom agent types whose tool allowlist is only their driver, with a private MCP server
each and no CLAUDE.md, so they cannot read the code; they install into `~/.claude/agents` because plugin agents ignore
`mcpServers`. Personas are built from limits the harness enforces; wrong-turn and backtrack limits are applied from the
log; findings need both a reproduction by a different agent and a screen-evidence check. Not yet run against its eval.

Vendored skill: apple-fluid-design, emilkowalski/skills@2d22863 `apple-design` renamed to avoid a clash (MIT; source in
`apple-fluid-design/LICENSE` and `UPSTREAM`). Guidance only, no workflow.

## 2.4.0 — 2026-10-15

app-optimisation `execute` verified on the eval fixture against a throwaway local Postgres 17: the
lane built a harness (seeder, benchmark, contract tests), kept five fixes each with before/after
numbers, and an independent agent reproduced every performance fix against its parent. Feed at 50
VUs went from 8.9 to 2,340 rps (p50 5.4 s to 20 ms); boot from 1.1 s with deadlocks to 0.3 s; 23 tests
pass. The one non-performance fix kept (`/countries` empty-cache guard) was correctly reported as not
reproducing a speed-up. 9 agents, 0.69M tokens, 56 minutes.

Fixes
- Reproductions ran in parallel against one shared database: harness resets corrupted each other's
  measurements, connections ran out, and one agent started its own Postgres cluster. Reproductions now
  run serially, alternating parent and fix, each on a fresh database it creates and drops. Lanes in
  execute mode run serially unless `parallel_lanes: true`.
- A lane left a four-worker uvicorn running. Every workflow now tells agents to stop each server,
  database or background process they start.
- Execute mode takes `env` (appended to every lane prompt, overriding what it contradicts) and
  `root_from` (rewritten to `root`), instead of hand-editing 16k-character prompts.

## 2.3.0 — 2026-10-15

Apply mode verified for two more skills, on eval fixtures with independent checks.

- test-audit campaign (apply): the rewritten suite catches 4/4 production mutations, up from
  3/4 (the non-member default had no real assertion); all 4 junk tests gone, including the
  source grep, replaced by a floor-vs-round table row; suite green, no debris. 21 agents, 0.8M tokens.
- code-quality (apply, 3 plan items): two dependency waves; the dependent item branched from
  its dependency; each branch and all three merged pass the pinned `tsc` gate; target tree
  clean, no worktrees left. Agents flagged their own intended behaviour changes for sign-off.
  7 agents, 0.28M tokens.

Fixes
- code-quality and app-optimisation: apply/execute agents create their own git worktree inside
  the target repo (under `.git/agent-worktrees/`). The Workflow tool's `isolation: 'worktree'`
  isolates the session's repo, not `args.root`, so parallel items would have shared one tree.
- test-audit: preservation mutates every keeper contract, not only restored gaps; the apply run
  above ran zero skill-side mutations because no gap was restored.
- Evals: test-audit apply runs are scored by production mutations the suite must catch; the
  code-quality fixture pins TypeScript 5.9.3 with a lockfile and `setup.sh` installs it offline.

## 2.2.0 — 2026-10-15

First apply-mode run (prune-comments, eval fixture): the edit path works end to end. Workers
edited comments only, an independent `comments.ts verify` confirmed zero code changes, the
py_compile gate stayed green against its baseline, nothing was reverted, and the critic found
nothing left. Edited tree: recall 0.94, keep 1.0, 24 agents, 0.75M tokens.

A second apply run on the pruned tree changed exactly one comment, the one 2.1 wrongly kept,
and nothing else: final tree recall 1.0, keep 1.0, no untracked files.

Fixes
- prune-comments: the profile no longer turns a rule stated in AGENTS.md into an `extra_keep`
  class; a code comment repeating a documented rule is a Duplicate. `extra_keep` stays empty
  unless the docs talk about comments.
- All four workflows: agents delete untracked files their own commands created (caches,
  build output); the 2.1 gate step left `__pycache__/` behind.
- Scorer: untracked files in an apply run's tree count as false positives.

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
