---
name: unix-modularity-standardiser
description: Make codebases easy to navigate and hard to misuse through UNIX-style modularity. Use when asked to make architecture self-explanatory, separate function or module responsibilities, keep background work out of the UI loop, extract duplicated logic, split oversized files, or enforce a code-line limit such as 300 lines.
---

# UNIX Modularity Standardiser

Make the codebase itself supply the context for the next change. From a
feature entry point, a reader should be able to find who owns the behavior,
which API to call, which dependencies are allowed, and where the work runs.
Express those answers in domain names, directory and package boundaries,
public APIs, types, and representative callers and tests.

Give each function one clear job and each module a cohesive responsibility.
Use the repository's code-line limit or default to 300. Size, clone similarity,
and directory names identify where to look. Trace the behavior and dependencies
to decide where a split improves the design.

Use audit mode for requests to review or report. For implementation requests,
make the authorized changes after inspecting the code and taking a baseline.
Ask for a decision when a split would change a public contract or when a
cohesive file needs an exception to an explicit policy.

## 1. Trace a feature from its entry point

Read the repository instructions and documented bootstrap and gates. Pick
a representative change in the affected feature. Start at its UI action,
route, CLI command, or exported API. Follow the callers and imports until
you can point to the owner of the business decision or state, the supported
interface, and any I/O, process, or thread boundary. Use symbol and file
references to show that path. Record any step that requires guessing,
copying a workaround, or reading unrelated internals.

For a refactor, run the affected tests and build, lint, or type checks that
apply. Record pre-existing failures. Identify a runtime path through the real
entry point before editing. Write down the behavior that must hold, including
an error or state transition when the change touches one.

## 2. Measure size and look for clones

Resolve script paths relative to this skill. Run with the target repository or
package root as the scanner argument.

```bash
python3 scripts/scan.py <root> --threshold 300
python3 scripts/dedup.py <root> --min-overlap 0.30
```

The scanner excludes common vendor and generated paths. Its counts approximate
code lines and it measures only the script region of Vue and Svelte files.
It reports total lines alongside the count and ranks violations by overage.
Use `--json` for machine-readable output. Check near-threshold results against
the source when syntax makes the count ambiguous. Reuse the repository's
language-aware tooling when this approximation conflicts with its policy.

The clone scan uses Pygments to normalize identifiers and literals. Use
`--only <fileA> <fileB> ...` to narrow expensive scans to candidate files that
can be compared with each other. Inspect matches for shared responsibility and
behavior before extracting code. Treat directory clusters and file-kind tags as
review cues. A cohesive single class, component, or data table may merit an
exception under the repository's policy.

## 3. Refactor around an enforceable boundary

- Name functions for the job a caller needs done and group them by the behavior
  they implement. Keep orchestration readable as a short sequence of meaningful
  operations. Give business decisions and side effects visible homes when they
  have different owners, lifecycles, or execution requirements. Keep cohesive
  steps together and avoid forwarding helpers that conceal where work happens.
- Put the supported API at the boundary callers encounter. Use types to show
  what crosses it and make a real caller or test easy to find as an example.
  Keep internals private and dependency direction visible in package layout.
  Preserve public entry points and update callers, tests, and build references
  that resolve moved files.
- Extract confirmed shared behavior when callers share the same contract and
  the implementation belongs in a layer they can all depend on. Check the
  execution context as well as the signature before reusing it. Rescan after
  extraction.
- When a correction keeps recurring, look for an API or package boundary that
  prevents the invalid use. For a rule the repository can measure, reuse its
  linter, visibility rules, or dependency checker. Verify that valid callers pass
  and the forbidden dependency fails. Make errors name the source, destination,
  and supported import or API. Scope the check to established boundaries.
- Keep cohesive code together. Avoid making a token split, moving code to a
  catch-all folder, compressing formatting, or creating a facade that lets
  callers bypass the boundary.

### UI and background work

Trace the affected interaction from event handler or render path through
direct and transitive calls. Check which process or thread executes the
work, including work triggered when a module loads. Look for blocking I/O,
expensive computation or allocations, and repeated scheduling on the
interaction path. Moving a function to another file or marking it `async`
does not move its synchronous work off the UI thread.

In Tan's Electron example, agents imported main-process code into the
renderer, causing long tasks and jank. The team named the two execution
contexts in the directory tree and enforced the boundary with dependency
checks and lint. In a similar app, follow its existing process bridge for
main-owned operations. Keep renderer imports on its side of the boundary,
share only contracts or code that fits both runtimes, and use an appropriate
worker for expensive computation when profiling warrants it. Check for
indirect imports through re-exports and shared modules.

Measure the same interaction and workload before and after a change aimed
at responsiveness. Use the runtime's profiler to check UI-thread long
tasks, frame drops, or interaction latency and confirm the work runs in the
intended context. Record what could be measured.

## 4. Enforce the size policy when requested

Prefer the repository's existing size gate. The bundled scanner can run
directly in local checks or CI when its counting policy fits:

```bash
python3 scripts/scan.py <root> --threshold 300 --check
```

Exit status is `0` on pass, `1` on blocking violations, and `2` on
configuration or read errors. With `--check --json`, stdout is JSON containing
all `violations` and the subset in `blocking_violations`. Failure diagnostics go
to stderr. The default scan without `--check` is an audit.

For a gradual rollout against existing debt, take a trusted report from the
pre-change tree. Use that report with the same package scope and threshold:

```bash
python3 scripts/scan.py <root> --threshold 300 --json > baseline.json
python3 scripts/scan.py <root> --threshold 300 --check --baseline baseline.json
```

Use a baseline from the target branch or a reviewed snapshot in CI. A baseline
admits an existing oversized path up to its recorded code count. A file that
crosses the threshold, grows while oversized, or moves to a new path while
oversized fails. Resolved violations disappear from current reports. Refresh a
stored baseline separately when shrinking it so fixed debt cannot reappear
under the previous allowance.

Prove a gate using a valid case and a failing case before depending on it.
Keep clone and mixed-topic detection advisory unless the repository has a
specific rule it can measure reliably.

## 5. Verify and report

Re-run the scan and the affected repository gates and compare with the
baseline. Exercise the identified behavior through the normal CLI, API, or UI,
including relevant failure cases or state transitions. Restart a watcher if it
still refers to a moved path. Record the command or user action, expected
invariant, actual outcome, and any runtime verification you could not perform.

Repeat the feature walkthrough using the resulting names, imports, API,
and a real caller or test. Check that a reader can locate the intended edit
and predict where it runs from that evidence. Validate dependency rules
against the legitimate call path and a forbidden path.

Lead the report with the affected feature path, confusing or misplaced
responsibilities, and the consequences for callers or runtime behavior.
Include evidence from the code and any runtime measurements. Report size
and clone findings with counts and note any applicable policy exceptions.

## Dependencies and source

The scanner uses Python's standard library. The clone detector requires
Pygments. Install it in the target environment or run the detector with
`uv run --no-project --with pygments python scripts/dedup.py <root>`.

The API, lint, and runtime-verification guidance draws on Lauren Tan's
[All Code Is Slop (Except Mine)](https://ai.engineer/code/2026/talks/lauren-tan).
