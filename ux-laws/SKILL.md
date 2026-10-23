---
name: ux-laws
description: "UX-law audit of any repository's interface, from source first and optionally from the rendered app. Use when asked to audit, review or improve UX; to check a screen, flow, component library or design system against the laws of UX (Hick's, Fitts's, Jakob's, Miller's, Doherty, Tesler's, Postel's, Occam's razor, the Gestalt grouping laws, peak-end, goal-gradient, serial position, Von Restorff, progressive disclosure, recognition over recall, visual hierarchy, feedback loops and the rest); when asked why an interface feels slow, cluttered, confusing or unresponsive; or before shipping a redesign. Covers accessibility-adjacent heuristic evaluation as well as the laws — Nielsen heuristics, WCAG target size, labels and contrast. Maps 35 laws to signals that are visible in code, grades every finding by how certain its evidence is, refuses to state an unmeasured claim as fact, and fans out a multi-agent audit per screen and per flow. Complements persona-test, which drives the real UI blind; this one reads the interface."
---

# UX laws

[The laws of UX](https://lawsofux.com/) are observations about perception, memory and attention. They
are directions, not rules: "fewer choices here", "answer faster", "group what belongs together". The
value of auditing against them is that each one names a *mechanism*, so a finding can say why a screen
costs the person something, rather than that someone disliked it.

Two things make this hard to do honestly, and both shape the whole skill:

**A repository is not an interface.** The laws are claims about what someone sees; source is what
produces it. So every finding carries an **evidence grade** — `certain` (the source says so outright),
`computed` (arithmetic over tokens and styles, shown), or `needs_measurement` (depends on render,
theme or data). An unmeasured claim is never reported as fact. [references/signals.md](references/signals.md)
is the bridge: what to grep, how to compute a hit box from padding and tokens, and when to stop.

**The laws are the favourite weapon of bad design review.** "Hick's Law" quoted at a nav, "7±2" quoted
at a list, "progressive disclosure" quoted at a feature someone wanted hidden. Every law entry
therefore carries its overcorrection, and a finding must survive its law's name being deleted from the
sentence. If what is left is not a concrete cost to a person, it is not a finding.

## 1. Configuration

Leave a field empty and discovery fills it from the repository (its `AGENTS.md`/`CLAUDE.md`/
`CONTRIBUTING`, design-system docs, theme files, routers). The repository's own design system, research
and documented conventions always win over these defaults.

```yaml
scope:         ["."]        # repo, UI paths, or "diff:main"
mode:          audit        # audit (findings + plan) | apply (execute an approved plan)
surfaces:      []           # web | ios | android | desktop | cli | api | email; empty = detect
laws:          []           # subset by id (see section 2); empty = all that apply to the surfaces
measure:       false        # also run the rendered lane (references/rendered.md); local targets only.
                            # Needs a browser driver: the repo's own Playwright/Cypress, the REA browser tools,
                            # or (for mobile) the simulator tooling persona-test installs
target:        ""           # local URL for the rendered lane; empty = discovered from the repo
allow_hosts:   []           # staging hosts to permit besides localhost. Test-mode payments, sandboxed mail only
accept_risks:  false        # proceed past a flagged serve command or a risk the profile named. Check first
viewports:     [[375,667],[768,1024],[1440,900]]
design_system: ""           # tokens/theme path; empty = discovered. Its values beat the defaults below
votes:         3            # verifiers per finding, each a different check (evidence, reach, fit)
max_gaps:      0            # critic gap passes to re-lens; 0 = max(4, 2 per shard). Each is one more lens agent
shard_screens: 6            # screens per lens review
max_findings:  6            # at most, per lens per shard. Never a target
```

## 2. The laws

35 laws in five lenses. Each lens is one reviewer's whole job for one shard, because a reviewer
holding all 35 finds none of them well. Lenses A–D run per shard of screens; lens E runs per flow,
since its laws do not exist on any single screen. Full entries — claim, signal, bar, fix, overcorrection,
source — are in [references/laws.md](references/laws.md); the table below is the index a reviewer
reads before opening a file.

### A — Choice and load: how much the interface asks the person to decide or hold in mind

| id | Law | The finding looks like |
|---|---|---|
| `hicks` | Hick's Law | More than ~7 siblings in one decision with no grouping, default or search; two equal primary actions |
| `choice-overload` | Choice Overload | ~6+ comparable options with nothing recommended or defaulted |
| `millers` | Miller's Law | A 7+ character string shown or typed unchunked; a form of 7+ fields with no sections. Never "more than seven items" |
| `chunking` | Chunking | A wall of text or a flat list of related items with no heading, divider or group |
| `cognitive-load` | Cognitive Load | Internal vocabulary, raw ids, enums, HTTP codes or unconverted units in user-facing text |
| `working-memory` | Working Memory | A step that needs a value it does not show |
| `progressive-disclosure` | Progressive Disclosure | Everything rendered at once with no primary/advanced split — or a required control hidden behind one |
| `occams-razor` | Occam's Razor | A step, field or confirm dialog whose removal costs the person nothing |
| `teslers` | Tesler's Law | The person formatting, converting, computing or re-keying what the system could |
| `pareto` | Pareto Principle | The main journey is not the shortest or most prominent path. Needs usage data |
| `parkinsons` | Parkinson's Law | A flow whose common case could be prefilled and is not |
| `asymmetric-choice` | Asymmetric choice | Consent defaulting to on; an accept and a decline with unequal prominence; an urgency figure with nothing behind it; cancelling longer than signing up |

### B — Form, grouping and hierarchy: what the eye groups and ranks before reading

| id | Law | The finding looks like |
|---|---|---|
| `proximity` | Law of Proximity | A related pair whose gap is ≥ its gap to the nearest unrelated element |
| `similarity` | Law of Similarity | Different kinds of action styled the same, or one kind styled two ways |
| `common-region` | Law of Common Region | A control whose enclosing card, border or surface differs from what it acts upon |
| `praegnanz` | Law of Prägnanz | A layout whose intended reading order is not its simplest available reading |
| `uniform-connectedness` | Law of Uniform Connectedness | A sequence or relation asserted but never drawn |
| `visual-hierarchy` | Visual Hierarchy | Two primaries on one screen, heading levels used as sizes, the main action the weakest, emphasis in colour alone |
| `von-restorff` | Von Restorff Effect | Everything isolated, or the one genuinely different option not isolated |
| `selective-attention` | Selective Attention | Required information in banner position or marketing styling |
| `aesthetic-usability` | Aesthetic-Usability Effect | Off-token one-off values; or a polished happy path with unstyled error, empty and loading states |

### C — Reach and response: the cost of acting, and whether the system answers

| id | Law | The finding looks like |
|---|---|---|
| `fitts` | Fitts's Law | Hit area under 24×24 CSS px *and* failing SC 2.5.8's Spacing test (AA failure); under 44 on touch; < 8 px between a destructive and a confirming action; primary action out of reach on a phone |
| `doherty` | Doherty Threshold | A user-initiated async action with no visible change within 400 ms; interaction animation over 400 ms; a wait over 1 s with no indicator or over 10 s with no estimate |
| `feedback-loops` | Feedback Loops | A state change with no visible outcome; a swallowed error on a user path; a destructive action with neither confirm nor undo; input lost on a failed submit |
| `paradox-active-user` | Paradox of the Active User | A task that cannot be completed without reading something outside the interface |
| `error-prevention` | Error Prevention | An irreversible action reachable without a deliberate second act; a mutation that can be submitted twice; a constraint known up front but applied only after submitting |

### D — Expectation and memory: what the person already knows, and what you make them know

| id | Law | The finding looks like |
|---|---|---|
| `jakobs` | Jakob's Law | A re-implemented native control that drops keyboard, form or platform behaviour; a broken Back button or deep link; a hijacked shortcut; a conventional thing in an unconventional place |
| `recognition-recall` | Recognition over Recall | Placeholder as the only label; an icon-only control with no accessible name; a value the person must retype that the system holds; no `autocomplete` |
| `mental-model` | Mental Model | A label whose behaviour differs from what the word means; one concept named two ways across UI, API and docs |
| `postels` | Postel's Law | Validation that rejects a valid real-world value it could normalise: spaces in a card or phone number, `+` in an email, apostrophes in a name, one date format, a required scheme, a short `maxlength` |
| `ai-legibility` | AI legibility | Generated output with no marker that it was generated, no provenance, no failure state, no way to correct or dismiss a suggestion, or an irreversible action taken from it with no review |

### E — Journey and ending: laws that only exist across more than one screen

| id | Law | The finding looks like |
|---|---|---|
| `goal-gradient` | Goal-Gradient Effect | A flow of 3+ steps with no visible position and total; progress starting at zero when work is already done |
| `serial-position` | Serial Position Effect | The primary and the most-used actions not at the ends of their series; a functional menu ordered alphabetically |
| `peak-end` | Peak-End Rule | A completed journey with no designed end state; a main-path error rendered by a default framework page |
| `zeigarnik` | Zeigarnik Effect | A long or multi-step flow with no persisted partial state and no resume |

## 3. Measurable signals

Measure first; a number points at a place to apply judgement, never at the fix. Anything marked
*rendered* cannot be settled from source — see [references/rendered.md](references/rendered.md).

| Signal | Laws | Bar | Source of the bar |
|---|---|---|---|
| Interactive hit area | `fitts` | ≥ 24×24 CSS px, **or** under it and passing the Spacing test: a 24 px circle centred on the target intersects no other target's box (`must` only if both fail) | WCAG 2.2 SC 2.5.8 (AA) and its five exceptions |
| Hit area on touch | `fitts` | ≥ 44×44 (`should`) | WCAG SC 2.5.5 (AAA), Apple HIG 44 pt, Material 48 dp |
| Gap between destructive and confirming action | `fitts` | ≥ 8 px | Material 3's 8 dp target separation |
| Time to first visible change after an action | `doherty` | ≤ 400 ms | Doherty |
| Feedback needed by wait length | `doherty`, `feedback-loops` | none < 0.1 s; indicator > 1 s; estimate and an exit > 10 s | Nielsen's response-time limits |
| Interaction animation duration | `doherty` | 150–300 ms typical, ≤ 400 ms | convention from platform motion guidance; no standard sets a duration |
| Interaction animation collapses under `prefers-reduced-motion` | `doherty` | 100% | WCAG 2.3.3 (AAA) |
| Siblings in one decision | `hicks`, `choice-overload` | > 7 ungrouped, or > 6 comparable with no default: look | convention; neither Hick's nor Iyengar & Lepper sets a threshold |
| Controls rendered at once on a screen | `progressive-disclosure` | > 10 with no primary/advanced split: look | convention |
| Consent controls defaulting to on; accept and decline of unequal prominence | `asymmetric-choice` | 0 | EU DSA Art. 25, FTC |
| Irreversible actions reachable without a deliberate second act | `error-prevention` | 0 | Nielsen heuristic 5 |
| A value re-entered within one process, not auto-filled or selectable | `teslers`, `recognition-recall` | 0 | **WCAG 2.2 SC 3.3.7 Redundant Entry (A)** |
| Help mechanisms in the same relative order across pages | `jakobs` | 100% | **WCAG 2.2 SC 3.2.6 Consistent Help (A)** |
| Drag-operated functionality with a single-pointer alternative | `fitts`, `error-prevention` | 100% | **WCAG 2.2 SC 2.5.7 Dragging Movements (AA)** |
| Focused element never entirely hidden by sticky or fixed content | `fitts`, `selective-attention` | 100% | **WCAG 2.2 SC 2.4.11 Focus Not Obscured (AA)** |
| Authentication without a memory, transcription or puzzle test; paste and password managers work | `recognition-recall`, `cognitive-load` | 100% | **WCAG 2.2 SC 3.3.8 Accessible Authentication (AA)** |
| Generated output marked as generated; review before anything irreversible or outward-facing | `ai-legibility` | 100% | Microsoft HAX 1, 9, 11, 16; Google PAIR |
| Unchunked string the person must read, copy or verify | `millers` | ≥ 9 characters with no familiar grouping | convention; Miller and Cowan motivate chunking but count chunks, not characters |
| Inputs with a visible persistent label | `recognition-recall` | 100% | Nielsen heuristic 6 |
| Interactive elements with an accessible name | `recognition-recall`, `fitts` | 100% | WCAG 4.1.2 |
| Inputs with an `autocomplete` token where one exists | `recognition-recall`, `teslers` | 100% | WCAG 1.3.5 |
| Swallowed errors on a user path | `feedback-loops` | 0 | — |
| State-changing actions with no visible outcome | `feedback-loops` | 0 | Nielsen heuristic 1 |
| Destructive actions with neither confirm nor undo | `feedback-loops`, `occams-razor` | 0 | Nielsen heuristic 3 |
| Input preserved after a failed submit | `feedback-loops` | 100% | — |
| Validation rejecting a valid real value | `postels` | 0 | Postel |
| Primary emphases per screen | `visual-hierarchy`, `von-restorff` | 1 | — |
| No heading level used purely for size | `visual-hierarchy` | 0 | WCAG 1.3.1 |
| Heading levels not skipped | `visual-hierarchy` | 0 breaks | best practice; skipping a level is not a 1.3.1 failure |
| Emphasis surviving greyscale | `von-restorff`, `visual-hierarchy` | 100% | WCAG 1.4.1 |
| Contrast of text and of emphasis | `visual-hierarchy` | 4.5:1 text, 3:1 large and non-text | WCAG 1.4.3, 1.4.11 *(rendered)* |
| Related gap vs unrelated gap | `proximity` | related < unrelated | Gestalt *(rendered for composed components)* |
| Hard-coded values where a token exists | `aesthetic-usability` | 0 | the repo's own design system |
| Flows of 3+ steps showing position and total | `goal-gradient` | 100% | — |
| Flows persisting partial state | `zeigarnik` | 100% of long or multi-step flows | — |
| Designed end state per completed flow | `peak-end` | 100% | — |
| Designed error, empty and loading state per screen | `peak-end`, `aesthetic-usability` | 100% of main-path screens | — |
| Primary action above the fold at 375×667 | `fitts`, `visual-hierarchy` | yes | *(rendered)* |
| Targets occluded by sticky bars or overlays | `fitts`, `selective-attention` | 0 | *(rendered)* |

Use the repository's own tools for what they cover — `eslint-plugin-jsx-a11y`, `axe`, Lighthouse,
`pa11y`, SwiftLint, Android Lint, stylelint — and never re-report what one of them already fails on.
Compute the rest from the files, as [references/signals.md](references/signals.md) sets out.

## 4. When laws disagree

They contradict each other constantly, and a finding that ignores the conflict is wrong half the
time. The order below resolves it; an audit that departs from it says so.

1. **Level A and AA conformance wins over every law**, and nothing in a repository waives it — not a
   documented convention, not the product's own research. A target that fails both the 24 px bar and
   SC 2.5.8's Spacing test, a programmatic label, and the 4.5:1 / 3:1 contrast ratios are not
   trade-offs. AAA criteria (SC 2.5.5's 44 px, SC 2.3.3's reduced motion) and NN/g guidance such as
   persistent visible labels are strong defaults that resolve at rule 2 or 3, not conformance.
2. **The product's own research wins over a law.** Documented findings, analytics and prior tests
   beat a general observation about people. A law never overrules measured evidence from this product.
3. **Convention (`jakobs`) wins over novelty, including over the novelty a law seems to suggest.**
   Deviate deliberately, and the deviation is the thing that needs justifying.
4. **Then the specific conflicts:**
   - `hicks` vs `teslers` — fewer choices vs complexity that cannot be destroyed. Removing an option
     the person still needs does not reduce complexity; it moves it to them. Stage the decision
     instead, or pick a default they can override.
   - `progressive-disclosure` vs `recognition-recall` — hiding reduces load and destroys
     recognisability. Hide only what the common case does not need, never what it is looked for by.
   - `jakobs` vs `von-restorff` — be familiar vs stand out. Stand out in brand and content; be
     conventional in controls, placement and gestures.
   - `occams-razor` vs `feedback-loops` — remove the step vs confirm the action. Replace a confirm
     with an undo where the action is reversible; keep the confirm only where it is not.
   - `aesthetic-usability` vs everything — it predicts that polish buys tolerance. It is never a
     reason to defer a fix; its real warning is that a beautiful screen hides problems in testing.
   - `fitts` vs `proximity`/`common-region` — reachable vs grouped. Growing targets pushes groups
     apart; tightening groups shrinks separation. Target geometry wins: pass the Spacing test first,
     then re-establish grouping with a shared background, border or divider rather than with gap.
     Grouping has channels other than distance; hit area does not.
   - `doherty` vs the labour illusion — answer fast vs make real hidden work visible. Pacing is
     defensible only where work is genuinely happening and the narration is true (naming each
     provider actually queried). Delay with nothing behind it, or narration that does not correspond
     to real steps, is a deceptive pattern however well it tests.
   - `serial-position` vs `jakobs` — most important first vs the platform's own order for confirm and
     cancel. Rule 3 decides it: keep the platform's order.
   - `millers`/`hicks` numbers vs anything — the numbers are conventions for where to look, and
     neither law supplies one. A finding whose whole argument is a count is not a finding.
5. **Still contradictory, or it turns on how the product wants to be read?** It goes to
   `needs_human`. This audit does not settle product strategy.

## 5. Fixing one finding (inline)

1. **Reproduce it where the person meets it.** Find the route, step or state. If you cannot reach it,
   it may be dead UI; check that before fixing anything.
2. **Read the component and its call sites.** Most findings belong to a shared `Button`, `Input`,
   `Modal` or theme token, not the screen you found them on. Fix the shared thing once.
3. **Name the law and then delete it from the sentence.** If what is left does not describe a cost to
   a person, stop — there is nothing to fix.
4. **Check section 4.** If an accessibility criterion, the product's research or an established
   convention bears on it, they decide, not the law.
5. **Change the smallest thing.** Padding before layout, a token before a component, a copy change
   before a flow change, an undo before a dialog.
6. **Verify the way the finding was made.** A `computed` hit-box fix is verified by recomputing; a
   measured one by re-measuring at the same viewport; a copy change by reading it aloud.
7. **Re-run the repository's own gates**, especially its accessibility and visual-regression jobs —
   a spacing change that fixes proximity usually moves a screenshot baseline.

## 6. Auditing a repository (workflow)

For a screen, a component library or a whole product, run `workflows/ux-laws.js` from this skill's
directory; invoking this skill for an audit is the opt-in.

```
Workflow({
  scriptPath: "<this skill's base directory>/workflows/ux-laws.js",
  args: { skill_dir: "<this skill's base directory>", scope: ["."], mode: "audit", votes: 3 }
})
```

If Workflow refuses the `scriptPath` because it is outside the directories this session can read, the
skills checkout is not an added directory (see the repository README). Read the script once and pass
its full text as `script` instead, with the same args; the result returns a `scriptPath` under the
session directory, which the confirmed relaunch reuses.

### Estimate, confirm, run, save

Every launch is two calls. The first returns `stage: "estimate"` after only the cheap discovery
phases: the surfaces found, the screens and flows, which laws apply, whether the rendered lane can run,
every command the run will execute with `suspicious_commands` flagged, and an `agents` block giving
`already_spent`, `before_verify`, `verify_max` and `total_max`. Approve against `total_max`, not
`before_verify`: verification is roughly nine tenths of the run, so a count that omits it understates
the job by an order of magnitude. `total_max` is a ceiling that assumes no finding merges with another,
and clustering typically removes a third to a half of them.
Show the person that estimate and the commands and ask before continuing; a suspicious command is
removed or approved explicitly. Then relaunch with the same `scriptPath` and args plus
`confirmed: true`, passing `resumeFromRunId` from the first call so discovery comes from cache. If the
person set a token target ("+2M"), the workflow stops starting new work near it and lists what it skipped.

As soon as a run returns, write the returned object to `<scratchpad>/ux-laws-<runId>.json` before
doing anything else, so a lost session does not lose the report.

| Phase | Agents | Work |
|---|---|---|
| Profile | 1 | Surfaces, frameworks, design system and tokens, accessibility tooling in CI *and separately the specific rules it fails the build on*, quoted with their config — only a named enabled rule suppresses a finding later, because a tool being installed is not coverage. Documented conventions and prior research, each quoted with its file. How the app is served. Describes behaviour neutrally: it never records a smell as a convention. |
| Map | 1 per surface | Screens from routes, modals, steps and tab panels; flows from the route graph and step machines; shards of at most `shard_screens` screens that belong to one flow or area. Marks UI with no path from a route as unreachable, and excludes stories, fixtures and generated code. |
| Signals | 1 per surface | Section 3 signals mechanically: hit-box arithmetic through the theme, option counts, label and accessible-name coverage, swallowed errors, validation patterns, animation durations, token bypasses. Numbers only, no judgement. |
| Lenses | 4 per shard | One reviewer per non-journey lens (A–D), reading the shard's screens in full with only its own laws in mind, against [references/laws.md](references/laws.md) and the measured signals. At most `max_findings` each; zero is a valid answer. Findings are collected, not yet verified. |
| Flows | 1 per flow | Lens E across a whole journey, which no single screen holds: position, persistence, end states, failure states, first/last placement. |
| Rendered | 1 per route batch, serial | Only with `measure: true`: the measurements in [references/rendered.md](references/rendered.md) against a locally served build. Promotes `needs_measurement` findings to measured, and refutes the ones the numbers contradict. |
| Verify | `votes` per cluster, once every lane has reported | A barrier, not a per-shard step: the lanes re-find each other's problems constantly, so verifying as each shard finished drew three independent juries per problem — three times the cost, the same finding shipped at two different evidence grades, and once refuted by one jury while another reported it. Every lane's findings meet in one registry and cluster before a single verifier runs. Each verifier runs a different check: **evidence** (is the code or number really that, at the grade claimed?), **reach** (does a real person meet this — is the component on a reachable screen, not dead UI, a story, a flagged-off variant or an admin tool?), **fit** (is this the right law, is the fix an overcorrection, does section 4 override it, does the repo document it as deliberate? — a Level A or AA failure is never overridden by documentation, and goes to a human instead). Each is a necessary condition, so a finding survives only if all confirm; any refutation drops it and anything else goes to `needs_human`. Findings on the same screen and element are merged first so each problem is verified once, and `could` findings are reported unverified. A verifier can also answer `needs_human`, which outranks every other verdict; so does a later lens re-raising a claim verification already refuted, because that is the audit disagreeing with itself. |
| Critic | 1, plus 1 per gap up to `max_gaps` | Laws, screens, flows or surfaces with suspiciously little attention — a form-heavy screen with no `postels` finding, a multi-step flow with no lens E finding, a design system with no `aesthetic-usability` finding. Those get one more lens round. |
| Plan | 1 per surface, 1 for the gap passes, then 1 merge | Per-surface plans keep each prompt small; the merge folds findings that share a shared component or token, fixes cross-surface `depends_on`, orders by dependency then by conformance then by must/should/could, and resolves contradictory fixes on one element rather than shipping both. Refuted candidates are passed in as a do-not-resurrect list, because a refutation has to bind the deliverable and not just the findings list. No numeric scores. |
| Report | 1 | The document in [references/report.md](references/report.md), written from the verified findings, the measurement list, the refuted candidates and what was checked and found sound. |

Other stages the first call can return instead of `estimate`: `no-surface` (nothing user-facing in
scope), `refused` (a non-local `target`, a serve command the profile flagged, or a named risk — fix
it, drop `measure`, or pass `accept_risks: true` after checking) and `failed` (the profile agent, or
every map agent, returned nothing; re-run with `resumeFromRunId`).

`mode: "apply"` with `args.plan` (items the person approved from an audit) runs items in dependency
waves, each in its own git worktree on a `ux/<slug>` branch based on its dependency's branch: change
the shared component or token first, run the gates of the surfaces the item touches — including
accessibility and visual regression — commit. An item whose dependency did not land is not applied
against an unchanged base; it is reported as blocked. Items within a wave run **serially**, because
browser and screenshot gates are shared state in the way `app-optimisation` learned databases were;
pass `parallel_items: true` only where the gates are known to be isolated. A fresh reviewer then checks each branch's diff against its base, and re-verifies
the finding's own measurement. Each branch is one pull request; nothing is merged or pushed.

After the workflow, present the report from [references/report.md](references/report.md) and ask which
items to apply. Applying is a separate run.

### Reading the result

- `report` is the human-facing markdown; it opens with what the audit could and could not see.
- `findings`: each carries `law`/`laws`, `screen`, `element`, `what` (in the person's terms), `evidence`,
  `grade`, `arithmetic` when computed, `shared_component` when the fix belongs to one, `fix`, `tradeoff`,
  `conflicts_with`, `priority` and `effort`. `grade_corrected_from` means a verifier or a measurement
  changed the grade; `unverified: "budget"` means a token target stopped its verification.
- `needs_measurement`: verified findings whose evidence stops at the source, each naming the one
  measurement that would settle it. Only the rendered lane empties this list.
- `plan`: items in dependency order, each with `verify` — how to prove the fix the way the finding was made.
- `polish`: `could` findings, reported unverified. `refuted`: candidates verification rejected, with the
  reason. `needs_human`: calls the audit will not make for you — a Level A/AA failure a document claims
  to waive, a conflict section 4 does not settle, a claim a later lens re-raised after verification had
  refuted it, and anything whose verifiers all failed. Read this list before the findings. `checked_and_sound`: what was examined and found fine. Plus `critic_gaps`,
  `unreachable`, `skipped_for_budget` and `rendered`.

## 7. Review checklist

For a changed screen or component, without running the workflow:

- **A** Can the person see fewer than ~7 things to decide between, with a default? Is anything being
  asked for that the system knows, could infer, or does not need yet?
- **B** Is there exactly one primary emphasis? Are related things closer to each other than to
  anything else? Does every emphasis survive greyscale? Are the error, empty and loading states
  designed to the same standard as the happy one?
- **C** Is every target at least 24×24, and 44 on touch? Does every action produce a visible change
  within 400 ms? Does every failure keep the person's input and tell them what to do? Is any error
  swallowed? Can every destructive action be undone?
- **D** Is every native control native, or a custom one that matches it on keyboard, focus and form
  behaviour? Does Back still work? Does every input have a visible label and an `autocomplete`
  token? Does any validation reject a value a real person would type?
- **E** Does the flow show where the person is and how much is left? Does it survive being abandoned?
  Is the last screen designed, and is the worst screen designed?
- Does every finding name a cost to a person once the law's name is deleted from the sentence, and
  does it state its evidence grade?

Blinded end-to-end walkthroughs of the running product are the `persona-test` skill, whose safety rules
the rendered lane follows; code structure behind the interface is `code-quality`. A wait that is genuinely
slow rather than merely unacknowledged is an `app-optimisation` lane, not a fix here — `doherty` findings
are about the missing acknowledgement.

Spring-based motion is judged on perceived settle and interruptibility, not on a duration number: a spring
has no fixed duration, so the 150–300 ms convention above does not apply to one. See `apple-fluid-design`,
and never report a spring as a `doherty` finding on its `duration` parameter alone.
