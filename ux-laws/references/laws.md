# The laws

One entry per law: what it claims, the signal that shows it in source, the bar that turns the
signal into a finding, the fix direction, and the overcorrection that misusing the law produces.
`id` is what a finding reports. Lens letters group laws for the review phase (A–E).

A law is a direction, not a rule, and most of them are a *reason* rather than a *threshold*. Where a
number appears it comes from a standard (WCAG, Apple HIG, Material) or a measured study, and it is a
place to look, never the finding itself. A screen that trips no signal can still be bad, and a screen
over a number can be right.

Cognitive Bias and Flow appear on lawsofux.com as framing rather than as anything a reviewer can
check against a file; they inform the lenses below and get no entries of their own.

---

## Lens A — Choice and load

How much the interface asks the person to decide, hold in mind, or work out.

### `hicks` Hick's Law
**Claims.** Time to decide grows with the number and complexity of choices: RT = a + b·log₂(n+1).
**Signal.** Count sibling options presented at one level: nav items, menu entries, `<option>`s,
radios, cards in a picker, tabs, settings rows, toolbar buttons, CLI flags in one group.
**Bar.** The law sets none — reaction time grows smoothly with n, and nothing discontinuous happens at
seven. ~7 ungrouped siblings is a convention for where to look. The finding is the *absence of structure*
at whatever count the screen has: no grouping, no search, no default, no recommendation. Also: two or more
equally-weighted primary actions on one screen.
**Fix.** Group into labelled categories, provide a sensible default or recommendation, add search
once a list is long, or split the decision across steps.
**Overcorrection.** Hiding options an expert needs behind progressive disclosure, or capping a list
at seven because of a number. Hick's applies to a *decision*, not to a scrollable list of content:
a feed of 200 posts and a search result page are not Hick's violations.

### `choice-overload` Choice Overload
**Claims.** Too many comparable options can suppress the decision itself, not just its speed
(Iyengar & Lepper's 24-vs-6 jam study: 60% vs 40% stopping, 3% vs 30% buying). It does not generalise:
Scheibehenne, Greifeneder & Todd's 2010 meta-analysis of 50 experiments found a mean effect near zero,
and the effect survives only where the options are genuinely comparable, the chooser is not a domain
expert, and the stakes are felt. Those three conditions are what the signal below selects for; where they
do not hold, there is no finding here. Note too that 6 was the study's *good* condition, not a threshold.
**Signal.** Plan or pricing tiers, product variants, template galleries, permission matrices,
onboarding paths rendered as a flat comparable set.
**Bar.** Convention, not a measured threshold: more than ~6 comparable, similarly-priced,
similarly-described options in one decision with nothing marked as popular, recommended or default. No
study sets a number anywhere between 6 and 24.
**Fix.** Mark a default, reduce to the options that differ meaningfully, or stage the choice
(pick a goal → show the two plans that fit it).
**Overcorrection.** Removing options people actually use, or pre-selecting the most expensive one
and calling it a recommendation.

### `millers` Miller's Law
**Claims.** Immediate memory holds about seven *chunks* — and the useful half is "chunk", not "seven".
Later work (Cowan) puts unaided capacity nearer four.
**Signal.** Long unbroken strings the person must read, copy or verify: card numbers, IBANs, phone
numbers, order ids, API keys, OTP codes, hashes rendered as one run of characters; forms with many
fields in one undivided block.
**Bar.** Convention, not a figure from Miller or Cowan, neither of whom counted characters: a string of
~9+ characters shown or entered with no familiar grouping, and a form of more than ~7 inputs with no
fieldsets, sections or steps. Where the thing already has a conventional grouping — a card, an IBAN, a
phone number — matching it is `jakobs`; the chunking argument is what applies to everything else.
**Fix.** Chunk the string (`4242 4242 4242 4242`), group the form into named sections, and format as
the person types rather than rejecting their spaces.
**Overcorrection.** Using "7±2" to justify a design limit — the law does not say a menu may have
seven items. Never quote the number as a cap; [lawsofux.com/millers-law](https://lawsofux.com/millers-law/)
warns about exactly this. A finding whose only argument is "more than seven" is not a Miller finding.

### `chunking` Chunking
**Claims.** Information grouped into meaningful units is easier to take in and recall than a flat run.
**Signal.** Walls of text with no headings; settings pages as one long list; tables with no column
groups; a changelog, a receipt or a diff with no visual segmentation.
**Bar.** Convention, with no study behind the figures: a block of more than ~5 related items or a text
region over ~150 words with no heading, divider or grouping element.
**Fix.** Headings, sections, dividers, summary rows — structure that matches how the content is used.
**Overcorrection.** Decorative sectioning that fragments one idea into three cards.

### `cognitive-load` Cognitive Load
**Claims.** Mental effort spent on the interface is effort not spent on the task; extraneous load is
the kind to remove.
**Signal.** Jargon and internal vocabulary in user-facing strings (service names, table names, enum
values, "fulfilment profile", "consignment"); raw ids and codes shown instead of names; units,
currencies or timezones left for the person to convert; error text quoting a stack or an HTTP status.
**Bar.** Any user-facing string containing an internal identifier, a raw enum, or a term that appears
nowhere in the product's own domain language.
**Fix.** Say it in the domain's words; resolve ids to names; render the unit; state what to do next.
**Overcorrection.** Removing precision engineers need (a request id in a support footer is load worth
carrying), or replacing a specific message with a friendly vague one.

### `working-memory` Working Memory
**Claims.** Information needed to finish a step must be *on* the step; anything carried between
screens is at risk.
**Signal.** A value shown on one screen and required on a later one (a code, a total, a reference);
a confirmation step that drops what is being confirmed; a wizard that discards earlier answers from view.
**Bar.** Any step that requires a value it does not display, or that cannot be re-read without
leaving the flow.
**Fix.** Carry the value forward in the UI, or let the person see the earlier step without losing input.
**Overcorrection.** Repeating the whole summary on every step until the summary becomes the noise.

### `progressive-disclosure` Progressive Disclosure
**Claims.** Show what is needed now; reveal the rest on demand, in place, when asked for.
**Signal.** Every field, filter, setting or advanced option rendered up front; a settings screen with
no primary/advanced split; a form asking for data not needed until later; conversely, a required
field hidden behind a collapsed "advanced" section.
**Bar.** More than ~10 controls rendered at once with no primary/secondary split; or a required
control the person must expand something to find.
**Fix.** One layer of defaults with an "advanced" or "more options" affordance holding the rest;
ask for data at the step that needs it.
**Overcorrection.** Burying a frequent action one click deeper, or nesting disclosures inside
disclosures. Hidden ≠ simple; this is the law most often used to hide a design problem.

### `occams-razor` Occam's Razor
**Claims.** Remove elements until removing another would break the design; the simplest adequate
solution wins.
**Signal.** Confirmation dialogs on reversible actions; a field the system already knows (a value
derivable from another answer); duplicate entry (email twice, address twice); a step whose only
output is "next"; two components doing the same job on one screen.
**Bar.** Any step, field or dialog whose removal costs the person nothing — in particular a confirm
dialog guarding an action that is already undoable.
**Fix.** Delete the step; derive the value; replace the confirm with an undo.
**Overcorrection.** Removing a confirmation from something genuinely destructive and not replacing it
with undo, or stripping labels and affordances in the name of clean.

### `teslers` Tesler's Law (conservation of complexity)
**Claims.** Every process has irreducible complexity; the only question is who absorbs it — the
developer or the person.
**Signal.** The person doing work the system could do: typing a date in a required format, converting
units or currency, formatting a phone number, re-keying data the system holds, computing a total,
choosing between options the system could infer, resolving an id to a name by hand.
**Bar.** Any input whose required shape the system could accept, parse or infer instead. One case is a
**conformance failure, not a preference**: WCAG 2.2 SC 3.3.7 Redundant Entry (Level A) — "information
previously entered by or provided to the user that is required to be entered again in the same process
is either auto-populated, or available for the user to select", excepting only where re-entry is
essential, required for security, or the earlier value is no longer valid. A confirm-email field, an
address typed twice, or a reference the person carries between steps of one process is a Level A failure.
**Fix.** Move the work inward: parse flexibly, prefill from what is known, infer the default, compute
the total. See `postels`, which is this law applied to input.
**Overcorrection.** Hiding complexity the person must see — guessing a shipping address with no way
to correct it, or auto-resolving a conflict silently. Absorbed complexity must stay inspectable.

### `pareto` Pareto Principle
**Claims.** Most of the effect comes from a small share of the causes; invest where usage is.
**Signal.** Equal visual weight given to a rare action and the main one; the primary journey needing
more steps than an administrative one; heavy engineering on a path with no users.
**Bar.** The product's main journey is not the shortest or most prominent path in the interface.
**Fix.** Rank by actual usage; make the common path the default path.
**Overcorrection.** Removing the long tail outright — the 20% of features serving 80% of *revenue*
is a different 20%. Only a finding backed by real usage data belongs here; otherwise say so.

### `parkinsons` Parkinson's Law
**Claims.** Work expands to fill the time allowed. Applied to an interface: a flow with no bound — no
prefill, no defaults, no stated length — invites more time and attention than it needs. The law does not
predict that stating a shorter time speeds completion; it is a reason to bound the work, not an effect size.
**Signal.** Open-ended flows with no bounds: no autofill, no saved defaults, no estimate, no limit;
also fake delays added to make work feel substantial.
**Bar.** A flow whose common case could be completed by prefill but is not.
**Fix.** Prefill, autocomplete, remember, and state an expected duration ("about 2 minutes").
**Overcorrection.** Artificial countdowns and urgency timers on a decision that is not time-bound.

### `asymmetric-choice` Asymmetric choice (deceptive patterns)
**Claims.** Not a perceptual law and not on lawsofux.com — a pattern class, kept here because it is the
most code-visible thing in the list and because three other entries point at it (`choice-overload`'s
"pre-selecting the most expensive one", `von-restorff`'s "isolating the option that profits the business",
`parkinsons`' urgency timers). Where accepting is easy and declining is hard, the interface has made the
choice, not the person. Unlike the laws, this one has regulatory teeth: EU DSA Art. 25 and FTC enforcement.
**Signal.** `defaultChecked` or `checked` on a marketing, data-sharing or upsell consent; a decline
rendered as a text link against a filled accept button; a signup route with no symmetric cancellation
route; a hard-coded countdown or a "3 people are viewing" figure with no source; a pre-ticked add-on in a
total; an unsubscribe that needs a login; consent stored as opt-out.
**Bar.** Any consent defaulting to on, any accept/decline pair with unequal prominence, any urgency figure
with no real quantity behind it, any subscribe route whose cancellation route has more steps.
**Fix.** Default consent to off; give accept and decline the same weight; make cancelling as short as
signing up; delete any figure you cannot derive from real data.
**Overcorrection.** Calling every default a dark pattern. A default that serves the person (remember this
device, the shipping option most people need) is good design; the test is who the default benefits when
they disagree.

---

## Lens B — Form, grouping and hierarchy

What the eye groups and ranks before anything is read. The Gestalt laws are about perception, so they
resolve in rendered output; in source they show up as spacing, borders, and style reuse.

### `proximity` Law of Proximity
**Claims.** Objects near each other are perceived as a group, however they are styled.
**Signal.** Label-to-control distance larger than control-to-next-control; help text nearer the next
field than its own; an error message not adjacent to the input it concerns; icon-and-text pairs with
more gap than the pairs have between them; uniform spacing where grouping was intended.
**Bar.** Any related pair whose gap is ≥ the gap to the nearest unrelated element.
**Fix.** Tighten within the group, widen between groups; use the spacing scale's steps, not one value.
**Overcorrection.** Cramming until the group has no internal breathing room.

### `similarity` Law of Similarity
**Claims.** Elements sharing colour, shape, size or orientation read as one kind of thing.
**Signal.** Two different actions styled identically (a destructive and a safe button in the same
variant); a non-interactive element styled like a link or a button; links that are not visually
distinguishable from body text; the same semantic action styled differently on two screens.
**Bar.** Styling that makes different kinds look the same, or the same kind look different — either
direction is a finding.
**Fix.** One variant per kind of action; keep interactive affordances distinct from static text.
**Overcorrection.** A new variant per instance, which destroys the signal entirely.

### `common-region` Law of Common Region
**Claims.** A shared boundary (border, background, card) groups what it contains, overriding proximity.
**Signal.** Controls inside a card that belong to another card's content; a sticky footer action
visually inside the wrong region; a modal whose actions sit outside its surface; an element appearing
in one card but affecting another; nested cards with no boundary distinction.
**Bar.** Any control whose enclosing region differs from what it acts upon.
**Fix.** Put the action inside the region it affects; one visual container per concept.
**Overcorrection.** Boxing every element until the page is a grid of borders.

### `praegnanz` Law of Prägnanz
**Claims.** The eye resolves ambiguous form into the simplest reading available.
**Signal.** Layouts with ambiguous reading order (two plausible columns-vs-rows readings); decorative
complexity where a plain shape would do; icon sets whose silhouettes do not read at size.
**Bar.** A layout whose intended order is not the simplest available reading.
**Fix.** Simplify to one obvious structure; let order follow the grid.
**Overcorrection.** Flattening to the point that nothing is distinguishable (see `visual-hierarchy`).

### `uniform-connectedness` Law of Uniform Connectedness
**Claims.** Elements joined by a visible connector (a line, an arrow, a shared container) read as
more related than mere proximity makes them.
**Signal.** Step indicators with no connector between steps; related rows with no rule between them;
a legend not connected to its series; a tree view with no indentation guides.
**Bar.** A sequence or relation the design asserts but draws no connection for.
**Fix.** Draw the connection — connector lines, shared container, matched colour.
**Overcorrection.** Connector chrome on items that have no relation.

### `visual-hierarchy` Visual Hierarchy
**Claims.** Size, weight, colour and position tell the eye what matters before reading starts. Not one of
Yablonski's laws; the standard treatment is Lidwell, Holden & Butler's *Universal Principles of Design*
and NN/g's work on scanning patterns.
**Signal.** Heading levels skipped or used for size (`h4` as a big label); more than one element
competing for primary emphasis; a type scale with many near-identical sizes; the most important
action styled as the weakest on the screen; emphasis carried by colour alone.
**Bar.** More than one primary emphasis per screen, heading order broken, or the main action not the
most prominent one.
**Fix.** One primary per screen; headings by level, size by scale step; emphasis in two channels
(weight and colour), never colour alone.
**Overcorrection.** Shouting — three sizes of bold, or a hero on every section.

### `von-restorff` Von Restorff Effect (isolation effect)
**Claims.** The item that differs from its neighbours is the one remembered.
**Signal.** Every card marked "popular"; every button in the accent colour; a destructive action
indistinguishable from its neighbours; the one genuinely different item not marked at all; emphasis
expressed only by colour (fails for colour-blind and greyscale readers).
**Bar.** More than one isolated element per group, or no isolation where one option genuinely differs.
**Fix.** Isolate exactly one thing per group, in more than one channel.
**Overcorrection.** Isolating the option that profits the business rather than the one that fits.

### `selective-attention` Selective Attention
**Claims.** People filter out what looks like what they came to ignore — banner blindness is the
best-documented case.
**Signal.** Important content in a banner, an aside or a top strip; essential messages styled as
promotion; a "notice" in the position ads occupy; an empty-state instruction styled as marketing.
**Bar.** Anything required to complete the task sitting in advertising position or styling.
**Fix.** Put necessary information in the content flow, adjacent to the control it concerns.
**Overcorrection.** Interrupting with a modal to force attention.

### `aesthetic-usability` Aesthetic-Usability Effect
**Claims.** People perceive attractive interfaces as more usable, and will tolerate minor problems in
one — which also means polish *masks* problems in testing.
**Signal.** Visual inconsistency with the product's own design system (off-scale spacing, one-off
colours, mixed corner radii, mixed icon families, non-token values hard-coded); and the inverse —
a highly polished surface whose feedback, error and empty states are unstyled or missing.
**Bar.** Hard-coded values where the design system has a token; or a screen whose happy path is
designed and whose error/empty/loading states are not.
**Fix.** Use tokens; design the unhappy states to the same standard as the happy one.
**Overcorrection.** Polishing instead of fixing. Never cite this law to defer a usability finding —
its practical warning is that beauty hides problems, so a pretty screen deserves *more* scrutiny.

---

## Lens C — Reach and response

The physical and temporal cost of acting, and whether the system answers.

### `fitts` Fitts's Law
**Claims.** Time to hit a target grows with distance and shrinks with size: MT = a + b·log₂(2D/W).
**Signal.** Computed hit area of interactive elements; gap between a primary and a destructive
action; position of primary actions on small viewports; icon-only buttons at default icon size;
close buttons; table-row actions; elements near but not at a screen edge.
**Bar.** A target under 24×24 CSS px fails WCAG 2.2 SC 2.5.8 (AA) **only if it also fails the Spacing
exception**: centre a 24 px-diameter circle on its bounding box, and the failure is that circle
intersecting another target's box or another undersized target's circle. Apply all five exceptions —
Spacing, Equivalent, Inline, User Agent Control, Essential — before reporting. A conformance failure is
`must`; where an exception applies, an undersized target is at most a `should` on Fitts's own grounds,
never a conformance claim. Under 44×44 on touch is below Apple HIG and WCAG SC 2.5.5, which is AAA —
`should`. A primary action outside comfortable thumb reach on a phone layout — `should`.
**Fix.** Grow the hit area (padding or a pseudo-element) without growing the visual; separate
destructive from confirming; move primary actions within reach; use screen edges and corners, which
are effectively infinite targets, for frequent ones.
**Overcorrection.** Oversized targets that eat the layout, or invisible hit areas that overlap each
other so the wrong one fires. Claiming a conformance failure without running the circle test is the
commonest way to produce a `must` finding that is not true.
**Related.** Dragging along a constrained path — a nested submenu needing diagonal traversal, a 4 px
slider track — is the steering law (Accot & Zhai 1997) rather than Fitts, but it is reported as `fitts`:
the fix (widen the path, or remove the traversal) is the same and a second id would split the findings.
**Two more AA bars reported here, both conformance rather than preference.**
*WCAG 2.2 SC 2.5.7 Dragging Movements (AA)*: "all functionality that uses a dragging movement for
operation can be achieved by a single pointer without dragging, unless dragging is essential or the
functionality is determined by the user agent". Signal: `draggable`, `onDragStart`, drag-and-drop
libraries, `onMouseMove`-driven sliders, swipe-to-delete, reorder handles — each with no click, tap or
keyboard equivalent. A slider with no arrow-key support and no numeric input fails.
*WCAG 2.2 SC 2.4.11 Focus Not Obscured, Minimum (AA)*: a focused component must not be *entirely*
hidden by author content. Signal: `position: sticky` or `fixed` headers, footers, cookie bars and
toolbars with no `scroll-margin-top`/`scroll-padding-top` on focusable content — tabbing lands behind
the bar. This is the keyboard twin of the occlusion check in the rendered lane.

### `doherty` Doherty Threshold
**Claims.** Attention holds when the system answers in under 400 ms; Nielsen's limits add shape —
0.1 s feels instantaneous, 1 s keeps the flow of thought, 10 s loses attention entirely.
**Signal.** `await`ed calls with no pending state; submit handlers that neither disable nor indicate;
mutations without optimistic update where safe; search or filter inputs with no debounce; route
transitions with no skeleton; animations and transitions on an interaction path longer than ~400 ms;
work on the main thread or on boot; spinners used for sub-100 ms operations.
**Bar.** Any user-initiated async action with no visible state change within 400 ms. Any interaction
animation over 400 ms. Any wait over 1 s with no indicator, or over 10 s with no estimate or
ability to leave.
**Fix.** Immediate acknowledgement, then a skeleton that matches the eventual layout; optimistic
update where it can be reverted; debounce input, not feedback; keep interaction animation in the
150–300 ms range.
**Overcorrection.** A spinner on a 50 ms action (which reads as slower than nothing), or an
artificial delay to make work feel valuable where the person is waiting on their own task.

### `feedback-loops` Feedback Loops (visibility of system status)
**Claims.** Every action gets a reaction; the person should always know what the system is doing and
what happened, without asking.
**Signal.** A mutation whose success produces no message, no state change and no navigation; a
`catch` that swallows (`catch {}`, `except: pass`, `.catch(() => {})`) or that logs only to console;
validation that fires only on submit; destructive actions with no undo; long jobs with no progress;
state changes announced visually but not to assistive technology (no `aria-live`, no focus move);
forms whose content is lost on a failed submit.
**Bar.** Any state-changing action with no user-visible outcome; any swallowed error on a user path;
any destructive action with neither confirmation nor undo; any error that discards the person's input.
**Fix.** Confirm success in place, keep input on failure, say what happened and what to do, prefer
undo over confirm, move focus to what changed, announce it. Where the action came from a suggestion the
system made, dismissing it must stick and correcting it must be cheaper than redoing the work by hand
(HAX 8, 9, 15); see `ai-legibility`.
**Overcorrection.** A toast for every keystroke, or confirmation dialogs stacked on confirmations.

### `paradox-active-user` Paradox of the Active User
**Claims.** People start using the product immediately and never read the documentation — even when
reading would be faster.
**Signal.** Onboarding that depends on a tour, a video or a docs link; empty states with no next
action; features whose only explanation is in a help centre; keyboard shortcuts documented nowhere
in the UI; errors that link to docs instead of saying what to do.
**Bar.** Any task whose completion requires reading something outside the interface.
**Fix.** Teach in place at the moment of need; make empty states the instructions; put the next
action in the error.
**Overcorrection.** Coach marks and tooltips on every control, which is documentation wearing a hat.

### `error-prevention` Error Prevention
**Claims.** Nielsen's fifth heuristic: the best error message is the one never needed. Distinct from
`feedback-loops` (recovering after the fact) and `postels` (tolerating odd input) — the finding here is
that the wrong state was reachable at all.
**Signal.** A mutation with no double-submit guard and no idempotency key; a payment or booking that can
be posted twice; a genuinely irreversible action behind a one-tap button or a plain confirm rather than a
typed confirmation; a future-only date field that accepts a past date; validation only on the server, so
the person learns after submitting; a destructive default (delete as the primary, Enter submitting a
destructive form); units or currency chosen after the amount is typed.
**Bar.** Any irreversible action reachable without a deliberate second act; any mutation that can be
submitted twice; any constraint the system knows and does not apply until after submission; and any
outward-facing or irreversible action taken from generated output with no review step (`ai-legibility`).
**Fix.** Disable on submit and make the write idempotent; constrain the input rather than validating it
(a date field that cannot select the past); require typing the name for the irreversible case; validate
on the client as well as the server, and never only the client.
**Overcorrection.** A confirm dialog on everything, which trains the reflex that defeats it — use undo
where the action is reversible, and reserve friction for what cannot be undone.

---

## Lens D — Expectation and memory

What the person already knows, and what the interface makes them know.

### `jakobs` Jakob's Law
**Claims.** People spend most of their time on other products, so they expect yours to work like those.
**Signal.** Reimplemented native controls (custom `select`, checkbox, date picker, file input) that
drop keyboard, form or platform behaviour; conventional elements in unconventional places (logo not
linking home, cart elsewhere than top-right on a shop, nav at the bottom on desktop); icons with
non-standard meanings; links that are not `<a>` and buttons that are not `<button>`; the browser Back
button or deep links broken by client-side state; non-standard gestures or shortcuts (overriding
⌘F, ⌘S); platform conventions ignored (iOS back-swipe, Android back button, native share sheet).
**Bar.** Any control that re-implements a native behaviour without matching it, any broken back/deep
link, any platform affordance overridden without an equivalent. Where help lives is a conformance bar:
WCAG 2.2 SC 3.2.6 Consistent Help (Level A) requires that human contact details, a human contact
mechanism, a self-help option or a fully automated contact mechanism, when repeated across pages,
"occur in the same order relative to other page content". Signal: a help, chat or contact entry point
present in the header on some routes and in the footer or nowhere on others.
**Fix.** Use the native element; when a custom one is unavoidable, match its full keyboard, focus,
form and assistive behaviour; keep conventional things in conventional places.
**Overcorrection.** Copying a competitor's layout wholesale, or refusing a genuinely better pattern
because it is new. Convention is the default, not the ceiling — deviate deliberately and say why.

### `recognition-recall` Recognition over Recall
**Claims.** Recognising is cheaper than recalling; keep options, instructions and prior input visible.
**Signal.** Placeholder text used as the only label (disappears on focus); labels that vanish on
input; inputs without `autocomplete` attributes; codes, ids or references the person must carry
between screens or re-type; search with no history or suggestions; icon-only controls with no
accessible name and no tooltip; a "previously used" value that is not offered.
**Bar.** Any input whose label is a placeholder only, any icon-only control with no accessible name,
any value the person must retype that the system already holds (Level A under SC 3.3.7 — see `teslers`).
Authentication is its own conformance bar: WCAG 2.2 SC 3.3.8 Accessible Authentication (Level AA)
forbids a *cognitive function test* — "a task that requires the user to remember, manipulate, or
transcribe information" — at any step, unless an alternative, an assisting mechanism, object
recognition, or user-provided non-text content is offered. In code that means: `autocomplete="off"` or
a wrong token on a login field, a blocked paste (`onPaste` preventDefault, `onCopy` blocked), a puzzle
CAPTCHA, or a one-time code that must be transcribed by hand. Password managers must work.
**Fix.** Persistent visible labels; `autocomplete` tokens; offer prior values; name every icon.
**Overcorrection.** Suggestion lists so eager they obscure the field, or autofilling a value the
person must then hunt down and correct.

### `mental-model` Mental Model
**Claims.** People act on a compressed model of how the system works; mismatch between that model and
the implementation is where errors come from.
**Signal.** Domain vocabulary that differs between UI, API and docs for the same concept; state the
UI calls one thing and the backend another; a "save" that queues rather than saves; "delete" that
archives; a toggle whose off position still collects data; counts that differ between two screens;
an action whose scope is wider than its label (deleting a folder deleting its shares).
**Bar.** Any label whose behaviour differs from what the word means, or one concept named two ways in
one product.
**Fix.** Rename to the truth or change the behaviour to the name; one word per concept across UI,
API, docs and support.
**Overcorrection.** Renaming established vocabulary mid-product, which breaks the model it fixes.

### `postels` Postel's Law (robustness principle)
**Claims.** Be conservative in what you send, liberal in what you accept — applied to input, the
interface should accept anything a person could reasonably mean.
**Signal.** Input validation regexes: phone numbers rejecting spaces, brackets or `+`; card numbers
rejecting spaces; postcodes case- or space-sensitive; emails rejecting `+`, subaddressing, long TLDs
or non-ASCII; names rejecting apostrophes, hyphens, spaces or non-Latin characters; dates in one
format only; URLs requiring a scheme; `maxlength` shorter than real values; input not trimmed;
required fields that are not actually required; validation that blocks typing rather than reporting
on blur.
**Bar.** Any validation that rejects a valid real-world value, or that could normalise instead of
reject. Any name field with a character class restriction. Any email check stricter than "has an @
with something either side" plus a send.
**Fix.** Normalise then validate — strip spaces, trim, case-fold the domain, parse flexible dates,
infer the scheme. Validate on blur, not on keystroke. Keep output strict.
**Overcorrection.** Accepting garbage and storing it unnormalised, or silently "correcting" a value
into something the person did not mean. The law is about what you *emit* — liberal in what you accept,
conservative in what you send — so normalise on the way in and keep one shape in storage.

### `ai-legibility` AI legibility
**Claims.** Not a law of perception and not on lawsofux.com — the established heuristics for interfaces
whose output is generated rather than authored, from Microsoft's *Guidelines for Human-AI Interaction*
(Amershi et al., CHI 2019) and Google's People + AI Guidebook. Kept as one entry rather than eighteen,
because only a handful are visible in source. Its claim: a generated answer carries no inherent signal
of what produced it, how reliable it is, or what it drew on, so the interface must supply all three —
otherwise the person's mental model of the feature is built from a confident sentence.
**Signal.** A model call whose output is rendered with no indication it was generated (HAX 1); no
statement of what the feature can and cannot do at the point of use, only in marketing (HAX 1); no
confidence, uncertainty or "this may be wrong" treatment anywhere, and no distinction between a
retrieved fact and a generated one (HAX 2); no citation, source or provenance beside a claim (HAX 11);
generated output written into a record, a message or a file with no review step (HAX 9, 16); no way to
edit, regenerate or reject a suggestion (HAX 9); a suggestion that cannot be dismissed, or that
reappears after dismissal (HAX 8); a streaming response with no stop control; an error, refusal,
timeout, filter or empty result with no designed state; no route to report a bad answer (HAX 15); a
prompt or system message rendered to the person as if it were their own content.
**Bar.** Any generated output presented without a marker that it is generated. Any irreversible or
outward-facing action taken from generated output with no review step. Any suggestion that cannot be
dismissed or corrected. Any failure, refusal or empty state with no designed screen.
**Fix.** Mark generated content; say at the point of use what the feature does and how it fails; show
sources beside claims; make review the default before anything leaves the product; let a suggestion be
edited, regenerated, rejected and stay rejected; design the refusal and the timeout.
**Overcorrection.** A disclaimer banner on every surface, which people stop reading within a session —
that is `selective-attention` reintroduced. Mark the output, not the product. Equally, do not treat a
confidence number as legibility: a percentage nobody can calibrate is noise, not provenance.
**Scope.** Only where the repository actually ships a model-backed user-facing feature. A library that
calls an API is not an AI surface; a chat panel, an autocomplete, a summariser or a generated draft is.

---

## Lens E — Journey and ending

Laws that only appear across more than one screen.

### `goal-gradient` Goal-Gradient Effect
**Claims.** Effort increases as a visible goal gets closer — and artificial early progress helps
(the endowed-progress effect: a 10-stamp card with 2 stamps free beats an 8-stamp card).
**Signal.** Multi-step flows with no step indicator or no total; progress that cannot be seen;
checkout or onboarding where the number of remaining steps is unknown; a progress bar that starts
at zero when some work is already done (account exists, email verified).
**Bar.** Any flow of 3+ steps with no visible position and total.
**Fix.** Show "step 2 of 4"; credit work already done; never add steps to make a bar look fuller.
**Overcorrection.** Fake or non-monotonic progress, or splitting one step into three to show movement.

### `serial-position` Serial Position Effect
**Claims.** First and last items in a series are recalled best; the middle fades.
**Signal.** Order of nav items, menu entries, toolbar actions, list columns, onboarding steps,
settings rows; the most important action sitting in the middle; alphabetical ordering of a
functional menu.
**Bar.** The primary and the exit/most-used actions not at the ends of their series.
**Fix.** Put the most important at the start and the most used at the end; order by use, not
alphabet, unless the list is looked up by name.
**Overcorrection.** Reordering a list people have memorised.

### `peak-end` Peak-End Rule
**Claims.** An experience is remembered by its most intense moment and its end, not its average.
**Signal.** Flows that end on a blank screen, a redirect to home, or nothing; a successful payment
with no receipt or confirmation; destructive-feeling peaks (data loss on error, a scary dialog, a
bare 500 page); unhandled error boundaries; cancellation and deletion flows with no acknowledgement;
no empty-state design on first run.
**Bar.** Any completed journey with no explicit, designed end state; any error state on a main path
rendered by a default framework page.
**Fix.** Design the last screen of every flow and the worst screen of every flow first.
**Overcorrection.** Confetti on a routine save, which spends the peak on nothing.

### `zeigarnik` Zeigarnik Effect
**Claims.** Interrupted or incomplete tasks stay in mind, and a visible incompleteness pulls toward
completion.
**Signal.** No draft saving, no resume, no "continue where you left off"; a flow abandoned mid-way
losing everything; a profile with no completeness indicator; notifications that mention incomplete
work with no route back to it.
**Bar.** Any multi-step or long-form flow with no persisted partial state.
**Fix.** Persist drafts, offer resume, show what remains.
**Overcorrection.** Nagging about incompleteness the person has chosen, or a completeness meter that
can never reach 100%.

---

## Not laws, but load-bearing

These are not on lawsofux.com and are not reported as law findings, yet they decide whether a law
finding is true. A reviewer checks them as part of the lens that needs them.

- **Target size exceptions.** WCAG SC 2.5.8 has five, and they must all be applied before `fitts` is
  reported as a conformance failure. **Spacing**: a 24 px-diameter circle centred on the undersized
  target's bounding box does not intersect another target's box or another undersized target's circle —
  this is how dense interfaces legitimately conform, and it is the measurement to run.
  **Equivalent**: another control on the same page does the same thing and does meet the size.
  **Inline**: the target sits in a sentence or a block of text. **User Agent Control**: the browser
  decides the size and the author has not changed it. **Essential**: the presentation is legally required
  or essential to the information. SC 2.5.5's 44×44 is AAA, not a conformance baseline.
- **Contrast.** Emphasis and isolation claimed in colour only (`von-restorff`, `visual-hierarchy`)
  must also survive greyscale and the 4.5:1 / 3:1 WCAG contrast bars.
- **Reduced motion.** Any animation finding assumes `prefers-reduced-motion` is honoured; if it is
  not, that is the finding.
- **Keyboard and focus.** Jakob's and feedback findings about custom controls are usually keyboard
  and focus findings first: focus order, visible focus ring, focus moved to what changed, Escape
  closing what opened.
- **Internationalisation.** Postel's and Miller's findings about formats presume a locale; a format
  claim that holds only for one country is a finding against the format, not the person.

## Sources

Every figure quoted above traces to one of these. Where a bar says "convention", there is no source and
the file says so rather than borrowing authority from a neighbouring study.

- [lawsofux.com](https://lawsofux.com/) — Jon Yablonski, the canonical collection and the source of
  most statements and takeaways above.
- The primary work behind the laws, where the body names a study: Hick 1952 and Hyman 1953 (choice
  reaction time); Fitts 1954 for `MT = a + b·log₂(2D/W)`, with MacKenzie's 1992 Shannon form
  `MT = a + b·log₂(D/W + 1)` the one in current HCI use; Miller 1956 (seven chunks) and Cowan 2001
  ("the magical number four"); Doherty & Thadani 1982 (the 400 ms figure, IBM Systems Journal);
  Iyengar & Lepper 2000 and Scheibehenne, Greifeneder & Todd 2010 (the jam study and its near-zero
  meta-analytic mean); Nunes & Drèze 2006 (endowed progress, 34% vs 19%); Kurosu & Kashimura 1995 and
  Tractinsky 1997 (aesthetic-usability); Carroll & Rosson 1987 (the active user paradox);
  Zeigarnik 1927; von Restorff 1933; Kahneman & Redelmeier on peak-end; Accot & Zhai 1997 (steering).
- [Nielsen, Response Time Limits](https://www.nngroup.com/articles/response-times-3-important-limits/)
  — the 0.1 / 1 / 10 second limits.
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/) — SC 2.5.8 Target Size (Minimum), 24×24 CSS px and its five
  exceptions, and SC 2.5.5 (AAA) for 44×44; and the criteria new in 2.2 that this file reports under
  existing laws: [3.3.7 Redundant Entry](https://www.w3.org/WAI/WCAG22/Understanding/redundant-entry.html) (A),
  [3.2.6 Consistent Help](https://www.w3.org/WAI/WCAG22/Understanding/consistent-help.html) (A),
  [2.5.7 Dragging Movements](https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements.html) (AA),
  [2.4.11 Focus Not Obscured (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html) (AA),
  and [3.3.8 Accessible Authentication (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/accessible-authentication-minimum.html) (AA).
- [Guidelines for Human-AI Interaction](https://www.microsoft.com/en-us/research/publication/guidelines-for-human-ai-interaction/),
  Amershi et al., CHI 2019 — the 18 HAX guidelines, and Google's
  [People + AI Guidebook](https://pair.withgoogle.com/guidebook/) — the source of `ai-legibility`.
- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
  — 44×44 pt controls; [Material Design](https://m3.material.io/) — 48×48 dp.
- [Nielsen's 10 usability heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/) —
  the source of visibility of system status (heuristic 1, `feedback-loops`), user control and freedom
  (3, the undo-over-confirm rule), consistency and standards (4, `jakobs`), error prevention
  (5, `error-prevention`), recognition rather than recall (6, `recognition-recall`), error recognition
  and recovery (9, `feedback-loops` and `cognitive-load`) and match with the real world (2, `mental-model`).
- [Universal Principles of Design](https://en.wikipedia.org/wiki/Universal_Principles_of_Design),
  Lidwell, Holden & Butler — the standard treatment of `visual-hierarchy`, which is not a Yablonski law.
- [EU Digital Services Act Art. 25](https://eur-lex.europa.eu/eli/reg/2022/2065/oj) and the FTC's
  dark-patterns enforcement — the only entry here (`asymmetric-choice`) that is law in the other sense.
