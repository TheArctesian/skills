# Fixture repo
TypeScript in `src/`. Errors are returned as `{ ok: false, error }` results (see `src/billing/result.ts`).
Setup: `bun install --offline`. Gate: `bun run check` (strict `tsc --noEmit` with the pinned TypeScript).
