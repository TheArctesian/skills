#!/usr/bin/env python3
"""Measure load motion per route: layout shift, long frames, running animations.

Measurement only: it never clicks or submits. Refuses non-local hosts unless --hosted is
passed, which needs the person's own authorisation.

  uv run --with playwright python probe.py --base http://127.0.0.1:5173 \
      --routes / /settings --widths 375 768 1440 --reduced --delay-ms 400 --out out/
"""
import argparse, json, pathlib, sys, time
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

INIT = r"""
(() => {
  window.__cls = []; window.__loaf = [];
  const name = n => { if (n && n.nodeType !== 1) n = n.parentElement; if (!n) return null;
    const c = typeof n.className === 'string' ? n.className.trim().split(/\s+/).slice(0, 3).join('.') : '';
    return n.tagName.toLowerCase() + (n.id ? '#' + n.id : '') + (c ? '.' + c : ''); };
  try { new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput)
    window.__cls.push({ t: Math.round(e.startTime), v: +e.value.toFixed(4), src: (e.sources || []).map(s => ({
      node: name(s.node), dy: Math.round(s.currentRect.y - s.previousRect.y),
      dh: Math.round(s.currentRect.height - s.previousRect.height) })) });
  }).observe({ type: 'layout-shift', buffered: true }); } catch {}
  try { new PerformanceObserver(l => { for (const e of l.getEntries())
    window.__loaf.push({ t: Math.round(e.startTime), d: Math.round(e.duration) });
  }).observe({ type: 'long-animation-frame', buffered: true }); } catch {}
  window.__running = () => document.getAnimations().filter(a => a.playState === 'running').map(a => {
    const t = a.effect.getTiming();
    return { name: a.animationName || a.transitionProperty || a.constructor.name,
      dur: Math.round(+t.duration * 100) / 100, delay: Math.round(+t.delay),
      pseudo: a.effect.pseudoElement || null, target: name(a.effect.target) }; });
})();
"""

def summarise(samples):
    seen = {}
    for s in samples:
        for a in s["running"]:
            k = (a["name"], a["dur"], a["pseudo"])
            seen[k] = seen.get(k, 0) + 1
    return [{"name": k[0], "dur": k[1], "pseudo": k[2], "samples": v} for k, v in sorted(seen.items(), key=str)]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--routes", nargs="+", default=["/"])
    ap.add_argument("--widths", nargs="+", type=int, default=[375, 768, 1440])
    ap.add_argument("--height", type=int, default=900, help="use 1600 too: shift below the fold does not count")
    ap.add_argument("--reduced", action="store_true", help="also measure prefers-reduced-motion")
    ap.add_argument("--delay-ms", type=int, default=0, help="delay fetch/XHR, so staged loading shows locally")
    ap.add_argument("--settle-ms", type=int, default=3000, help="fixed wait: networkidle may never fire")
    ap.add_argument("--cookie", help="name=value, read from a local synthetic-member login")
    ap.add_argument("--chrome", help="browser executable, if Playwright's own is not installed")
    ap.add_argument("--hosted", action="store_true", help="allow a non-local host; needs the person's authorisation")
    ap.add_argument("--out", default="probe-out")
    a = ap.parse_args()

    host = urlparse(a.base).hostname or ""
    if not a.hosted and not (host in {"localhost", "127.0.0.1", "::1"} or host.endswith(".localhost")):
        sys.exit(f"refusing {host}: pass --hosted only if the person authorised it themselves")
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, **({"executable_path": a.chrome} if a.chrome else {}))
        for reduced in [False, True] if a.reduced else [False]:
            for width in a.widths:
                ctx = browser.new_context(viewport={"width": width, "height": a.height},
                                          reduced_motion="reduce" if reduced else "no-preference")
                if a.cookie:
                    n, v = a.cookie.split("=", 1)
                    ctx.add_cookies([{"name": n, "value": v, "domain": host, "path": "/"}])
                ctx.add_init_script(INIT)
                if a.delay_ms:
                    def slow(route, req):
                        if req.resource_type in {"fetch", "xhr"}:
                            time.sleep(a.delay_ms / 1000)
                        route.continue_()
                    ctx.route("**/*", slow)
                for route in a.routes:
                    page = ctx.new_page()
                    page.goto(a.base + route, wait_until="commit")
                    samples, last = [], 0
                    for t in (50, 150, 400, 900):
                        page.wait_for_timeout(t - last); last = t
                        try:
                            samples.append({"t": t, "running": page.evaluate("window.__running()")})
                        except Exception:
                            samples.append({"t": t, "running": []})
                    page.wait_for_timeout(a.settle_ms)
                    cls, loaf = page.evaluate("[window.__cls, window.__loaf]")
                    slug = (route.strip("/").replace("/", "_") or "root") + f"-{width}" + ("-reduced" if reduced else "")
                    page.screenshot(path=str(out / f"{slug}.png"))
                    results.append({"route": route, "final_url": page.url, "width": width, "reduced": reduced,
                                    "cls": round(sum(e["v"] for e in cls), 4),
                                    "shifts": [e for e in cls if e["v"] > 0.001],
                                    "long_frames": [f for f in loaf if f["d"] >= 50],
                                    "animations": summarise(samples)})
                    page.close()
                ctx.close()
        browser.close()
    (out / "probe.json").write_text(json.dumps(results, indent=1))
    for r in results:
        moved = "" if urlparse(r["final_url"]).path == r["route"] else f"  REDIRECTED to {r['final_url']}"
        worst = (r["shifts"] or [{"src": []}])[0]["src"][:1]
        print(f'{r["route"]:<32} {r["width"]:>5}{" reduced" if r["reduced"] else "":<8} cls={r["cls"]:<7} '
              f'long={len(r["long_frames"])} anims={len(r["animations"])} {worst or ""}{moved}')

if __name__ == "__main__":
    main()
