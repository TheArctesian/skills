# Report format

Synthetic findings are hypotheses about the interface, not evidence about users. The report says so first.

## Structure

1. **Limitations** (always first, 3–5 lines): synthetic participants, the model, the number of personas and tasks,
   which drivers ran, what was not covered (from the coverage gaps), and that findings need real users to confirm
   frequency and impact.
2. **Summary**: one paragraph, then a table of sessions: persona, task, ended (done / gave-up / budget / blocked),
   end state met (and whether the harness or the persona's own screen text checked it), wrong turns, backtracks.
3. **Findings**, confirmed first, then uncertain, each sorted by severity:
   - title naming the screen and the problem
   - severity 0–4 (Nielsen: 0 not a problem, 1 cosmetic, 2 minor, 3 major, 4 blocks the task), judged from how
     often it occurred across sessions, how much it blocked (did sessions give up there?), and whether it recurs
     on every visit
   - kind and trust tier: `trusted` (findability, labels, feedback, error recovery, dead ends, accessibility tree,
     layout) or `medium` (copy comprehension: check with real users)
   - reach: how many distinct enforced handicaps hit it (driver, text size, appearance, reading, scrolling), not how
     many persona names
   - the evidence trail: persona, task, steps, what the screen showed
   - the verifier verdicts
   - a fix hint in interface terms (what to show, label or move), never code
4. **Refuted and unverified**: one line each.
5. **Coverage gaps and collapsed personas**.
6. **Validate with real users**: the medium-tier and uncertain findings worth a real session.

## Forbidden

- Percentages or counts of users ("40% of users"), any population claim.
- Quotes presented as a user's voice.
- Satisfaction, emotion, trust or preference scores.
- "Users will…" or "users want…".
- Comparisons with real-user studies.
