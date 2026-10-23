# Signals: finding the laws in source

A UX law is a claim about a rendered interface, and an audit of a repository reads source. This file
is how to bridge that gap: what to grep for, how to compute a number from code, and — most
importantly — when source is not enough and the finding must be downgraded or measured.

## 0. The three evidence grades

Every finding carries one. The verify phase rejects a finding whose claim outruns its grade.

| Grade | Means | Example |
|---|---|---|
| `certain` | The source states the fact outright. | A regex that rejects `+` in an email; `catch {}` on a mutation path; a `maxlength="10"`; a missing `<label>`; a 900 ms transition. |
| `computed` | Derived from source by arithmetic over tokens or the style graph. | Hit area = `padding` + `font-size × line-height` + `border`, resolved through the theme. |
| `needs_measurement` | Depends on how the component is composed, themed or overridden at runtime. | "The primary action is below the fold on a phone"; "these two items read as one group". |

`certain` may be reported as a fact. `computed` must show its arithmetic. `needs_measurement` is never reported as a
fact: it names the one measurement that would settle it. A measured value promotes it to `certain`, or refutes it;
nothing else does, and silence promotes nothing. These three names are the whole vocabulary — the schema accepts no
others.

## 1. Find the interface first

Before any law, locate what the person actually sees. In order:

```sh
git ls-files | grep -Ei '\.(tsx|jsx|vue|svelte|astro|html|htm|erb|haml|slim|blade\.php|hbs|twig|razor|cshtml|swift|kt|dart|xml|ui|qml|templ)$'
git ls-files | grep -Ei '(tailwind|theme|tokens|design-system|styles?|_variables|global)\.(js|ts|css|scss|json|yaml)$'
git ls-files | grep -Ei '(routes?|pages?|screens?|views?|app)/' | head -50
git ls-files | grep -Ei '(en|en-US|locales?|i18n|messages|strings)\.(json|ya?ml|ftl|arb|strings)$'
```

Then map **screens**, not files. A screen is what a person has in front of them at one moment: a
route, a modal, a step, a tab panel, a CLI subcommand's output. The audit shards by screen and flow
because that is the unit every law is about. One file can hold three screens; one screen can span
twelve files.

Exclude from scope, and say so: Storybook stories, visual-test fixtures, `__mocks__`, generated
clients, vendored code, admin tools with no end users, and any component with no path from a route
(dead UI is not a UX finding — see the `reach` check).

## 2. Per-stack: where the signal lives

| Stack | Interactive elements | Styles and spacing | Async and feedback | Labels and text |
|---|---|---|---|---|
| React / Next / Remix | `<button>`, `onClick` on non-buttons, `role=`, custom `Button`/`IconButton` | Tailwind classes, `styled-components`, CSS modules, `sx=`, theme file | `useEffect` + fetch, React Query/SWR (`isPending`, `isLoading`), server actions, `useTransition`, Suspense boundaries, error boundaries | JSX text, `aria-label`, `placeholder`, i18n keys |
| Vue / Nuxt | `<button>`, `@click`, `v-on` on `div`, UI-kit components | `<style scoped>`, Tailwind, theme `.scss` | `async setup`, `useFetch` (`pending`), `<Suspense>` | template text, `:aria-label` |
| Svelte / SvelteKit | `<button>`, `on:click`, actions | `<style>`, Tailwind, `app.css` | `{#await}` blocks, `load`, form actions (`$page.form`), `enhance` | markup text, `aria-*` |
| Angular | `(click)`, `mat-*`, CDK overlays | component `.scss`, Material theme | RxJS subscriptions, `async` pipe, interceptors | template text, `i18n` |
| Plain HTML / server-rendered (Rails, Django, Laravel, Go templates) | `<button>`, `<a>`, `<input type=submit>` | linked stylesheets, framework CSS | full-page form posts, `hx-*` (htmx `hx-indicator`, `hx-swap`) | template text, `<label for>` |
| SwiftUI | `Button`, `.onTapGesture`, `NavigationLink` | `.frame`, `.padding`, `.font`, `Spacing` enums | `async`/`await` in `.task`, `@State isLoading`, `ProgressView` | `Text`, `.accessibilityLabel`, `Localizable.strings` |
| UIKit | `UIButton`, `addTarget`, gesture recognisers | Auto Layout constants, `.xib`/storyboard frames | completion handlers, `UIActivityIndicatorView` | `setTitle`, `accessibilityLabel` |
| Android / Compose | `Button`, `clickable`, `onClick` | `Modifier.size/padding`, `dimens.xml`, `MaterialTheme` | coroutines, `collectAsState`, `LinearProgressIndicator` | `stringResource`, `contentDescription` |
| Flutter | `GestureDetector`, `InkWell`, `*Button` | `EdgeInsets`, `SizedBox`, `ThemeData` | `FutureBuilder`, `setState` loading flags | `Text`, `Semantics(label:)` |
| Electron / Tauri | as web, plus menus and tray | as web | IPC round trips with no pending state | menu labels, `aria-*` |
| CLI / TUI | flags, subcommands, prompts | n/a | progress to stderr, spinners, `--quiet` | `--help` text, error strings |

## 3. Computing hit area (Fitts) without rendering

Resolve, in this order, and show the arithmetic in the finding:

1. Explicit size: `width`/`height`, `w-6 h-6`, `.frame(width:height:)`, `Modifier.size()`, `SizedBox`.
2. Padding plus content: `padding` (all four sides) + content box. Content box for an icon is the
   icon's own size (`size-4` = 16 px, `w-5` = 20 px, SF Symbol at `.font(.body)` ≈ 17 pt); for text it
   is `font-size × line-height`.
3. Tailwind scale: `1` unit = `0.25rem` = 4 px at the default root; check `tailwind.config` for an
   overridden `spacing` scale before assuming it.
4. Minimum-size rules: `min-h-*`, `min-height`, a base `Button` class, a platform default
   (`UIButton` 44 pt; Material `Button` 48 dp; HTML `<button>` has no minimum).
5. Inherited component defaults: read the shared `Button`/`IconButton` once and reuse its computed
   size for every call site that does not override it. One finding on the shared component beats
   forty on its call sites.

Examples:

```
<button class="p-1"><Icon class="size-4" /></button>      → 4+16+4 = 24 px   → meets AA, fails AAA/touch
<button class="p-2"><Icon class="h-4 w-4" /></button>     → 8+16+8 = 32 px   → fails 44 on touch
<IconButton size="sm"> with sm = padding 2px, icon 16     → 20 px           → fails AA  (must)
Image(systemName:).frame(width: 20, height: 20)           → 20 pt           → fails 44  (must on iOS)
```

Pseudo-element and `::after` hit-area expanders, `hitSlop`, `.contentShape(Rectangle())` with a
larger frame, and `Modifier.minimumInteractiveComponentSize()` all count — look for them before
reporting, and record the grade as `computed`.

Anything depending on a runtime theme, a container query, or a prop the call site passes is
`needs_measurement` and goes to the rendered lane.

## 4. Greppable certainties

These are `certain` from source alone. Tune the pattern to the stack; the point is the class of thing.

```sh
# feedback-loops: swallowed errors on a user path
grep -rnE 'catch\s*\(?[a-z_]*\)?\s*\{\s*\}|\.catch\(\s*\(\)\s*=>\s*\{?\s*\}?\s*\)|except[^:]*:\s*pass|catch \{ \}' --include='*.ts*' --include='*.js*' --include='*.py' --include='*.swift'
grep -rn 'console\.\(log\|error\)' <ui-dirs> | grep -i 'catch\|error'      # logs instead of telling the person

# postels: validation that rejects real values
grep -rnE "pattern=|RegExp\(|\.test\(|matches\(|NSPredicate|\\\\d\{|[\"'/]\^.*\\\$[\"'/]" <ui-dirs>
grep -rniE 'maxlength|maxLen|\.max\(([0-9]{1,2})\)' <ui-dirs>              # short caps on names, phones, addresses
grep -rniE '[a-z]+@[a-z]+\\\\.[a-z]|\[a-zA-Z\]\+.*name|^\[A-Za-z \]' <ui-dirs>

# recognition-recall: placeholder as label, unnamed icon controls
grep -rn 'placeholder=' <ui-dirs> | wc -l ; grep -rn '<label\|aria-labelledby\|FormLabel' <ui-dirs> | wc -l
grep -rnE '<(button|Button|IconButton)[^>]*>\s*<(Icon|svg|[A-Z][a-zA-Z]*Icon)' <ui-dirs> | grep -v 'aria-label\|title=\|sr-only\|accessibilityLabel\|contentDescription'
grep -rn 'autoComplete\|autocomplete' <ui-dirs> | wc -l                    # compare with the input count

# doherty: async with no pending state, slow interaction animation
grep -rnE 'await |\.then\(' <ui-dirs> | grep -vi 'loading\|pending\|isSubmitting\|disabled\|Skeleton\|Spinner\|ProgressView\|optimistic'
grep -rnE 'duration-(5|7|10)[0-9]{2}|transition:[^;]*[0-9]{3,}ms|[0-9]\.[0-9]s|animation-duration' <ui-dirs>
grep -rniE 'prefers-reduced-motion|accessibilityReduceMotion|disableAnimations' <ui-dirs>   # absence is the finding

# jakobs: native behaviour re-implemented, or a click on a non-interactive element
grep -rnE '<div[^>]*onClick|<span[^>]*onClick|@click=.*<div|onTapGesture' <ui-dirs>
grep -rniE 'custom.?(select|dropdown|checkbox|radio|datepicker)|role="(button|listbox|combobox)"' <ui-dirs>
grep -rnE 'preventDefault\(\)' <ui-dirs> | grep -iE 'key|ctrl|meta|cmd'    # hijacked shortcuts

# hicks / progressive-disclosure: option counts
grep -c '<option' <file>; grep -c 'MenuItem\|DropdownMenuItem\|NavLink\|Tab ' <file>
grep -rn 'checked\|Switch\|Toggle' <settings-screens> | wc -l

# cognitive-load / mental-model: internal vocabulary in user-facing strings
grep -rniE '\b(uuid|guid|id:|_id|enum|null|undefined|NaN|500|4[0-9][0-9]|exception|stack|timeout|ECONN)\b' <i18n-or-template-text>

# visual-hierarchy: heading order, competing primaries
grep -rnoE '<h[1-6]' <ui-dirs> | sort | uniq -c
grep -rn 'variant="primary"\|btn-primary\|\.buttonStyle(\.borderedProminent)' <ui-dirs> | awk -F: '{print $1}' | uniq -c | sort -rn

# WCAG 2.2's newest criteria, all conformance rather than preference
# 3.3.7 Redundant Entry (A): the same value asked for twice in one process
grep -rniE 'confirm(_|-)?(email|password|address)|email2|retype|re-enter|verifyEmail' <ui-dirs>
# 3.3.8 Accessible Authentication (AA): a cognitive function test, a blocked paste, a defeated password manager
grep -rnE 'onPaste|onCopy|autocomplete="off"|autoComplete="off"|captcha|recaptcha|hcaptcha|puzzle' <auth-dirs>
grep -rn 'type="password"' <auth-dirs> | grep -v 'autocomplete\|autoComplete'
# 2.5.7 Dragging Movements (AA): drag-only operation with no single-pointer equivalent
grep -rniE 'draggable|onDrag(Start|End|Over)|dnd-kit|react-beautiful-dnd|sortablejs|swipe|onPanGesture|onMouseMove' <ui-dirs>
# 2.4.11 Focus Not Obscured (AA): sticky chrome with no scroll margin on what can take focus
grep -rnE 'position:\s*(sticky|fixed)|\bsticky\b|\bfixed (top|bottom)-' <ui-dirs>
grep -rniE 'scroll-margin|scroll-padding|scrollMarginTop' <ui-dirs>   # absence beside the above is the finding
# 3.2.6 Consistent Help (A): a help or contact entry point that moves or disappears between routes
grep -rniE 'help|support|contact us|live ?chat|intercom|zendesk' <layout-and-nav-files>

# ai-legibility: a model-backed surface and what it does or does not tell the person
grep -rniE 'openai|anthropic|@ai-sdk|langchain|bedrock|vertex|gemini|completion|chat\.|streamText|generateText|useChat' <src>
grep -rniE 'generated|ai-generated|may be (wrong|inaccurate)|double.?check|confidence|citation|source[s]?:|provenance' <ui-dirs>
grep -rniE 'dismiss|reject|regenerate|retry|stop generating|thumbs|feedback' <ai-ui-dirs>

# peak-end: designed endings and designed failures
git ls-files | grep -iE 'empty|zero-?state|not-?found|404|500|error-?(page|boundary)|success|confirmation|thank'
grep -rn 'ErrorBoundary\|error\.tsx\|\+error\.svelte\|rescue_from' <ui-dirs>

# aesthetic-usability: values bypassing the design system
grep -rnE '#[0-9a-fA-F]{3,8}\b|rgba?\(|[0-9]+px' <ui-dirs> | grep -v 'tokens\|theme\|variables' | wc -l
```

A grep result is a *candidate*, never a finding. Open the file, read the component and its call
sites, and confirm the person actually meets it.

## 5. Spacing and grouping from source (Gestalt)

Proximity, similarity and common region resolve visually, so from source they are `computed` at best:

1. Read the spacing scale (`tailwind.config`, `theme.spacing`, `_variables.scss`, `dimens.xml`,
   SwiftUI spacing constants). Note its steps.
2. For a group, list the gaps: label→control, control→help, control→next control, group→group. Use
   `gap-*`, `space-y-*`, `mt-*`, `margin`, `VStack(spacing:)`, `Modifier.padding`.
3. The finding is a *relation*, not a value: related gap ≥ unrelated gap. A number alone is never a
   proximity finding.
4. Common region needs the container: which element's border, background or card encloses the
   control, and does that container own what the control affects.
5. Similarity needs the variant map: which class or variant each action uses, and whether two kinds
   of action share one.

If the component composes spacing from props or a runtime theme, stop — that is `needs_measurement`, and the
rendered lane answers it.

## 6. Flows, which no single file holds

Lens E only exists across screens. Build the flow graph before reviewing it:

- Routes and their links: router config, `<Link>`/`href`/`NavigationLink` targets, redirects,
  `router.push`, guards and middleware.
- Steps: a wizard's state machine, step enums, `currentStep`, URL step params.
- Terminal states: where a successful flow lands, and whether that destination is designed.
- Persistence: localStorage, draft tables, autosave, `beforeunload` handlers, form libraries'
  persistence options.
- Server-side journeys: form posts, redirects after POST, flash messages.

Then for each flow of three or more steps, check: is position visible, is partial state persisted, is
the end state designed, is the worst state designed, where do the first and last items sit.

## 7. Non-GUI surfaces

A repository with no UI can still be audited — the laws apply wherever a person acts.

**CLI.** Flags per command (`hicks`), `--help` as the only discovery path (`paradox-active-user`),
no progress on a long job and no feedback on success (`doherty`, `feedback-loops`), strict argument
parsing that rejects `--foo=bar` or a trailing slash (`postels`), destructive commands with no
`--dry-run` and no confirmation (`feedback-loops`), inconsistent flag naming across subcommands
(`jakobs`), errors that print a stack instead of the next action (`cognitive-load`, `peak-end`),
ids the person must copy between commands (`working-memory`, `recognition-recall`).

**AI surfaces.** A chat panel, an inline autocomplete, a summariser, a generated draft or a "ask about
this" affordance. Trace the model call to the component that renders its output and ask what the render
carries: is the output marked as generated (`ai-legibility`), is there a source beside a claim, is there
a designed state for a refusal, a filter, a timeout and an empty result (`peak-end`), can a suggestion be
dismissed and does the dismissal stick (`feedback-loops`), can the output be edited or regenerated before
it is saved or sent (`error-prevention`), is there a stop control on a stream (`doherty`). Also check what
the model is told versus what the person is shown — a system prompt rendered as the person's own content
is a `mental-model` finding. A repository that merely calls a model API with no user-facing surface is
not an AI surface; say so rather than reviewing it.

**API and SDK as interface.** Required parameters that could be defaulted (`teslers`), strict request
validation (`postels`), error bodies with no actionable message (`feedback-loops`), naming that
differs from the product's own vocabulary (`mental-model`), breaking a convention of the ecosystem's
other clients (`jakobs`).

**Docs, email and notifications.** Peak-end on transactional mail (does the receipt confirm what
happened), recognition over recall (does the email carry the reference the next step needs),
selective attention (is the action buried under marketing).

Say in the report which surfaces the repository has. A library with no user-facing surface should
return no findings and say why, not manufacture them.

## 8. When source is not enough

Downgrade to `needs_measurement` and, if the app can be served, hand to the rendered lane
([rendered.md](rendered.md)). Always, for:

- Anything about what is above the fold, overlapping, or reachable by thumb.
- Actual contrast, since it depends on resolved theme values in both colour schemes.
- Real response times, which depend on data and network.
- Whether two elements read as one group.
- Anything behind a feature flag, an A/B split, a runtime theme or a tenant configuration.

Never guess at these from source. A claim at the wrong grade is the failure mode this skill is most
likely to produce.
