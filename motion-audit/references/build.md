# Building the proposals

For when the person asks to build the audit. Keep their standing process if they have one. A programme is finished when every lane is.

## Shape

1. **Re-measure first.** Planners check each proposal against the current branch and may answer DROP or AMEND with evidence. Roughly one proposal in ten will not survive, and that is the audit working.
2. **Write one programme file**: the lane table, the frozen foundation API, and numbered rulings that override plans. Every agent reads it. Settling a dispute there beats re-briefing.
3. **Foundation first, then parallel lanes.** Shared exit, arrival, reorder, spring, async-button and gate code lands first, reviewed. Each file has one owning lane; anything else goes in a handoff note.
4. **Loop each lane**: plan, build, then review until approved. Expect 2–5 rounds.
5. **Integrate**: merge the lanes (ordering any that delete what another still consumes), shrink baselines, merge the base branch, run all gates, repeat a browser pass over the merged app.
6. **Land**: only when told. Read the deploy's real health output, not its green tick.

Read-only plan agents may be unable to write files; pull the plan from their report. Have builders commit before
any full suite and never end a turn waiting on a background run.

## What the reviewer must do

Builders' green gates proved little. In every lane, the reviewer found what they missed by:

- **Mutating**: delete the guard, see which named test turns red; no red is a finding. Tests that merely match source text survive this constantly.
- **Measuring in a real browser**, using [measurement.md](measurement.md), then reading the screenshots.
- **Interrupting**, as the same file lists.

Give the reviewer a detached worktree at the lane's tip so it can mutate freely. Grep the diff for leaked plan
IDs and "round N" in comments before each PR; prose gates miss them.

## Defects to expect

Each of these shipped past green gates once:

| Trap | Fix |
|---|---|
| An exit transition writes `transform`, replacing the transform a list reorder uses to hold the leaving row | Use the individual `translate` property |
| A leaving item in an anchored stack, pinned by the edge that moves, jumps a slot | Pin the anchored edges and its measured width |
| A long-lived entrance animation on a list item stops the framework lifting it out of flow | Put the role on an inner wrapper |
| An async button's styles outrank its host's size; `auto` width never interpolates; `aspect-ratio` makes a disc | Size only in the waiting state, between definite lengths |
| Pending buttons stay pressable; `disabled` turns them hollow | The button refuses activation itself, with `aria-disabled` and `preventDefault` |
| A `:global` rule added to reach a child restyles the whole app | Anchor every one under the component root; gate it |
| An indicator measures a hidden or detached node and remembers 0 | Skip zero boxes; write positions before enabling the transition |
| A view transition dies when a captured node re-renders | Name a wrapper that survives, or render one persistent element |
| A size observer watches the element it animates, and loops | Observe an inner wrapper |
| A skeleton is right but the grid draws from the first partial batch and reshuffles | Treat data as resolved only when complete; hold the old data until then |
| "Same-page" navigation reruns a load because something reads the whole URL, and remounts the page | Track the narrowest dependency, such as the route id |
| FLIP scaling distorts text or doubles the easing | Counter-scale an untransitioned inner node, sample the ease once, share one origin |
| A leaving face still in layout resizes the sheet mid-animation | Pin it until its exit ends |
| A reduced-motion token folds a *threshold* too, so every wait flashes or every touch scrubs | Input and perception thresholds are named constants that do not fold |

## Gates worth adding

Make drift fail, with shrink-only budgets where offenders exist today: transition directives must use tokens or
shared helpers; animation frames are allowlisted with a reason; animation shorthands and hand-written arrivals fail;
component-scoped escapes must be anchored.
