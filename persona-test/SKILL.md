---
name: persona-test
description: Synthetic-persona usability testing of a web app or iOS app. Blinded persona agents (no access to the code) drive the real UI through Playwright or an iOS simulator, each with limits the harness enforces (device, text size, dark mode, screen-reader view, patience); findings are merged, reproduced by a different agent, checked against the screen for "is it the interface or the agent?", then ranked by Nielsen severity with evidence trails. Use when asked to usability-test a product, find where users would get stuck, run a persona walkthrough or synthetic user test, check a flow before a real-user study, or catch UX regressions on localhost or staging. Not a replacement for real users.
---

# Persona test

An agent that has never seen the code tries to do what a user came to do, through the real interface, and stops
where a person would. Findings are hypotheses about the interface, to be confirmed with real users, not a substitute
for them.

## 1. Setup (once)

```sh
<this skill's base directory>/scripts/install-agents.sh   # symlinks agents/persona-*.md into ~/.claude/agents
```

Then start a new session so the agent types register. Plugins cannot ship them: plugin agents ignore `mcpServers`,
and each persona needs its own private browser or device server. Needs Node (`npx` fetches `@playwright/mcp` and
`@mobilenext/mobile-mcp` on first use) and, for iOS, Xcode with simulators.

## 2. Configuration

Fill what you know; empty fields are discovered by the Profile phase.

```yaml
target:        ""     # local URL; empty = detect how to serve it. Non-local hosts need allow_hosts
platforms:     []     # web | ios; empty = detect
personas:      []     # descriptions or cards (references/persona-schema.md); empty = designed from the brief
tasks:         []     # goals in the user's words; empty = proposed from the main journeys
max_personas:  4      # at most, never exactly
max_tasks:     2
step_budget:   25     # actions per session
devices:       {ios: 3}   # simulators booted at once; about 2.5 GB each
max_verify:    10     # clusters verified; the rest are reported unverified
allow_hosts:   []     # staging hosts with test-mode payments and sandboxed mail only
run_tag:       ""     # names this run's simulators (persona-test-<tag>-n)
```

## 3. Run the workflow

Invoking this skill is the opt-in. Run `workflows/personas.js`:

```
Workflow({
  scriptPath: "<this skill's base directory>/workflows/personas.js",
  args: { skill_dir: "<this skill's base directory>", root: "<repo>", target: "http://localhost:3000" }
})
```

If Workflow refuses the `scriptPath` because it is outside the directories this session can read, the skills checkout
is not an added directory (see the repository README). Read the script once and pass its full text as `script`
instead, with the same args; the result returns a `scriptPath` under the session directory, which the confirmed
relaunch reuses.

### Estimate, confirm, run, save

Every launch is two calls. The first runs Profile and Personas only and returns `stage: "estimate"`: the persona
cards, the tasks, session and agent counts, an upper bound on input tokens, simulators and memory, every command it
will run, `suspicious_commands` and `risks`. Show the person the cast, the tasks and the commands and ask before
continuing; a suspicious command or a risk is fixed or approved explicitly. Then relaunch with the same args plus
`confirmed: true` and `resumeFromRunId`, so Profile and Personas come from cache. A token target ("+2M") stops new
work near the limit and lists what it skipped.

Other stages: `setup` (agents not installed: run `install-agents.sh` and restart), `refused` (non-local target, or
live keys / production endpoints / real senders found; pass `accept_risks: true` only after checking).

As soon as a run returns, write the returned object to `<scratchpad>/persona-test-<runId>.json`.

| Phase | Agents | Work |
|---|---|---|
| Profile | 1, sees the code | How to serve or build the app, the product brief (user-facing text only), journeys, visible UI labels, test accounts and data, risks. Sentences in the brief that name code are dropped mechanically. |
| Personas | 1–2 | At most N persona cards built from what the harness enforces, and goal-phrased tasks with a checkable end state. A task linter rejects goals that contain the interface's own labels or jargon; one rewrite, then drop. |
| Provision | 1 | Starts the web app in the background, seeds one throwaway account per persona, builds the iOS app and boots the simulator pool (`scripts/device-pool.sh`). |
| Run | 1 per persona × task (+ prep and end-state check on iOS) | Blinded persona agents (`agents/`) drive the UI and log every step. Web sessions run in parallel, each in an isolated browser; iOS sessions queue on the simulator slots, each starting from a clean install with the persona's settings. Wrong-turn and backtrack limits are enforced from the log; 3+ backtracks become a finding even when the persona finished. Paths that match step for step mark personas as collapsed. |
| Verify | 2 per cluster, both must confirm | Observations merge by screen + element first. **Reproduce**: a plain full-sight agent, not the one that found it, tries the goal. **Evidence**: an agent inspects that screen and decides whether the interface causes the problem (missing, hidden, unlabelled, ambiguous, silent, lossy) or the agent fumbled, including [references/ai-only-obstacles.md](references/ai-only-obstacles.md). A refutation drops a cluster; anything else is uncertain. |
| Critic | 1, parallel with Verify | Journeys and handicap combinations nobody covered. One round. |
| Rank | 1 | Nielsen severity 0–4, trust tier, fix hints in interface terms, and the report in [references/report.md](references/report.md). |
| Teardown | 1, always | Stops the server, deletes the simulators, removes run state. Runs even when an earlier phase fails. |

## 4. Reading the result

- `report` is the human-facing markdown; give it in chat or publish it. It opens with limitations.
- `findings`: confirmed first. Each has `severity`, `kind`, `tier` (`trusted` or `medium`), `reach` (distinct enforced
  handicaps that hit it, not persona names), `blocking` (sessions that did not finish), `evidence` (steps per
  persona) and `verdicts`.
- `sessions`: per persona and task, how it ended and whether the end state was met; `success.by` says whether the
  harness checked it (iOS screenshot, probe) or it was compared with the persona's own final screen text.
- `refuted`, `unverified`, `collapsed`, `coverage_gaps`.

Never restate findings as facts about users: no percentages, no "users will", no quotes as a user's voice. Medium-tier
and uncertain findings go on the "validate with real users" list.

## 5. Safety

- Local or allow-listed staging targets only; payments in test mode; mail and SMS to a sandbox such as Mailpit.
- Personas type only throwaway local test credentials, which appear in their transcripts. Never give real ones.
- Production builds where possible, so dev error overlays and source maps do not leak the code to personas.
- Nothing in this workflow edits the repository, pushes, merges or deploys. Leftover simulators from a crashed run:
  `scripts/device-pool.sh sweep`.

## 6. Not yet

Android (mobile-mcp supports it; needs an AVD and `adb` on PATH), macOS apps (Peekaboo, one persona at a time, in a
VM or a dedicated macOS user), an apply mode that fixes confirmed findings, and before/after re-runs of a fix.
