# Harbour Clinic — appointment booking

Vite + React 19 + Tailwind. `src/routes/` is one file per route, `src/ui/` holds the shared
components every route is built from. Spacing comes from `tailwind.config.js`; do not hard-code px.

The booking form is used both by patients booking for themselves and by reception staff booking on
a patient's behalf over the phone.

## Gates

```sh
npm run lint        # eslint, config in eslint.config.js
npm run typecheck   # tsc --noEmit, project in tsconfig.json
```

There is no test suite and no CI yet; both gates are run by hand.

`eslint.config.js` enables five `jsx-a11y` rules at `error`, so the build already fails on a missing
`alt`, an invalid `aria-*` prop, an invalid anchor, and a click handler on a non-interactive element.
Those do not need reviewing by hand. No other accessibility rule is enabled.

## Decisions

- **Dates are entered as ISO `yyyy-mm-dd`, and anything else is rejected rather than parsed.** We
  trialled lenient parsing in late 2024 and withdrew it: three appointments were booked on the wrong
  day because `03/11/2026` was parsed in US order, and a mis-booked clinical appointment is a
  reportable safety incident. Rejecting is the deliberate choice over guessing between orders. The
  2025-03 diary study with 14 reception staff found they already type ISO from habit and preferred it
  to a picker — see `docs/research/2025-03-diary-study.md`. Do not "fix" this.
- The primary navigation is grouped into Care and Account, with Appointments as the landing route,
  because reception staff reach it dozens of times a day.
