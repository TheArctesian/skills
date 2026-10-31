# Measuring motion

Every trap here produced a false reading in a real audit.

## Environment

- **A hidden document aborts view transitions**, and the abort looks like a hard cut with no error. Embedded browser panes can report hidden and throttle rAF. Use headless Chromium, which is always visible.
- **`networkidle` may never fire** on apps with streams or polling. Wait a fixed settle time instead.
- **Headless frame rate is not device frame rate.** It shows a loop's ceiling. To check a canvas budget, count paints (wrap `clearRect`/`putImageData`), not rAF callbacks; state the limit otherwise.
- **Dev servers differ from production builds** in load timing. Say which you measured.
- **Log in with the app's own test path** on synthetic data, and clear any first-run gate once before measuring, or every route quietly measures the gate. Check `page.url` after navigating.

## Reading `document.getAnimations()`

- Finished animations with `fill: both` stay listed. Filter to `playState === 'running'`, or you will report old arrivals as current.
- `getTiming().easing` on a CSS animation reads `linear` because the curve lives on the keyframes. It does not mean the animation is linear. Sample values or read the stylesheet.
- A JS tween or spring never appears here. Sample the property (`d`, `transform`, text) per frame to prove it moves continuously.
- Finding an animation listed does not mean it is visible or that it runs to the end.

## Layout shift

- The `layout-shift` observer excludes shifts within 500 ms of input (`hadRecentInput`), so post-click jumps read as zero. After an interaction, sample `getBoundingClientRect()` per frame.
- **A fast local API hides staged loading.** Batches land together and the score reads zero, while real users see the jump. Delay later requests with route interception (for example 400 ms) and measure again.
- **Shift below the fold does not count.** Measure in a tall viewport too (1600 px) before claiming a reserved height is right, and compare the reserved height with the loaded height directly.
- Measure at narrow, medium and wide widths and under reduced motion. Shift often grows as a grid narrows, and motion cannot soften it for someone who asked for less.
- Identical scores across pages usually mean one shared cause. Read `sources[].node` before celebrating or blaming.

## View transitions

- **Pausing at `ready` hides cut-offs.** Chromium ends a transition when a captured element is replaced, as when a loading branch swaps to a loaded one or a `span` becomes an `a`. Sample `currentTime` every frame through `finished`, with fast and slow data, in both directions.
- Then, to inspect a midpoint, pause each pseudo animation at half duration and screenshot. Look for one mark, not a doubled image.
- Duplicate names silently cancel the whole transition. Check uniqueness at runtime.
- Named elements also get the UA's group animation, a hardcoded 0.25 s that reduced-motion tokens do not reach.

## Interaction checks that catch real defects

- **Interrupt everything**: second click mid-flight, Escape mid-open, Back mid-transition, two dismissals 60 ms apart, then look for orphaned clones and hidden originals.
- **Press twice, with a delayed response** (route interception, 1.5 s). Count the requests. A loading state you can press through means duplicates.
- **Compare elements outside the change** against the base branch: unscoped CSS restyles things on other pages, sometimes only after a particular page was visited, so test both visit orders.
- **Measure both axes.** A neighbour's x can hold still while its y jumps 4 px.
- **Reduced motion**: confirm what the reader actually sees, that nothing waits on a hardcoded timer, and that no snapshot is taken for nothing.
- **Look at the frames.** Read the PNGs. String assertions pass on overlapping text.
