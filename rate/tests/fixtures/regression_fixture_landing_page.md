# Example landing page — cold rating: **71/100**

Self-contained regression fixture standing in for a "rate a cross-domain target like a landing page" scenario. No real findings — used only to exercise the grader end to end.

---

## What 100/100 looks like

1. The hero communicates the core value proposition without scrolling, on a 375px viewport
2. Every primary CTA is reachable within one thumb-reach zone on mobile
3. Social proof (logos, review count, or a named customer) appears above the fold
4. LCP, INP, and CLS all pass Core Web Vitals thresholds on a throttled mobile profile
5. Pricing (if applicable) is stated in plain numbers, not "contact us" for a self-serve product
6. Every interactive element passes a basic axe accessibility scan
7. Copy names a specific outcome or number, not generic adjectives like "powerful" or "seamless"

---

## Area-by-area

| Area | Score | Evidence |
|---|---|---|
| Above-fold clarity | **68** | fixture.tsx:1 |
| CTA placement | **74** | fixture.tsx:2 |
| Social proof | **65** | fixture.tsx:3 |
| Mobile layout | **72** | fixture.tsx:4 |
| Performance (LCP/INP/CLS) | **70** | fixture.tsx:5 |
| Copy specificity | **76** | fixture.tsx:6 |

---

## Path to 100 — ordered by cost-to-fix vs value

### P0 — Required (71 → ~80)

1. **Add a named customer or review count above the fold.** No social proof currently appears before the first scroll. ~30 min. [fixture.tsx](fixture.tsx).
2. **Replace generic hero copy with a specific outcome claim.** ~20 min. [fixture.tsx](fixture.tsx).

### P1 — Nice-to-have (80 → ~90)

3. **Tighten mobile CTA thumb-reach placement.** ~25 min. [fixture.tsx](fixture.tsx).

### P2 — Polish (90 → 100)

4. **Run an axe scan and fix reported contrast issues.** ~30 min. [fixture.tsx](fixture.tsx).

---

## Verdict

71/100. Regression fixture used only to test the grader's structural checks end to end; no real target was inspected.
