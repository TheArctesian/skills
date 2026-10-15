---
name: code-quality
description: "CUPID code-quality review and refactoring for any repository and language. Use when asked to review, clean up, restructure, split, move or modularise code; when a size, complexity or structure gate fails; when asked to make code more composable, predictable, idiomatic or domain-based; or for a component or whole-repo quality audit. Not for routine feature edits. Judges code against CUPID's five properties (Composable, Unix philosophy, Predictable, Idiomatic, Domain-based), backs judgement with measurable gates and a shrink-only baseline, and fans out a multi-agent audit workflow for repository-scale reviews."
---

# Code quality: CUPID

[CUPID](https://cupid.dev/properties/) describes properties of joyful code, not rules.
Each property is a direction ("more composable"), not a pass/fail line. Code has a centre
of gravity: moving it toward one property usually moves it toward the others. The gates
measure what can be measured; this skill covers the judgement they cannot, and every
finding names the property it serves.

The five properties decide; the numeric limits are a backstop that points at places to
look. A file under every limit can still fail CUPID, and a file over one may be the right
shape (a generated table, a single cohesive parser). Never make a change whose only
justification is a number.

## 1. Configuration

Leave a field empty and discovery fills it from the repository (its `AGENTS.md`/
`CLAUDE.md`/`CONTRIBUTING`, lint configs, CI). The repository's own limits always win
over these defaults.

```yaml
scope:          ["."]            # repo, component paths, or "diff:main"
mode:           audit            # audit (findings + plan) | apply (execute an approved plan)
gates:          []               # lint, typecheck, test, structure commands per component
limits:                          # defaults when the repo sets none; counted in code lines
  file_lines:     300
  function_lines: 60
  params:         4
  complexity:     15
  nesting:        4
  folder_files:   12
baseline:       ""               # shrink-only debt file, if the repo has one (section 4)
votes:          3                # verifiers per finding, each a different check (evidence, worth, fit)
shard_files:    12               # files per lens review; one directory or concept per shard
```

## 2. The five properties

Each property has facets. For each: the question to ask, the smells that answer "no",
the fix direction, and the overcorrection to avoid.

### C: Composable — plays well with others

| Facet | Ask | Smells | Fix |
|---|---|---|---|
| Small surface area | Could a caller use this after reading only its exported names? | Exports nobody imports; option bags with 10 flags; "kitchen-sink" classes; barrels re-exporting internals | Export the minimum; split a wide API along its callers' needs |
| Intention-revealing | Do names and signatures say what it does without reading the body? | `process(data)`, `handle(x, true, false)`, boolean parameters, stringly-typed modes | Name the intent; enums or separate functions instead of flag parameters |
| Minimal dependencies | Can it be used, and tested, without dragging half the system in? | Imports from many domains; core logic reading env, clock, DB, HTTP or DOM directly; tests that need heavy mocks; import cycles | Plain data in, plain data out; I/O at the edge; inject the boundary, not the world |

Overcorrection: an interface or factory per class "for testability". Abstraction with one
implementation and no second caller is surface area, not composability.

### U: Unix philosophy — does one thing well

| Facet | Ask | Smells | Fix |
|---|---|---|---|
| Single purpose, outside-in | Can you state its purpose in one sentence with no "and"? | Files that are "X and also Y"; functions with section comments; modules whose halves change at different times or for different people | Split on the seam where the "and" sits |
| Simple, consistent model | Does it behave like the neighbouring units built the same way? | One-off conventions; a pipeline stage that also logs, retries and caches | Do one stage; compose stages |

This is not SRP's "one reason to change". Do not split things that always change
together (a type and its parser, a component and its styles). Line count is a symptom;
never cut mid-concept to hit a number (`part2.ts`, `more.rs`).

### P: Predictable — does what you expect

| Facet | Ask | Smells | Fix |
|---|---|---|---|
| Behaves as expected | Does it do what its name says, every time, and nothing else? | `get*` that writes; hidden caching; side effects in constructors, getters or render paths; silent fallbacks to defaults | Rename to the truth, or remove the surprise |
| Deterministic | Same input, same output? | Reads of clock, randomness, env, global or module state inside core logic; order-dependent iteration over hash maps; tests that flake | Pass time, randomness and config in; keep global state out of the core |
| Observable | When it fails or slows, can you see why from outside? | Swallowed errors (`catch {}`, `except: pass`, `_ = err`); `any`/`unknown` returned as success; panics on input; no logs or metrics at boundaries | Typed errors (`Result`, discriminated unions, typed exceptions); structured logs and metrics at I/O edges, not sprinkled through the core |

Overcorrection: logging every line. Observability lives at boundaries.

### I: Idiomatic — feels natural

| Facet | Ask | Smells | Fix |
|---|---|---|---|
| Language idioms | Would an experienced developer in this language write it this way? | Java-style getters in Python; manual loops where the standard library has the operation; ignoring the formatter or linter defaults; fighting the type system with casts | Adopt the ecosystem's formatter, linter and conventions at their defaults; see `references/` |
| Local idioms | Does it match how this repository already does the same thing? | Three HTTP clients; two error types for one job; a new pattern introduced next to an established one without migrating either | Copy the neighbouring shape; if the local idiom is wrong, change it everywhere in a separate change |

Overcorrection: rewriting working code into a fashionable idiom with no reader benefit.

### D: Domain-based — the code models the problem

| Facet | Ask | Smells | Fix |
|---|---|---|---|
| Domain language | Would a domain expert recognise the names? | `data`, `info`, `item`, `obj`, `payload`; weasel suffixes `Manager`, `Service`, `Helper`, `Handler`, `Processor`, `Factory`, `Util`; primitive obsession (`string` ids, `number` money) | Name the concept; wrap costly-to-confuse primitives in domain types |
| Domain structure | Does the tree read like the business? | Top-level `models/ services/ controllers/ utils/ helpers/ common/ misc/ components/` as dumping grounds; a feature scattered across five layer folders | Group by domain (`billing/invoices/`), layers inside a domain if at all |
| Domain boundaries | Are module boundaries where the domain's boundaries are? | One module reaching into another's tables or internals; shared "core" packages every domain edits; cross-domain DTO soup | Each domain owns its data and exposes a small API; translate at the boundary |

## 3. Measurable signals

Measure first; a number points at a place to apply judgement, never at the fix.

| Signal | Property | Default limit |
|---|---|---|
| Code lines per file | U | `limits.file_lines` |
| Lines per function, parameters, complexity, nesting | U, C | `limits.*` |
| Files per directory | D | `limits.folder_files` |
| Exports with no importer outside the module | C | 0 |
| Fan-out (distinct modules imported) and import cycles | C | cycles: 0 |
| Grab-bag or weasel names in paths and types | D | 0 |
| Swallowed errors, `any`, unchecked casts, panics on input | P | 0 |
| Clock, random, env or global reads inside core modules | P | 0 |
| Suppressed lints without a stated reason | I | 0 |

Use the repository's linters for what they cover (Clippy, typescript-eslint, Ruff,
golangci-lint, SwiftLint, detekt) and compute the rest with `git ls-files`, a code-line
counter that skips blanks and comments, and the language's import graph.

## 4. The shrink-only baseline

When a limit lands on a repository with existing debt, record each offending file and its
current number in a baseline file. A recorded file may shrink but never grow; a new file
must meet the limit. After improving a file, lower or remove its entry in the same change,
so the improvement is locked in. Never add entries by hand or raise a number to make a
change pass; split the code instead. If the repository has no baseline and the audit
finds widespread debt, propose one as a plan item rather than tightening linters at once.

Suppress a lint only with a stated reason (`#[expect(clippy::x, reason = "...")]`,
`// eslint-disable-next-line rule -- why`, `# noqa: RULE  why`).

## 5. Fixing one failure (inline)

1. **Measure.** Run the gate; read which rule failed and by how much.
2. **Read the whole unit** and its callers before cutting. List its responsibilities as
   one-line sentences; each sentence is a candidate unit (U).
3. **Find the seam**, best first: a domain concept with its own vocabulary (D); pure logic
   versus I/O (C, P); a UI section with its own state; a pipeline stage (U); a group of
   routes for one resource (D).
4. **Move, do not rewrite.** Relocate code verbatim, fix imports and visibility, run the
   tests; change behaviour in a separate step if at all. Keep public paths stable with
   re-exports where callers are many.
5. **Name for the domain.** A new folder is a noun from the business; a new file is named
   for what it does (`recurring/schedule.rs`, not `recurring/helpers.rs`).
6. **Verify** with the package's tests and every gate, then lower the baseline.

## 6. Auditing a repository (workflow)

For a component or a whole repository, run `workflows/cupid.js` from this skill's
directory; invoking this skill for an audit is the opt-in.

```
Workflow({
  scriptPath: "<this skill's base directory>/workflows/cupid.js",
  args: { skill_dir: "<this skill's base directory>", scope: ["."], mode: "audit", votes: 3 }
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
| Profile | 1 | Components, languages, gates, the repo's own limits and baseline, local idioms worth matching. |
| Measure | 1 per component | Section 3 signals per file; groups files into review shards along directories or concepts. |
| Lenses | 5 per shard | One reviewer per CUPID property, each reading the shard in full against section 2 with only its own property in mind. |
| System | 5 | Repo-wide lens per property: dependency graph and cycles (C), tree shape (D), cross-component idiom drift (I), error and observability strategy (P), units with mixed purposes spanning files (U). |
| Verify | `votes` per finding | Each verifier runs a different check: evidence (is the code really like that?), worth (is the churn justified?), fit (is the fix an overcorrection or off-idiom?). Verdicts are confirmed, refuted or uncertain; a finding needs a confirmed majority, and findings without a refuted majority go to `needs_human` instead of being dropped. |
| Plan | 1 per component, then 1 merge | Per-component plans keep each prompt small; the merge sees item summaries, folds shared seams, fixes cross-component `depends_on`, and orders by dependency, then by must/should/could. No numeric scores. |
| Critic | 1 | Names properties, components or signals with no coverage; those get another lens round. |

`mode: "apply"` with `args.plan` (items the person approved from an audit) runs items in
dependency waves. Each item gets its own git worktree on a `cupid/<slug>` branch, based on
its dependency's branch (merging several when it has several), so dependent refactors
build on each other instead of conflicting: move-don't-rewrite, gates, baseline ratchet,
commit. A fresh reviewer then checks each branch's diff against its base. Each branch is
one pull request; nothing is merged or pushed.

After the workflow, present the plan grouped by property with the top items first, and ask
which items to apply. Applying is a separate run.

## 7. Review checklist

- **C** Is every export used outside its module? Could a caller use it from its signature
  alone? Is I/O at the edge, with the core taking and returning data?
- **U** Can each new or changed unit be described in one sentence without "and"?
- **P** Does every name tell the truth? Is the core deterministic? Do errors surface as
  typed results, with logs and metrics at the boundaries?
- **I** Does it read like the language's standard style and like its neighbours?
- **D** Do folder, file and type names come from the domain? Would a newcomer find it?
- Did the change grow a baselined file, or add a suppression without a reason?

Per-language idioms and seams:

- Rust: [references/rust.md](references/rust.md)
- TypeScript and Svelte: [references/typescript-svelte.md](references/typescript-svelte.md)
- Python: [references/python.md](references/python.md)
- Anything else: [references/other-languages.md](references/other-languages.md)

Writing or changing tests follows the `test-audit` skill; a move that forces a test to
change is a sign the test asserted implementation.
