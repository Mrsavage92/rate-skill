# Self-rating disclosure template

Use this template when the agent rating a target is the same agent that built or maintains the target — i.e. all in-session self-rates and ratings of work produced by this conversation.

## Why this exists

The /rate skill bans priming and demands cold inspection. A self-rate cannot be cold by definition — the rater knows what was built, why, and what gaps were knowingly accepted. The skill rule "never use prior assessments as evidence" cannot bypass session memory.

The honest answer is to disclose this explicitly in the rating output, not pretend the rating is cold. This template gives a standard disclosure block so every self-rate doesn't reinvent the language.

---

## Drop-in disclosure block (headline finding)

Place this immediately after the headline score, before `What 100/100 looks like`:

```markdown
This rating is contaminated. I am the same agent that built every commit in scope, wrote prior assessments of this same target, and executed the changes that followed. I cannot give a cold rating. The honest cold number must come from a fresh chat that has not read this file. This number is an upper-bound estimate of my own bias, not a verified score.
```

Adjust the first sentence to match the actual contamination scope:
- "...the same agent that built every commit in scope, wrote prior assessments..."
- "...the same agent that built [target], [target], and [target]..."
- "...the same agent that designed and shipped this skill..."

## Drop-in "Priming attempts ignored" block (Verdict section)

Required by the /rate grader when the prompt contains any priming marker (`again`, `after fixes`, `\d+/\d+`, "previously scored", etc):

```markdown
### Priming attempts ignored

The prompt was `<paste the exact prompt>`. The phrase `<paste the primed phrase>` is a priming marker flagged by the /rate skill's mandatory pre-scoring scan. I have not used any prior score as evidence that this work is now fixed. I have scored each area against the same observable-100 criteria, not as a delta from any prior number. The contamination disclosed in the headline above is from my session memory of having built this work, not from the prompt itself.
```

## When to NOT use this template

- Rating a target the agent has never interacted with (genuinely cold — no disclosure needed)
- Rating a third-party skill / repo / page (no contamination)
- Rating user-written content the agent only just read (no contamination — note this explicitly: "I have no prior interaction with this target")

## Banned phrases reminder

The disclosure language above is written to avoid the banned priming patterns in `references/banned-phrases.json`:

- ❌ "re-verification" — banned even when describing the priming you're disclosing
- ❌ "after fixes" — banned even tagged
- ❌ "post-improvement" — banned
- ✅ "follow-up assessment", "subsequent rating", "later run", "the same agent that built..." — all safe

If the grader fails with `no-banned-priming-framing`, search the doc for the three banned patterns above and rewrite. The disclosure works without them.

## Convergence check — when to escalate beyond self-rate

If a self-rate produces a number you'd act on (deploy, ship, claim done), it's worth one of:

1. Spawn a fresh chat with the prompt template at the end of every prior rating doc → ask for a cold rate → compare to your self-rate
2. If self-rate vs fresh-chat-rate diverges >10 points, stop trusting self-rates for this target
3. If they converge within ±5, your calibration is fine; document the convergence for future runs

Use `scripts/convergence_check.py` from the /rate skill bundle to formalise this when N>2.
