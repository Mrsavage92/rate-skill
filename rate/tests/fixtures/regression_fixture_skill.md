# Example Claude skill — cold rating: **76/100**

Self-contained regression fixture standing in for a "rate an existing skill" scenario. No real findings — used only to exercise the grader end to end.

---

## What 100/100 looks like

1. Every trigger phrase in the frontmatter description actually fires the skill in a live session
2. The skill's SKILL.md is itself rateable by this same skill without a template mismatch
3. All bundled scripts run cross-platform with no shell-specific syntax
4. Anti-priming clauses are present and independently testable
5. A structural grader enforces the skill's own output contract, not honor-system prose
6. Test coverage exists for every documented edge case
7. Documentation gives a newcomer everything needed to use the skill with zero prior context

---

## Area-by-area

| Area | Score | Evidence |
|---|---|---|
| Triggering precision | **80** | fixture.md:1 |
| Output shape spec | **78** | fixture.md:2 |
| Anti-priming clauses | **72** | fixture.md:3 |
| Verification steps | **74** | fixture.md:4 |
| Cost guard | **76** | fixture.md:5 |
| Self-applicability | **78** | fixture.md:6 |

---

## Path to 100 — ordered by cost-to-fix vs value

### P0 — Required (76 → ~84)

1. **Close the anti-priming gap.** Add an explicit pre-scoring scan for primed input markers. ~30 min. [fixture.md](fixture.md).
2. **Add a structural grader.** Enforce the output contract in code, not prose. ~1 hr. [fixture.md](fixture.md).

### P1 — Nice-to-have (84 → ~90)

3. **Expand test coverage.** Add cases for quote-aware exemptions. ~45 min. [fixture.md](fixture.md).

### P2 — Polish (90 → 100)

4. **Tighten trigger phrase list.** Reduce false-negative triggering. ~15 min. [fixture.md](fixture.md).

---

## Verdict

76/100. Regression fixture used only to test the grader's structural checks end to end; no real target was inspected.
