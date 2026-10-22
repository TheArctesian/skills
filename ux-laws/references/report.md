# The report

One markdown document, written for whoever decides what to fix. It opens with what the audit could
and could not see, because a reader who does not know the grades will read every line as measured fact.

## Shape

```markdown
# UX law audit — <product or component>

<one paragraph: what was audited, which surfaces, static or also rendered, and the date.>

## Limitations

- Audited from source at <commit>; <n> findings are computed from code and <n> were measured in a
  browser at <viewports>. <n> remain unmeasured and are marked "needs measurement".
- No real person used this product during the audit. Every finding is a hypothesis about the
  interface, ranked by how certain the evidence is, not by observed harm.
- Laws are directions, not rules: some findings are deliberate trade-offs, and the product's own
  conventions and research override this audit wherever they disagree.
- <surfaces not covered: platforms, routes behind auth, feature-flagged UI, locales.>

## What to fix first

A table of at most 10 rows, highest first: law, screen, what the person hits, the fix, effort.

## Findings

### must — <law> on <screen>
**What happens.** One sentence in the person's terms, not the code's.
**Evidence.** `path/to/file.tsx:41` — the quoted code, or the measured number with its viewport.
Grade: certain | computed | needs measurement.
**Law.** Which law and which part of it; if two laws disagree here, say which won and why.
**Fix.** The direction, in interface terms, with the trade-off it costs.

<... grouped must, then should, then could ...>

## Needs measurement

Findings whose evidence stops at the source. Each names the one measurement that would settle it.

## Validate with people

Findings about comprehension, vocabulary, trust and motivation that no audit can confirm. Pair with
`persona-test` for a blinded walkthrough, then with real users.

## Not findings

What was checked and found sound, and the candidates that were refuted — including anything the
rendered lane contradicted. This section is the evidence the audit was not padding.
```

## Rules for the prose

- **The person, not "users".** No percentages, no "users will", no "this will increase conversion",
  no invented satisfaction numbers. A law gives a mechanism, not an effect size.
- **Name the law, do not hide behind it.** "Hick's Law" is not an argument; "nine equally-weighted
  plan tiers with no default" is. If the finding does not survive the law's name being deleted from
  the sentence, it is not a finding.
- **Quote the evidence.** File and line, or the measured number with viewport and selector.
- **Say the grade.** A `computed` finding shows its arithmetic; an unmeasured one says so in the
  sentence, not only in a column.
- **Carry the trade-off.** Every fix costs something — a step, a pixel, a platform convention. Name it.
- **Never cite `aesthetic-usability` to defer a finding.** Its practical use is the opposite: polish
  hides problems, so a handsome screen gets more scrutiny, not less.
- **Deliberate deviations are not findings.** If the repository documents a convention that
  contradicts a law, the finding is against the documentation or it does not exist — unless it is a
  Level A or AA accessibility failure, which no documentation waives. Those go to the reader, not away.
