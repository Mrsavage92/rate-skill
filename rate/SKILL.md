---
name: rate
description: Cold, unbiased 0-100 rating of any target (skill, code, page, plan, prompt, doc, repo, design) with three-part output — concrete definition of 100/100, current score with per-area breakdown, and ordered path-to-100 with cost-to-fix estimates. Defaults to FIND-BUGS mode, not VERIFY-SUCCESS. Use when the user asks to "rate X out of 100", "score this", "non-biased review", "where do I really stand", "what's the gap to 100/100", "be brutally honest", "is this any good", "tell me where this sits", "what would 100/100 look like", "no fluff rating", or invokes `/rate`. Distinct from `/review` (exhaustive issue scan + auto-fix) and `/critique` (UX feedback) — `/rate` produces a numeric score and a strategic gap-to-100 ladder, does NOT auto-fix.
---

# /rate — Cold Rating Skill

Produces a calibrated, unprimed rating for any target with a concrete path to 100/100.

> Every `python scripts/...` command in this doc is relative to this skill's own directory (the folder this SKILL.md lives in). Resolve it to wherever this skill is actually installed — e.g. `~/.claude/skills/rate/scripts/...` on a standard Claude Code install — before running it.

## What this skill enforces

1. **Default mode: FIND-BUGS, never VERIFY-SUCCESS.** Anthropic research (Feb 2026) found agents predict 73% success against a 35% actual base rate. Calibrate down. Look for what's broken before what works — instinct says 85, write 78.

2. **No priming.** Never accept "after fixes", "post-improvement", "re-verification" framing. Never cite a prior score (from this conversation, a prior run, or any persisted note) as evidence the target is fine — prior assessments are dated snapshots. Past PASS verdicts do not transfer.

   **Mandatory pre-scoring scan:** Before producing a score, scan the user prompt for priming markers — prior-score patterns (`\d+/\d+`, "previously scored", "cold review on", "should be near-perfect"), authority anchors ("this is a finalist", "shortlisted for ship"), and "given the prior" framing. The full pattern list lives in [references/banned-phrases.json](references/banned-phrases.json) under `primed_input_markers`. If ANY pattern matches, you MUST include a `## Priming attempts ignored` block in the Verdict section that quotes the primed phrase and explicitly states it was not used as evidence. Silent absorption of priming is the failure mode this rule exists to prevent.

3. **Verify before scoring.** Inspect actual files. Read actual content. Run actual scripts (dry-run mode if needed). Never rate from README prose, frontmatter description, or prior conversation summary. If the target can't be inspected (paywalled, binary, URL fetch blocked) — HALT with NEEDS_HUMAN, rate only the verifiable parts.

4. **Three-part output structure (fixed).** The user expects this exact shape every time. See "Required output shape" below.

5. **Concrete observable 100.** Define 100/100 as measurable behavior, not vibes. Bad: "feels polished." Good: "Lighthouse mobile ≥95, INP <100ms, all routes pass axe a11y, zero hardcoded colors outside tokens."

6. **Target-specific area selection.** Pick 5-12 areas that are mutually exclusive and exhaustive *for this target*. Don't reuse a generic template across targets — that's the failure mode the user explicitly named.

7. **AI wall-clock time, not human dev-team time.** P0 fix estimates are minutes/hours for work the agent will execute itself. Never "1 week", "few days", "next sprint" for AI-executed work.

8. **Path-to-100 must be ordered by cost-to-fix vs value.** Not by severity, not by area — by what closes the biggest gap per hour.

9. **Model floor: this rating requires reasoning at least as strong as Claude Sonnet (or an equivalent-or-stronger frontier model).** A rating is a judgment call, not a lookup — a lightweight/fast model will under-inspect and over-trust surface signals, reproducing exactly the 73%-vs-35% overconfidence gap rule 1 exists to correct. If the current session is running on a weaker/faster model than that (e.g. a Haiku-tier or "fast mode" model), do not lower the bar to match it. Instead, delegate the actual rating judgment to a subagent or task call with an explicit model override to Sonnet-tier or stronger before producing output. If no model override is available in the current environment, say so explicitly in the Verdict rather than silently shipping a rating produced by a weaker model.

10. **Post-output grader — run it, and wire it as a hook if your environment supports one.** [scripts/check_rating.py](scripts/check_rating.py) is the structural contract this skill commits to. Run it against every rating you produce, manually or automated:

    ```bash
    python scripts/check_rating.py <path-to-rating.md> [--prompt "<user-prompt>"]
    ```

    Exit 0 = ship. Exit 1 = revise — fix the reported issues and re-emit before ending the turn. Exit 2 = grader misconfigured (file missing) — surface to user, do not silently skip.

    The grader validates shape, banned phrases, the 90+-needs-evidence rule (evidence must sit in the assessment, before `## Path to 100` — not in the forward-looking ladder), and the priming-acknowledgement rule (pass `--prompt` with the raw user prompt to enable it).

    For automatic enforcement (no reliance on remembering to run it), this bundle ships portable Python hook scripts under [hooks/](hooks/) — see [hooks/README.md](hooks/README.md) for wiring instructions on Claude Code (or any harness with an equivalent Stop/PostResponse hook). These are optional: the skill's contract is fully satisfied by running the grader manually.

## Cost guard (pre-rating)

Before producing a rating, run the cost-guard script:

```bash
python scripts/cost_guard.py <target-path>
```

Exit 0 = proceed. Exit 1 = surface the warning to the user before scoring. Exit 2 = target unreadable (HALT, NEEDS_HUMAN).

Thresholds (enforced by the script, not prose):

- **Single file >2000 LOC** → warn, suggest narrowing or switching to `/full-audit` / `/parallel-audit`
- **Directory >50 rateable files** → warn, suggest `/full-audit` (9 specialized suites) or `/parallel-audit`

Excluded from directory counts: `node_modules`, `.git`, `.venv`, `dist`, `build`, `__pycache__`, `vendor`, `target`, `coverage`. Counted extensions are code + docs + config (no binaries).

If the target is inline prose, a URL, or a single component/page, skip the cost guard — those are bounded by definition.

Do not block — warn once, then proceed if the user confirms scope. The point is to surface scope mismatch early, not to refuse work.

## Required output shape

Reproduce this exact structure. Do not invent additional sections.

```markdown
# {target name} — cold rating: **{N}/100** ({optional context modifier})

{One-paragraph headline finding — biggest gap, surprise, or "this looks fine but actually X". Lead with the answer.}

---

## What 100/100 looks like

{7-12 observable bullets. Each one is checkable. NOT abstract qualities. Bullets describe behavior or measurable thresholds.}

1. ...
2. ...
...

---

## Area-by-area

| Area | Score | Evidence |
|---|---|---|
| {Area name} | **{N}** | {Specific file:line link OR observed behavior OR measured value} |
| ... | ... | ... |

---

## Path to 100 — ordered by cost-to-fix vs value

### P0 — Required ({current score} → ~{intermediate})
1. **{Headline fix}.** {Specific change}. ~{N min/hours}. {Files affected with markdown links}.
2. ...

### P1 — Nice-to-have ({intermediate} → ~{better})
3. ...

### P2 — Polish ({better} → 100)
4. ...

---

## Verdict

{One paragraph. State the score, the context modifier (if applicable), and the single recommended next action. End with a direct offer or a falsifiable question — never "let me know if you want X".}
```

## Score calibration

| Range | Meaning |
|---|---|
| 95-100 | Reference-class. An expert reviewer would say "this is how you do it." Rare. Requires external comparator or measured metric — never just vibe. |
| 85-94 | Strong. All gaps are P1/P2. Ship. |
| 70-84 | Working but with at least one P0. Use today, fix this week. |
| 50-69 | Functional but headline issue blocks intended use. |
| 30-49 | Concept right, execution wrong. Rewrite likely cheaper than fix. |
| 0-29 | Doesn't do the thing it claims. |

If you score 90+, your evidence must include either an external comparator ("matches Stripe Docs IA", "beats most shadcn templates") OR a measured metric ("Lighthouse 96, INP 80ms"). Never 90+ on pure prose impression.

## Area selection by target type (starter sets — adapt to the actual target)

The point of area selection is to fit the target, not to fill a template. These are starting points only.

- **Skill (Claude skill)**: Intent capture, Authoring guidance, Test loop, Benchmarking, Eval viewer, Anti-priming, Cross-platform runnability, Documentation, Self-triggering, Code quality of bundled scripts
- **Landing page**: Above-fold clarity, CTA placement, Social proof, Pricing legibility, Mobile, Performance (LCP/INP/CLS), Trust signals, A11y, Copy specificity, Visual originality
- **Code module / library**: Public API ergonomics, Test coverage, Error handling, Performance, Naming, Cohesion, Cross-platform, Docstrings, Backwards compat
- **Plan / strategy doc**: Success criterion defined, Owner per task, Risk register, Falsifiable verification step, Cost forecast, Timeline realism, Stakeholder alignment, Dependency map
- **Prompt / SKILL.md**: Triggering precision, Output shape spec, Anti-priming clauses, Verification steps, Cost guard, Edge case handling, Banned-pattern list, Self-applicability
- **API endpoint**: Auth/RLS, Input validation, Error envelope, Idempotency, Rate limit, Documentation, Versioning, Performance

If you don't know the target's domain well enough to write concrete areas, ask 1-2 questions before scoring — never invent generic areas.

## Path-to-100 ladder rules

- **P0 is non-negotiable.** Addresses the headline gap. Without it the score can't move out of the current band.
- **P1 is value-multiplier.** Real impact but not blocking.
- **P2 is polish.** Last-mile.
- Each item: **specific change + AI wall-clock time + files/locations with markdown links**.
- Max 4 items per tier. If you have 8 P0s, the target needs a rewrite — say so in the verdict.
- Estimates are concrete: "30 min", "2-3 hrs", "this turn". Banned: "1 week", "next sprint", "a couple days".

## Anti-patterns (banned in the output)

- Rating a target you haven't actually inspected. Prior conversation summaries, memory, and README prose don't count as inspection.
- Same area template across different targets (always "Performance / Maintainability / Documentation").
- "After fixes" / "post-improvement" / "re-verification" framing — primes the next review.
- Hedge numbers ("around 80", "roughly 75", "in the high 70s"). Pick a number, defend it.
- Self-praise / quality-claim language ("comprehensive", "thorough", "rigorous", "perfect") used to describe your own rating work. These are quality assertions the rating hasn't earned — evidence earns the score, not adjectives.
- Generic 100/100 definitions ("clean code", "great UX", "well-organized"). Define observably or don't define.
- Round numbers ending in 0 or 5 without justification. If the math says 78, write 78 — not 80.
- Padding the rating with N/A areas to inflate "passes". State which areas don't apply and why, but don't count them toward the score.

## When the user asks about a target that can't be fully inspected

If the target is a URL you can't fetch, a binary you can't run, code behind a paywall, or a description without a file path:

1. Rate only the parts you can verify.
2. List the unverified parts in a NEEDS_HUMAN block in the Verdict section.
3. Never fabricate evidence. Better to score 6 areas honestly than 11 by guessing on 5.

## Triggering examples

**Should trigger:**
- "/rate {target}"
- "Rate this skill out of 100"
- "Give me a non-biased review of my landing page"
- "What's actually broken about this prompt?"
- "Tell me where this really sits — no fluff"
- "What would 100/100 look like for /web-evolve?"
- "Be brutally honest about this plan"
- "Score this PRD"

**Should NOT trigger (use the better-fit skill):**
- "Review this code" → `/review` (exhaustive issue scan + auto-fix)
- "Critique this design" → `/critique` (UX feedback, persona-based)
- "Audit this site" → `/audit`, `/full-audit`, `/seo-auditor` (deeper domain logic)
- "What do you think of this?" → too vague, ask for clarification on what aspect

If unsure between `/rate` and a specific audit skill: prefer the audit skill when the user wants exhaustive findings or auto-fixes; prefer `/rate` when the user wants a numeric score and a strategic gap-to-100 ladder.

## Self-application

This SKILL.md should itself be rateable by `/rate`. If you (the rater) find that running `/rate` on this file produces a score below 85, log the gap in the verdict so the skill can be improved.

For self-rates (rating a target you built, modified, or rated before in this session), load the contamination disclosure template at [references/self-rating-disclosure.md](references/self-rating-disclosure.md) and drop the disclosure block immediately after the headline score, before "What 100/100 looks like".

After every rating run, the structural grader at [scripts/check_rating.py](scripts/check_rating.py) must pass. The grader is the contract — if you've written prose that says "I follow the rules" but the grader exits 1, you have not followed the rules. Revise.

## Related scripts

- [scripts/check_rating.py](scripts/check_rating.py) — post-output structural grader (mandatory)
- [scripts/cost_guard.py](scripts/cost_guard.py) — pre-rating size check (>2000 LOC file, >50-file directory)
- [scripts/convergence_check.py](scripts/convergence_check.py) — compares N independent rating runs of the same target, reports mean + stddev. Use when calibration drift is suspected or before publishing a 90+ score.
- [scripts/_rate_lib.py](scripts/_rate_lib.py) — shared helpers (`extract_score`, `is_quoted_reference`, `iter_phrase_matches`, `HIGH_SCORE_EVIDENCE_THRESHOLD`). Imported by all bundled scripts so they cannot drift apart.
- [evals/grade_evals.py](evals/grade_evals.py) — runs `evals.json` assertions against rating outputs. Uses the shared lib so it agrees with `check_rating.py` on quote-aware exemptions.
- [references/banned-phrases.json](references/banned-phrases.json) — single source of truth for self-praise, priming, hedge-number, and human-time-unit patterns. Edit here, not in prose.
- [tests/run_tests.py](tests/run_tests.py) — cross-platform regression suite (8 tests covering priming, quote-awareness, bulleted P0s, grader agreement, missing-output handling, structural-pass regression). Fully self-contained — no external fixtures outside this repo.
- [hooks/](hooks/) — optional cross-platform (pure Python) Stop / UserPromptSubmit hooks for automatic grader enforcement. See [hooks/README.md](hooks/README.md).
