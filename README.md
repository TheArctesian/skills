# skills

some skills i rly like

| Skill | What it does | Workflow |
|---|---|---|
| [prune-comments](prune-comments/SKILL.md) | Deletes slop comments, keeps contracts, rules and non-obvious reasons; proves the diff is comment-only | `workflows/prune.js` |
| [code-quality](code-quality/SKILL.md) | CUPID review and refactoring (Composable, Unix philosophy, Predictable, Idiomatic, Domain-based) | `workflows/cupid.js` |
| [test-audit](test-audit/SKILL.md) | Authoring gate, audit and campaign for low-value or implementation-coupled tests | `workflows/test-audit.js` |
| [app-optimisation](app-optimisation/SKILL.md) | Measured performance lanes, benchmark-before-and-after, one-PR-at-a-time landing | `workflows/lanes.js` |

## How the workflows are built

Every skill ships a [Workflow](https://code.claude.com) script that the skill tells Claude to
run; invoking the skill is the opt-in. They share one shape so they work on any repository:

1. **Profile.** One agent reads `AGENTS.md`/`CLAUDE.md`/`CONTRIBUTING`, manifests and CI to find
   components, languages, gates and conventions. Nothing repo-specific is hard-coded; pass
   `args.profile` to skip discovery.
2. **Shard.** Per component, an inventory agent measures and splits the work into small shards
   (files, test files, lanes). Smaller shards mean more agents and closer reads.
3. **Pipeline.** Each component, and each shard inside it, flows through its stages without
   waiting for the others (`pipeline()`); barriers only where a stage needs every result.
4. **Verify.** Every destructive or opinionated call (a deletion, a finding, a suspected gap)
   is checked by verifiers that each test a different condition, combined by logic rather
   than vote: when every condition is necessary (is it real, is it worth it, does the fix
   fit) all must pass; when any one is a sufficient defence (a test guards a unique
   contract) one is enough.
5. **Critic.** A final agent looks for what was missed and feeds another round until dry.
6. **Prove.** Mechanical checks where possible: comment-only diffs, mutation tests, gate
   baselines, reproduced benchmarks.

Every launch is two calls: the first stops after discovery and returns an estimate (agents,
commands to be run, anything suspicious) for the person to approve; the second passes
`confirmed: true` and resumes from cache. Workflows default to read-only modes and respect a
token target. Verifiers each run a different check and can answer "uncertain", which goes to
a human rather than being guessed.

[evals/](evals/README.md) holds a fixture repo per skill with planted answers and a scorer;
run them before changing a skill. Versions and scores live in [CHANGELOG.md](CHANGELOG.md).

Each script takes `args.skill_dir` (the skill's base directory) so its agents can read the
skill's rules instead of copies of them. Nothing in a workflow pushes, merges or deploys.
