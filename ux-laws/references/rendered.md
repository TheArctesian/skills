# The rendered lane

Optional, opt-in with `measure: true`, and only ever against a local or allow-listed target. It exists
for one job: to turn `needs_measurement` claims into measured ones, and to catch the laws that have no source
signal at all. It does not drive the product like a user — that is the `persona-test` skill, and the
two compose: run this for the geometry and timing, that for whether a person can get through.

## When to run it

Worth it when the static lane produced `needs_measurement` findings about geometry, overlap,
contrast or timing, and the app can be served locally. Skip it for a library, a CLI, or a repository
whose app cannot be started without credentials or third-party services.

## What it measures, per route

For each route in scope, at each viewport, in both colour schemes:

| Measurement | Laws | How |
|---|---|---|
| Hit box of every interactive element | `fitts` | `getBoundingClientRect()` over `button, a, input, select, textarea, [role=button], [role=link], [role=checkbox], [role=tab], [onclick], [tabindex]:not([tabindex="-1"])`. |
| The SC 2.5.8 Spacing test | `fitts` | For every target under 24×24, centre a 24 px-diameter circle on its bounding box; the failure is that circle intersecting another target's box or another undersized target's circle. This, not the raw size, is the AA conformance bar — run it before reporting any target as a `must`, and apply the Equivalent, Inline, User Agent Control and Essential exceptions too. |
| Gap between adjacent targets | `fitts`, `proximity` | Pairwise edge distance of targets within 48 px; flag < 8 px between a destructive and a confirming action (Material 3's 8 dp separation guidance). |
| Overlap and occlusion | `fitts`, `selective-attention` | `elementFromPoint()` at each target's centre: if it returns something else, a sticky bar, banner or overlay is covering it. |
| Above-the-fold position of the primary action | `fitts`, `visual-hierarchy` | Rect top vs viewport height at 375×667. |
| Computed gaps within and between groups | `proximity`, `common-region` | Computed margins and the nearest enclosing element with a border, background or `role=group`. |
| Contrast | `visual-hierarchy`, `von-restorff` | Resolved foreground/background pairs against 4.5:1 and 3:1; and a greyscale pass to catch colour-only emphasis. |
| Heading outline and landmark structure | `visual-hierarchy`, `chunking` | `h1`–`h6` order; `main`, `nav`, `header` presence. |
| Accessible names | `recognition-recall` | Every target's computed accessible name; empty is the finding. |
| Count of siblings in each menu, select and nav | `hicks`, `choice-overload` | Children per container, after render — a source count can be wrong when the list is data-driven. |
| Time to first visible change after an action | `doherty` | Click, then observe DOM mutation or `aria-busy`: measure to the first paint-affecting change. 400 ms is the bar. |
| Interaction animation duration | `doherty` | `getComputedStyle` `transition-duration` and `animation-duration` on elements that change on interaction; and whether they collapse under `prefers-reduced-motion: reduce`. |
| Form state after a failed submit | `feedback-loops` | Submit invalid, then read every field's value: anything emptied is the finding. |
| Input tolerance | `postels` | Type a realistic awkward value into each field (`+44 7700 900123`, `o'brien`, `user+tag@example.co.uk`, `4242 4242 4242 4242`, `EH6 6LX` lowercased) and record whether it is accepted, normalised or rejected. |
| Reduced-motion and dark-scheme deltas | `aesthetic-usability` | Re-measure contrast and visibility with each media feature forced. |

Viewports: 375×667 (small phone), 768×1024 (tablet), 1440×900 (desktop). Add 320 px width and 200%
page zoom when the product claims accessibility conformance.

## How to drive it

Any of these, in order of preference:

1. **The repository's own tooling.** If it already has Playwright, Cypress or an accessibility job,
   add a measurement script to it — the project's own browser setup already knows how to log in and
   seed data.
2. **Playwright directly**, headless, one browser context per route batch.
3. **The REA browser tools** (`capture_web_screenshot`, `inspect_web_page`,
   `inspect_web_event_listeners`, `observe_web_execution`) when a repository has no browser tooling
   and installing some is not wanted.
4. **iOS or Android**: the simulator tooling `persona-test` installs; measure from the accessibility
   tree rather than pixels — frames come back in points, which is what the 44 pt bar is in.

Measurement is a script, not a judgement. Write the script, run it, keep the numbers; the lens
agents read the numbers. A finding from this lane quotes the number, the selector and the viewport.

## Rules

- **Local or allow-listed only.** Never measure production. Payments in test mode. No real
  credentials; throwaway local accounts only.
- **One server.** Agents measuring in parallel against one dev server interfere, so route batches run serially: the
  workflow runs one batch agent at a time, and each one starts its own server on a free port and stops it before
  returning. Never run two batches at once against one server.
- **Stop what you start.** Every server, browser and simulator is stopped before the phase returns,
  and any untracked file the run created is removed.
- **Production-mode build where possible**, so dev overlays and HMR banners are not measured as UI.
- **Deterministic data.** Seed the same fixtures every run, or the numbers are not comparable
  between the before and the after of a fix.

## Reporting a measured finding

A measured number is what promotes a pending finding to `certain` or refutes it. Carry:

```
measured: { route, viewport, scheme, selector, value, bar, screenshot? }
```

A measured number that *contradicts* a static finding refutes it — record that, because a refuted
static finding is how the static heuristics get tightened. Static findings that the rendered lane
could not reach (a route behind auth it could not seed) stay `needs_measurement`; they are not
promoted by silence.
