# Persona and task schema

A persona is the set of things the harness can enforce. Names, ages and backstory barely change what an LLM agent
does; what it can perceive and how soon it must stop do. Without hard limits every persona collapses into one
competent user who finishes everything (agents complete tasks more often and more efficiently than people).

## Persona card

| Field | Values | Enforced by |
|---|---|---|
| `id` | short slug, e.g. `skim-phone-dark` | — |
| `driver` | `web-desktop`, `web-mobile`, `web-tree`, `ios`, `ios-tree` | agent type: viewport or device, and whether a screenshot tool exists at all |
| `settings.text_size` | iOS content size: `small` … `large` (default) … `extra-extra-extra-large`, `accessibility-medium` … `accessibility-extra-extra-extra-large` | `simctl ui content_size` before each session (iOS only) |
| `settings.appearance` | `light`, `dark` | `simctl ui appearance` (iOS); `browser_emulate_media` (web) |
| `settings.locale` | e.g. `ar_SA`, `de_DE` (iOS only) | `defaults write -g AppleLocale` |
| `limits.max_wrong_turns` | 1–6 | workflow counts `wrong_turn` in the log; the session ends there |
| `limits.max_backtracks` | 1–6 | workflow counts `backtrack` in the log; the session ends there |
| `limits.reading` | `skim`, `full` | prompt; skim personas read headings, buttons and first lines only |
| `limits.scroll` | `cue-only`, `free` | prompt |
| `knows` | domain words and products already familiar | prompt |
| `sketch` | one line of context | prompt; never overrides a limit |

Spread the cast across what the harness enforces. A good four:

1. `web-mobile`, skim, cue-only scrolling, 2 wrong turns: the impatient phone user.
2. `web-tree`, full reading, free scrolling, 4 wrong turns: the screen-reader user. Unlabelled controls are invisible.
3. `web-desktop`, full reading, 4 wrong turns, knows a competitor: the careful comparer.
4. `ios` with `accessibility-extra-large` text and dark appearance: layout breakage at large sizes.

Two personas with the same driver and the same limits are one persona. The workflow reports pairs that walk the same
screens in the same order as collapsed.

## Task

| Field | Rule |
|---|---|
| `goal` | What the person wants, in their words, with a checkable end state: "get a refund for last week's order". Never a label, menu name, route or tab from the interface; the workflow rejects goals containing multi-word UI labels or product jargon. |
| `start` | The first screen only: a URL or a deep link. Never a deep link into the middle of the task. |
| `success` | `text` (the final screen shows this text), `url` (the final URL contains this), or `probe` (a local shell command that exits 0 when the end state exists, e.g. `curl -sf localhost:8000/api/orders?user=t1 | grep -q rice`). On iOS the harness screenshots the simulator and checks; on web `text`/`url` are compared with the persona's verbatim final screen. |

Ask for at most the number of tasks requested; fewer, sharper tasks beat padding.
