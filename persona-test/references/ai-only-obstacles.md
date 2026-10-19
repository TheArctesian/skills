# AI-only obstacles

Trouble a driving agent has that people do not. A finding that rests only on one of these is refuted by the evidence
check. The list is inlined in `workflows/personas.js` (`AI_ONLY`); keep the two in sync.

- A long native select or picker: people type to jump; agents scroll the options.
- A standard date or time picker.
- Hover-only tooltips whose text is also shown inline.
- An action taken during an animation or transition.
- A tap that landed off target by coordinates (iOS), where the target itself is a normal size.
- Decorative images correctly hidden from the accessibility tree (`aria-hidden`, `accessibilityHidden`).
- A carousel or banner that moves on its own, when nothing the task needs is inside it.
- Needing to scroll a page that visibly continues (cut-off content, a scroll bar, a partial card).

## Not on this list: people hit these too

- The on-screen keyboard covering a field or the submit button.
- A permission prompt arriving before the app explains why.
- A control with no accessible name (invisible to screen-reader users).
- Tap targets under 44 pt.
- Text truncated or overlapping at large text sizes.
- A form that clears input on a validation error.

Platform notes: Flutter apps without `Semantics` expose an almost empty accessibility tree, so agents fall back to
screenshots and coordinate taps and miss more; an empty tree is itself an accessibility finding, but downstream
findability findings from such sessions deserve suspicion.
