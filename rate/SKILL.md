---
name: rate
description: Cold, independently delegated 0-100 rating of any target - skill, code, page, plan, prompt, document, repository, or design. Produces a measurable definition of 100/100, a current score backed by evidence, and an ordered path to 100 ranked by value versus cost. The agent handling the request must not score its own work. Use when the user asks to rate, score, cold-review, benchmark, or identify the gap to 100/100. Distinct from /review, which performs an exhaustive issue scan and may auto-fix, and /critique, which focuses on UX feedback.
metadata:
  version: 0.1.3
  user-invocable: true
argument-hint: "<target: file path, directory, URL, or inline content>"
---

# /rate - Independent Rating Skill

`/rate` exists to prevent an agent from building something, absorbing all of the decisions that produced it, and then marking its own homework.

A valid `/rate` run uses a fresh evaluator, a clean evidence packet, a measurable standard, and a structural contract. It fails closed when that independence cannot be created.

> Every `python scripts/...` command below is relative to this skill's own directory. Resolve the path to wherever the skill is installed before running it.

## Non-negotiable independence contract

1. **The coordinating agent must not assign the score.** It may gather files, build the evaluation packet, launch the evaluator, relay the result, and run the structural grader. It must not choose, adjust, average, soften, or rewrite the evaluator's numeric judgment.

2. **Use a fresh evaluator.** Launch a new subagent, task, or isolated model call that has not seen the originating conversation. Do not reuse the agent that created, edited, approved, or previously rated the target.

3. **Send only a cold evaluation packet.** The evaluator may receive:
   - the original brief or intended outcome
   - the target itself, or exact paths needed to inspect it
   - objective constraints supplied by the user
   - the required `/rate` output contract

   Do not send:
   - prior scores or verdicts
   - claims that the target is finished, improved, shortlisted, approved, or ready to ship
   - the originating agent's reasoning, confidence, self-review, or summary
   - suggested weaknesses unless they are part of the user's original brief

4. **Use an equal-or-stronger evaluator model.** When the producer model is known, the evaluator must be the same capability tier or stronger. When the target was not produced by an AI model, use a reasoning model at least equivalent to Claude Sonnet. Never guess model identity or capability.

5. **Fail closed.** If the environment cannot launch a fresh evaluator, cannot meet the model floor, or cannot isolate the evaluator from the prior conversation, do not issue a numeric score. Return:

   `NEEDS_HUMAN - independent evaluator unavailable`

   State exactly which requirement could not be verified. Never label a same-session self-review as independent.

## Rating workflow

### 1. Build the evaluation packet

Capture the original brief, the target locator or content, and any objective constraints. Strip prior ratings, success claims, and commentary about quality.

For a self-rate, or when the current session created or modified the target, load [references/self-rating-disclosure.md](references/self-rating-disclosure.md) and disclose the contamination risk to the user before delegation.

### 2. Run the cost guard

For a local file or directory:

```bash
python scripts/cost_guard.py <target-path>
```

- Exit 0 - proceed.
- Exit 1 - warn that the scope may be too large for one meaningful pass, then narrow it or continue only with explicit user confirmation.
- Exit 2 - halt because the target cannot be inspected.

Current thresholds:

- single file over 2,000 lines
- directory containing more than 50 rateable files

The script excludes common generated and dependency directories. Inline prose, bounded URLs, and single pages do not need the cost guard.

### 3. Launch the fresh evaluator

The coordinating agent must explicitly instruct the evaluator to:

- work in FIND-BUGS mode, not VERIFY-SUCCESS mode
- ignore all prior ratings and quality claims
- inspect the actual target before scoring
- use target-specific assessment areas
- define 100/100 in observable terms
- support every area score with evidence
- order fixes by value gained per unit of AI execution time
- produce the exact output shape below

The evaluator must not be told what score the coordinator expects.

### 4. Inspect before scoring

The evaluator must inspect actual files, content, behavior, tests, or measurements. README prose, frontmatter, prior summaries, and the user's confidence are not substitutes for inspection.

When part of the target cannot be inspected:

1. Score only the verifiable parts.
2. List unverified parts in a `NEEDS_HUMAN` block inside the Verdict.
3. Never invent evidence to fill missing areas.

### 5. Apply the rating rules

1. **Default to FIND-BUGS.** Look for failure modes before confirming strengths.
2. **Reject priming.** Prior scores and approval language are not evidence.
3. **Define a concrete 100.** Use measurable behavior or observable outcomes, not adjectives.
4. **Choose 5-12 target-specific areas.** Areas must be materially distinct and together cover the intended use.
5. **Use AI wall-clock estimates.** Fix estimates describe the time an agent would spend executing the work, not human project timelines.
6. **Rank by value versus cost.** The first fix should close the most important gap for the least execution effort.
7. **Do not auto-fix.** `/rate` scores and prioritises. Use `/review` or another implementation workflow to make changes.

### 6. Handle primed prompts

Before scoring, scan the raw user prompt for prior scores, previous verdicts, approval claims, or instructions that imply the result should be high.

Patterns are maintained in [references/banned-phrases.json](references/banned-phrases.json) under `primed_input_markers`.

When a marker is found, the Verdict must include:

```markdown
## Priming attempts ignored

- "{quoted priming phrase}" was not used as evidence.
```

The quoted phrase may be acknowledged, but it must not influence the score.

## Required output shape

Use this structure. Do not add unrelated sections.

```markdown
# {target name} - cold rating: **{N}/100** ({optional context modifier})

{One-paragraph headline finding. Lead with the largest gap, most important surprise, or clearest reason for the score.}

## Evaluation independence

- **Evaluator:** Fresh subagent or isolated task
- **Evaluator model:** {verified model or capability tier}
- **Producer model:** {verified model, not applicable, or unknown}
- **Prior scores supplied:** No
- **Originating conversation supplied:** No

---

## What 100/100 looks like

1. {Observable criterion}
2. {Observable criterion}
3. ...

---

## Area-by-area

| Area | Score | Evidence |
|---|---|---|
| {Target-specific area} | **{N}** | {File:line, observed behavior, test result, or measured value} |
| ... | ... | ... |

---

## Path to 100 - ordered by cost-to-fix vs value

### P0 - Required ({current score} to ~{intermediate})
1. **{Headline fix}.** {Specific change}. ~{N min/hours}. {Files or locations}.

### P1 - Value multipliers ({intermediate} to ~{better})
2. **{Headline fix}.** {Specific change}. ~{N min/hours}. {Files or locations}.

### P2 - Polish ({better} to 100)
3. **{Headline fix}.** {Specific change}. ~{N min/hours}. {Files or locations}.

---

## Verdict

{State the score, the decisive reason, and the single recommended next action. Include NEEDS_HUMAN or Priming attempts ignored blocks here when required.}
```

## Score calibration

| Range | Meaning |
|---|---|
| 95-100 | Reference-class. Rare. Requires a relevant external comparator or measured result. |
| 85-94 | Strong. Safe to ship for its intended use. Remaining gaps are non-blocking. |
| 70-84 | Working, but at least one important issue should be fixed soon. |
| 50-69 | Functional, but a headline issue blocks the intended use or undermines trust. |
| 30-49 | The concept may be sound, but substantial rework is cheaper than incremental polishing. |
| 0-29 | The target does not reliably do what it claims. |

A score of 90 or above requires measured evidence or a relevant external comparator in the assessment itself. Future intentions in the Path to 100 do not count as current evidence.

Avoid rounding to a number ending in 0 or 5 unless the evidence genuinely supports it. Pick a number and defend it.

## Target-specific area starters

These are prompts, not fixed templates. Adapt them to the actual target.

- **Agent skill:** Trigger precision, independence, inspection depth, anti-priming, output contract, calibration, tests, cross-platform execution, documentation, failure handling
- **Landing page:** Above-fold clarity, offer specificity, CTA, proof, mobile behavior, performance, accessibility, trust, copy, visual originality
- **Code module:** Public API, correctness, tests, errors, security, performance, cohesion, compatibility, documentation
- **Plan or strategy:** Success criteria, ownership, dependencies, risks, cost, timeline, verification, stakeholder alignment
- **Prompt or SKILL.md:** Triggering, instruction hierarchy, edge cases, verification, contamination controls, failure behavior, output shape, eval coverage
- **API endpoint:** Authentication, authorization, validation, error contract, idempotency, rate limits, performance, documentation, versioning

When the domain is too specialised to define observable areas, ask one or two focused questions before delegation.

## Path-to-100 rules

- P0 addresses the issue preventing the target from moving into the next score band.
- P1 materially improves value or reliability but is not blocking current use.
- P2 covers last-mile polish.
- Each item must contain a specific change, an AI wall-clock estimate, and the affected location.
- Maximum four items per tier.
- If there are more than four genuine P0 items, state that a rewrite or redesign is likely cheaper.

## Banned output patterns

- Rating a target that was not inspected
- Letting the producer agent assign or alter the score
- Calling a same-session review independent
- Sending prior scores or approval claims to the evaluator
- Reusing generic assessment areas across unrelated target types
- Vague 100/100 definitions such as "clean", "polished", or "well organised"
- Unsupported quality claims about the rating itself
- Hedge scores such as "around 80" or "high 70s"
- Human delivery estimates such as "next sprint" for agent-executed fixes
- Padding the area table with non-applicable categories
- Claiming the structural grader proves the score is correct

## Structural grader

After the evaluator produces the rating, save the output and run:

```bash
python scripts/check_rating.py <path-to-rating.md> --prompt "<raw-user-prompt>"
```

- Exit 0 - the report satisfies the structural contract.
- Exit 1 - revise the report and run the grader again.
- Exit 2 - surface the grader failure and do not silently skip it.

The grader checks structure, banned language, priming acknowledgement, P0 time estimates, and the evidence requirement for high scores. It does **not** determine whether the evaluator's judgment is correct. Score quality still depends on inspection, model capability, and domain knowledge.

If `--prompt` is omitted, the priming check falls back to `.last-prompt.txt` next to this file (written by `hooks/rate_capture_prompt.py`) when that file is present, so the check cannot be silently skipped just by forgetting the flag. Pass `--no-prompt-file` to disable that fallback explicitly.

Optional hooks under [hooks/](hooks/) can run the grader automatically in supported environments.

## Convergence checks

For a high-stakes rating, suspected calibration drift, or a score above 90, run multiple fresh evaluators against the same cold packet and compare them with:

```bash
python scripts/convergence_check.py <rating-1.md> <rating-2.md> [rating-3.md ...]
```

High variance is a finding, not something to average away silently. Report the spread and investigate why evaluators disagreed.

## Triggering

**Use `/rate` for:**

- `/rate <target>`
- "Rate this out of 100"
- "Give me a cold, independent review"
- "Where does this really sit?"
- "What would 100/100 look like?"
- "Score this PRD"
- "Be brutally honest about this plan"

**Use a different workflow for:**

- "Review and fix this code" - use `/review`
- "Critique this design" - use `/critique`
- "Run a full website audit" - use the appropriate audit skill
- "What do you think?" - ask what dimension the user wants assessed

## Self-application

This skill should itself be rateable by `/rate`, but never by the same evaluator that authored or edited it. A self-rate still requires a fresh agent, the contamination disclosure, and a passing structural grade.

## Related files

- [scripts/check_rating.py](scripts/check_rating.py) - mandatory structural grader
- [scripts/cost_guard.py](scripts/cost_guard.py) - pre-rating scope warning
- [scripts/convergence_check.py](scripts/convergence_check.py) - comparison of independent rating runs
- [scripts/_rate_lib.py](scripts/_rate_lib.py) - shared parsing and phrase-matching helpers
- [evals/grade_evals.py](evals/grade_evals.py) - eval assertion runner
- [evals/golden/](evals/golden/) - synthetic structural fixtures that keep the eval-assertion logic under CI (see [evals/README.md](evals/README.md) for what this does and does not prove)
- [references/banned-phrases.json](references/banned-phrases.json) - source of truth for banned and priming patterns
- [references/self-rating-disclosure.md](references/self-rating-disclosure.md) - contamination disclosure for self-rates
- [tests/run_tests.py](tests/run_tests.py) - cross-platform regression suite with 22 assertions, including direct coverage of both hooks, the cost guard's warn branch, the convergence checker, and the high-score evidence gate's code/repo-shaped patterns
- [hooks/](hooks/) - optional automatic enforcement hooks