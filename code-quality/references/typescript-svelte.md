# TypeScript and Svelte

## Standards adopted

| Source | What to take from it |
|---|---|
| [ESLint](https://eslint.org/docs/latest/rules/) `recommended` | Correctness baseline, plus the core maintainability rules `complexity` (15), `max-depth` (4), `max-params` (4), `max-lines-per-function` (80). |
| [typescript-eslint](https://typescript-eslint.io/users/configs/) `strict` + `stylistic` | No `any`, no non-null `!`, no empty functions, `interface` for object shapes, `T[]` arrays. |
| [eslint-plugin-svelte](https://sveltejs.github.io/eslint-plugin-svelte/rules/) `recommended` | Keyed `{#each}`, `resolve()` for internal links, `SvelteMap`/`SvelteSet` for reactive collections, `$derived` over `$effect` writes. |
| [Svelte 5 docs](https://svelte.dev/docs/svelte/what-are-runes) | Runes (`$state`, `$derived`, `$props`), snippets instead of slots, shared reactive state in `.svelte.ts` modules. |
| [SvelteKit project structure](https://svelte.dev/docs/kit/project-structure) | `src/lib` (`$lib`) for shared code, `src/lib/server` for server-only modules, routes own their page-specific components. |

Each package should own its `eslint.config.js` and a `lint` script, so a gate
runs per component.

## Where code lives

- **Routes compose; they do not build.** `+page.svelte` reads `data`, holds
  page-level state, and lays out components. Each visual section with its own
  markup or state is a component in the route folder (`routes/billing/
  invoices/InvoiceTable.svelte`). Aim for a route under ~150 script+markup lines.
- **Components used by more than one route** live in `$lib/<domain>/`
  (`$lib/team/`, `$lib/billing/`), never loose in `src/lib` and never in a
  catch-all `$lib/components/`. Generic UI primitives get a domain of their own
  (`$lib/charts/`, `$lib/forms/`).
- **Logic leaves the component.** Formatting, filtering, sorting, date math,
  API calls and data shaping go in a `.ts` module beside the component (or a
  `.svelte.ts` module when it holds runes). Components keep wiring only; aim for a
  `<script>` under ~100 lines.
- **API access** goes through one typed client per domain (`$lib/billing/api.ts`),
  not `fetch` calls scattered through components.
- **Server-only code** (secrets, database) lives under `$lib/server/`.

## Svelte idioms

- `$derived` for anything computed; `$effect` only for real side effects (DOM,
  timers, subscriptions), never to copy one state into another.
- Props via `let { a, b }: Props = $props();` with a named `interface Props`.
- Snippets (`{#snippet}` / `{@render}`) for repeated markup within a component;
  a separate component once the markup has its own state or exceeds ~40 lines.
- Every `{#each}` has a key: `{#each items as item (item.id)}`.
- Internal links and `goto` use `resolve()` from `$app/paths`.
- Scoped `<style>` per component; shared tokens as CSS custom properties.
- A `<!-- svelte-ignore code -->` names only the codes Svelte raises; put the
  reason in a separate comment, because `svelte/no-unused-svelte-ignore` reads
  any trailing text as more codes.
- Throwaway `Map`/`Set` built while computing a value belongs in a plain `.ts`
  function; `svelte/prefer-svelte-reactivity` flags it inside components.
- Links built by helpers: return a typed path template (`` `/task/${string}` ``)
  and wrap it in `resolve()` at the call site; ESLint has no type information in
  plain `.ts` files.

## TypeScript idioms

- Model domain values as types (`type Pence = number & { __brand: "Pence" }` where
  confusion is costly); prefer discriminated unions over optional-field soup.
- Narrow instead of asserting: replace `x!` with a guard, an early return, or a
  type that cannot be undefined. In tests, use `expect(x).toBeDefined()` then a
  narrowed helper, or build fixtures that are typed as present.
- `unknown` plus a parser at the boundary instead of `any`.
- A module exports what other modules use and nothing else.
- Barrel files (`index.ts` re-exporting everything) only for a domain's public face.

## Verify

```sh
<pm> run lint && <pm> run check && <pm> test   # pm = bun | pnpm | npm, whatever the package uses
```

Plain TypeScript (no Svelte) skips the Svelte sections; React and Vue follow the same
"routes compose, logic leaves the component, one API client per domain" rules.
