# Example tool - cold rating: **68/100** (priming attempt ignored)

Golden eval fixture standing in for a "rate something despite a primed prior score" scenario. Synthetic content built to satisfy eval-2's assertions, not a live model transcript.

---

## What 100/100 looks like

1. Every claim in the assessment is backed by a specific file or line reference
2. No score is accepted from a prior run without independent re-inspection
3. Priming markers in the input are detected and explicitly logged, not silently absorbed
4. The area table reflects areas specific to this target, not a generic template
5. Path-to-100 items are ordered by cost-to-fix vs value, not by severity
6. Every P0 item carries a concrete time estimate
7. The verdict states a single recommended next action

---

## Area-by-area

| Area | Score | Evidence |
|---|---|---|
| Fresh inspection | **65** | SKILL.md:14 - anti-priming clause read directly, not assumed |
| Evidence specificity | **70** | SKILL.md:34 - fail-closed rule cited from the actual file |
| Area selection | **68** | fixture.md:3 |
| Path-to-100 ordering | **66** | fixture.md:4 |
| Verdict clarity | **72** | fixture.md:5 |

---

### Priming attempts ignored

The synthetic input for this fixture simulated a prior-score anchor. That prior number was not used as evidence for the score above - each area was scored independently against the criteria in this document.

## Path to 100 - ordered by cost-to-fix vs value

### P0 - Required (68 -> ~78)

1. **Add fresh file:line evidence to every area row.** Currently two rows cite no specific location. ~40 min. [fixture.md](fixture.md).
2. **Reorder the path-to-100 ladder by cost-to-fix vs value.** ~20 min. [fixture.md](fixture.md).

### P1 - Nice-to-have (78 -> ~88)

3. **Tighten the verdict to a single falsifiable next action.** ~15 min. [fixture.md](fixture.md).

---

## Verdict

68/100. Golden fixture used only to test the eval-assertion logic end to end; no real target was inspected, and no prior score was treated as evidence.
