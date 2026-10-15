# Lane prompt template

Fill every `<…>` from the exploration report. Keep the evidence specific: file paths,
line numbers and the observed behaviour. Phrase each one as a candidate the lane must
confirm, not as a conclusion.

```text
Make <app>'s <lane> faster: <the metrics that matter to users in this lane, e.g. cold
start, time to open each screen, time to content, scroll smoothness, loading older
content>. Find the real bottleneck with measurements first. Benchmark before and after
every fix, and keep a fix only if the numbers prove it.

Ground rules:
- Synthetic data only; no production access. Any cloud read or write needs my approval,
  asked once in a batch.
- You own <paths>. Changes in <other lane's paths> become handoff notes, not edits.
- Follow <AGENTS.md / CONTRIBUTING>: <size limits, style, generated-project steps>.
- <Lane-specific safety, e.g. "never point a debug build at a real account">.

1. Harness first.
   - <Seed a heavy synthetic user: volumes>.
   - <Build a repeatable benchmark that reports: metrics, endpoints/screens, deep pages>.
   - Run on <production-like engine or build>.
   - Save the baseline to progress.md.

2. Candidates from exploration, ranked. Confirm each with numbers before you fix it.
   1. <gap> (<file:line>): <what was seen>. <Fix direction>. <Any contract check, e.g.
      "check every consumer's expected order first">.
   2. …

3. For each fix:
   - Add a focused behaviour test.
   - Re-run the benchmark.
   - Record a row in the table: metric | baseline | after | kept or reverted | why.

4. Deliverables:
   - The harness and benchmark scripts.
   - Focused PRs, each with its before/after numbers.
   - Handoff notes for <other lanes>.
   - A list of production changes for me to approve.

Gates: <commands>, plus `git diff --check`. Merge origin/main before opening a PR.
Don't merge or deploy. That is a separate approval.
```
