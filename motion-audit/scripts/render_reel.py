#!/usr/bin/env python3
"""Render a reel that exposes window.seek(t), window.REEL = {T, BEAT}, and ?render.

  uv run --with playwright python render_reel.py beats|loop|full reel.html out/ [--chrome PATH]
"""
import argparse, pathlib, re, shutil, subprocess, sys
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument("mode", choices=["beats", "loop", "full"])
ap.add_argument("reel"); ap.add_argument("out")
ap.add_argument("--chrome"); ap.add_argument("--size", type=int, default=1440)
ap.add_argument("--fps", type=int, default=60); ap.add_argument("--subframes", type=int, default=4)
a = ap.parse_args()
out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
clip = {"x": 0, "y": 0, "width": a.size, "height": a.size}

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, **({"executable_path": a.chrome} if a.chrome else {}))
    pg = b.new_page(viewport={"width": a.size, "height": a.size})
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(pathlib.Path(a.reel).resolve().as_uri() + "?render")
    pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(800)
    T, beat = pg.evaluate("[REEL.T, REEL.BEAT]")
    if a.mode == "beats":
        for i in range(round(T / beat)):
            t = i * beat + beat * 0.6
            pg.evaluate(f"seek({t})"); pg.screenshot(path=str(out / f"beat-{i + 1:02d}.png"), clip=clip)
        print(f"{round(T / beat)} frames in {out}")
    elif a.mode == "loop":
        read = "Array.from(document.querySelectorAll('[data-seam]')).map(e => e.style.transform)"
        pg.evaluate("seek(0)"); first = pg.evaluate(read); pg.screenshot(path=str(out / "seam-0.png"), clip=clip)
        pg.evaluate(f"seek({T - 1e-6})"); last = pg.evaluate(read); pg.screenshot(path=str(out / "seam-end.png"), clip=clip)
        nums = lambda v: [float(n) for n in re.findall(r"-?\d+\.?\d*(?:e-?\d+)?", v)]
        for x, y in zip(first, last):  # sampled 1 microsecond apart, so moving values differ by a hair
            same = all(abs(i - j) < 1e-3 for i, j in zip(nums(x), nums(y)))
            print("same " if same else "DIFF ", x, "|", y)
    else:
        frames = out / "frames"; frames.mkdir(exist_ok=True)
        rate = a.fps * a.subframes; n = round(T * rate)
        for i in range(n):
            pg.evaluate(f"seek({i / rate})"); pg.screenshot(path=str(frames / f"f{i:05d}.png"), clip=clip)
        vf = f"tmix=frames={a.subframes},select='not(mod(n+1\\,{a.subframes}))',setpts=N/{a.fps}/TB"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(rate), "-i", str(frames / "f%05d.png"),
                        "-vf", vf, "-r", str(a.fps), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16",
                        str(out / "reel.mp4")], check=True)
        shutil.rmtree(frames); print(out / "reel.mp4")
    b.close()
    if errors:
        sys.exit("page errors: " + "; ".join(errors[:5]))
