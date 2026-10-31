# The showcase reel

One HTML file, one continuous loop, no real data. A cursor drives everything, so each proposal is seen with its cause.

## Storyboard

Write it into the report before any code. Default: 120 BPM, one beat 0.5 s, one bar 2 s, 7–8 bars, something on
every beat. Each row: bar, beat, time, moment, proposal ID. Chain moments that belong together (button → wait →
check → toast; row → detail → back) as **one shape, never cut**: the same element morphs its size, radius and
colour, and its content swaps with a short blur.

## Build rules

- Every style is computed from `t` inside `seek(t)`: no CSS transitions, timers, or state carried between frames. Scrubbing to any time must give the same frame. This also makes rendering deterministic.
- Springs are closed-form step responses. A value that retargets is the sum of one spring per change. The template adds the previous loop's tail, so value and velocity are exactly periodic.
- Paired edges (tab indicators, knobs) ride different springs, so the leading edge stretches ahead.
- While something is held, its value comes from the cursor. On release it springs back from wherever it was.
- The camera zooms so each moment fills the frame; check that both ends of a chain stay in shot. Keep the cursor in screen space so it does not scale. No `will-change` on anything the camera scales.
- Swapped text gets its own exit and enter timing, overlapping slightly.
- Use the product's real tokens by linking its stylesheet, after inline fallbacks so the file still works when published alone.
- The last frame equals the first, including cursor position and velocity. Verify numerically, not by eye.
- Honour reduced motion for viewers: hold a representative still frame with a Play button. Add a scrubber outside the stage.

The reel is a simulation. Say so plainly, because a polished reel is easily mistaken for shipped behaviour.
Timings must match the proposals; if you spread two simultaneous events onto separate beats for legibility, say that in the storyboard.

## Render

1. `render_reel.py beats reel.html out/` renders one frame per beat. Tile them and also check mid-transition frames, where overlaps hide. Typical defects: rows with no opaque ground overlapping mid-reorder, ink text on an ink indicator, a chain's far end off camera.
2. `render_reel.py loop reel.html out/` checks the seam.
3. `render_reel.py full reel.html out/` renders 60 fps at 4 subframes, blended with `tmix`, to `out/reel.mp4`. Keep media out of git.

Silent unless the person supplies a track. With one, build the beat grid from it, start on a downbeat, and place UI sounds at measured peaks.
