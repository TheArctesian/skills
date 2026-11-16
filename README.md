# skills

some skills i rly like

| Skill | What it does | Workflow |
|---|---|---|
| [prune-comments](prune-comments/SKILL.md) | Deletes slop comments, keeps contracts, rules and non-obvious reasons; proves the diff is comment-only | `workflows/prune.js` |
| [unix-modularity-standardiser](unix-modularity-standardiser/SKILL.md) | Makes feature ownership and execution boundaries clear from the code. Audits oversized files and duplication, with an optional 300-code-line CI gate. | scripts: `scan.py`, `dedup.py` |
| [code-quality](code-quality/SKILL.md) | CUPID review and refactoring (Composable, Unix philosophy, Predictable, Idiomatic, Domain-based) | `workflows/cupid.js` |
| [test-audit](test-audit/SKILL.md) | Authoring gate, audit and campaign for low-value or implementation-coupled tests | `workflows/test-audit.js` |
| [app-optimisation](app-optimisation/SKILL.md) | Measured performance lanes, benchmark-before-and-after, one-PR-at-a-time landing | `workflows/lanes.js` |
| [persona-test](persona-test/SKILL.md) | Synthetic-persona usability tests: blinded agents drive the real web or iOS UI, findings reproduced and checked against the screen | `workflows/personas.js` |
| [ux-laws](ux-laws/SKILL.md) | Audits an interface against 35 laws of UX from source, grading every finding by how certain its evidence is; optional rendered measurement | `workflows/ux-laws.js` |
| [macos-cleanup](macos-cleanup/SKILL.md) | Reclaims disk on a macOS dev machine: audits agent worktrees (immune to stale `.git` pointers), build output, Docker, simulators, caches and Downloads; proves each deletion safe, asks, remeasures | none (scripts: `scan.sh`, `worktree-audit.sh`, `artifacts.sh`) |
| [motion-audit](motion-audit/SKILL.md) | Measures what moves in the running app, ranks what is missing or wrong, and demonstrates the best proposals in a looping reel; optional reviewed build | none (scripts: `probe.py`, `render_reel.py`; reel template) |
| [apple-fluid-design](apple-fluid-design/SKILL.md) | Apple's fluid-interface and motion principles for the web (springs, gestures, materials, type). Vendored from [emilkowalski/skills](https://github.com/emilkowalski/skills), MIT | none (guidance only) |

## Install

Requires Bash and Python 3.9+. Run from a checkout you plan to keep:

```sh
git clone https://github.com/TheArctesian/skills.git
cd skills
./install.sh           # link into every supported user-wide skill directory
./install.sh --list    # show every supported agent and its resolved path
./install.sh --remove  # remove links made to this checkout
```

The installer covers Codex, Claude Code, OpenCode, Devin, DeepSeek Harness,
DeepSeek TUI, Kimi Code CLI, Cursor, GitHub Copilot, Gemini CLI, and the rest of
the [supported agent registry](scripts/agent-skill-paths.tsv). It prepares the
directories even when the agent CLI is absent. Agents that share a directory
reuse the same links. Edits in the checkout are live, and existing files or
links from other sources are preserved. Restart your agent to refresh discovery.

For project-scoped installation, use `./install.sh --project /path/to/project`.
This includes project-only tools such as Eve and PromptScript. Add `--list` to
preview the paths or `--remove` to undo. These links point to your local checkout
and should stay out of project commits.

All targets receive the `SKILL.md` bundles. The `Workflow` scripts and
persona-test's custom agents use Claude Code features. User-wide install also
links the persona agents into Claude Code's agent directory. To run the
workflows from another project, add your skills checkout to
`permissions.additionalDirectories` in Claude Code settings (or use
`/permissions` → Additional directories). Persona-test uses Node (`npx`) and
requires Xcode with simulators for iOS.

The registry uses the [Vercel Agent Skills compatibility list](https://github.com/vercel-labs/skills/blob/main/docs/agents.md)
and adds [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/skill-filesystem/README.md)
and [DeepSeek TUI](https://github.com/deniscai/DeepSeek-TUI#skills), which read a
shared skills directory. Local installs work offline. Cloud agents need the
bundles in the environment where they run.

## How the workflows are built

Skills with a [Workflow](https://code.claude.com) script invoke it through Claude Code.
The workflows share a common structure across repositories:

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

## Lessons from the evals

Each of these came from a failed eval run, not from design up front:

- **Discovery must not bless what it describes.** A profile step that records current behaviour
  as a "local idiom" or a "client contract" teaches every later agent to protect it. A
  `utils/helpers` folder recorded as the local convention stopped the domain lens flagging it;
  an oldest-first feed recorded as a contract got preserved as a feature. Profiles now describe
  behaviour neutrally and never list a known smell or gap as a convention.
- **Combine different checks by logic, not by vote.** Three verifiers testing three necessary
  conditions (is it real, is it worth it, does the fix fit) must all agree; a 2-1 majority let a
  true-but-trivial finding through on the "it's real" check alone. Where each check is a
  sufficient defence, one is enough.
- **Don't ask for a fixed number of results.** "Top 8 gaps" on a two-file lane produced padding,
  and the padding is where the decoy got in. Ask for "at most N".
- **Merge before you verify.** Lenses overlap by design, so the same smell arrives three to five
  times; verifying each copy cost more than the audit. Merging by file and line cut one audit
  from 209 agents to 62.
- **Vague rules get followed literally.** "Trim a suppression's reason to the shortest the linter
  accepts" produced bare `# noqa` lines, because the linter accepts none. "Concurrency" listed as
  an architectural rule kept a hazard comment that should have become a test finding.
- **Parallel agents must not share stateful resources.** Benchmark reproductions run in parallel
  against one database reset each other's indexes and ran out of connections; one agent started its
  own Postgres cluster to escape. Anything load- or state-sensitive runs serially on its own resources,
  and every agent stops what it starts.
- **The skill will out-review your fixture.** Several "false positives" on supposedly clean
  files were real bugs in the fixture. Check a false positive before tightening the skill. A council
  review of `ux-laws` before its first run found twelve unplanted violations in its own fixture, a
  "clean" screen that described three things the app could not do, and a scorer that passed a single
  padded finding naming every law at full recall — all of which would have been read as skill failures.
  Attack the eval before you trust it.
