# Lane checklists

Each lane lists what to measure, then the gaps that most often turn out to be real.
Treat the gaps as hypotheses until the harness confirms them.

## Infrastructure

**Measure:**
- cold start: container start to first healthy response
- p50/p95/p99 and throughput at 1, 10 and 50 virtual users (k6 or similar)
- pool checkout waits
- image size and pull time per app
- production per-route latency, where telemetry exists (read-only, with approval)

**Common gaps:**
- **Concurrency.** One server process (no workers) on a couple of replicas, with sync
  handlers sharing a small threadpool.
- **Connection ceiling.** DB pool × processes × replicas is close to
  `max_connections`, with no pooler (PgBouncer). This blocks scaling out.
- **Startup work.** Migrations or `create_all` run on every boot, which slows cold
  start and scale-out.
- **Shared process.** Schedulers and cron jobs run inside the request process and
  compete for the pool and CPU, possibly running twice when there are several
  replicas.
- **Distance to the DB.** Compute and database in different regions or on a public
  network, plus `pool_pre_ping` adding a round trip on every checkout.
- **Cold starts.** Scale-to-zero on user-facing apps, or a burstable DB tier with
  CPU-credit throttling.
- **Static delivery.** No CDN, assets not precompressed, no long-lived cache headers
  on hashed files.
- **Images.** Single-stage builds that ship all of `node_modules`, and stray apt
  layers.
- **Polling.** Background polling (every 1–2 seconds) adding steady load.
- **Unrecorded settings.** Hand-made infra with no IaC, so there is no reproducible
  baseline. Capture it as code.

## API / backend

**Measure:**
- a heavy synthetic user on the production engine
- per-endpoint p50/p95 and query count on page 1, page 10 and a deep page
- `EXPLAIN (ANALYZE, BUFFERS)` on slow queries
- boot time, and `python -X importtime` (or the runtime's equivalent)

**Common gaps:**
- **Wrong window.** Ascending order with a limit returns the *oldest* N rows. Serve
  newest-first with a keyset cursor, and check what order every consumer expects
  first.
- **Rescanning history.** Overviews that `GROUP BY` over a user's entire history on
  every load. Use a bounded window, a rollup table or a short cache invalidated on
  ingest.
- **Missing indexes.** Indexes that exist in a script but were never built in
  production, and missing `(owner, time, id)` composites for keyset paging.
- **Writes on reads.** Sweeps or commits on read paths.
- **Deep-page over-fetch.** Fan-out across sources that over-fetches more the deeper
  you page, or decrypts or serialises rows it then discards.
- **Unbounded lists.** No pagination, and explicit N+1 loops for counts.
- **Recompute for one row.** Recomputing a whole feed to return a single row.
- **Boot cost.** Reflection-based migrations on every boot, and heavy optional
  imports loaded eagerly.
- **Serialisation.** Generic encoders where the schema's own serialiser is faster.

## Native client (macOS / iOS / Android)

**Measure:**
- signposts (OSSignposter or Trace) for launch: init → first frame → first content
- signposts for page open → shell → content
- a launch metric test, or `xctrace` App Launch
- Animation Hitches traces while scrolling the long lists
- release builds, pointed at a local backend with synthetic data. Never a real
  account: debug builds can pick up live work.

**Common gaps:**
- **Root invalidation.** The root view observes dozens of stores, so any background
  publish re-renders everything. Push observation down, or use `@Observable`.
- **Launch fan-out.** Every sync job starts at launch on the main actor, and SQLite
  I/O runs on the main thread.
- **Heavy init.** Analytics, stores and singletons are set up before the first frame.
  Defer them.
- **Pages torn down on navigation.** A `.id(state)` or similar destroys page models,
  so each revisit refetches.
- **No snapshot.** Nothing is saved to disk, so a cold launch waits on the network.
  Use a stale-while-revalidate snapshot.
- **History prefetch.** Older history prefetches months but not adjacent days or
  weeks, and the cache lives only in memory with a short TTL.
- **Non-lazy lists.** Stacks re-diffed on a fast poll. Use a lazy list with stable
  IDs, publish only on real change, and back off polling when idle.
- **Work in body.** Rows, colours or formatters rebuilt on every body evaluation.
- **3D and images.** Scenes reparsed per mount, and image loads with no cache.

## Web client

**Measure:**
- Lighthouse or WebPageTest: LCP, INP, CLS
- bundle size per route
- SSR time to first byte
- long tasks during scroll

**Common gaps:**
- waterfall data loads that could run in parallel
- no streaming
- oversized bundles that should be split
- uncompressed SSR
- long lists that aren't virtualised
- an animated background or other heavy decoration on every page
- images with no responsive sizes or lazy loading
