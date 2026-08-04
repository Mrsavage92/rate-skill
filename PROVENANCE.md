# Provenance

`/rate`'s own contract asks every target it rates to disclose producer model
and evaluator independence (see the "Evaluation independence" block in the
[required output shape](rate/SKILL.md#required-output-shape)). It would be
inconsistent to stay silent about this repository's own provenance.

## How this repo was built

- **Producer:** Claude (Claude Sonnet 5, via Claude Code), working with a
  human maintainer across an interactive session. The skill originated inside
  the maintainer's personal Claude Code configuration, was extracted into
  this standalone repository, and was hardened through two rounds of
  independent cold rating (see below).
- **Independent verification during development:** at two points during
  development, a fresh subagent with no memory of the building conversation
  was asked to cold-rate this repository using the skill's own process. The
  first run scored 74/100 and found a real overclaim in the README plus
  concrete test-coverage and enforcement gaps; those were fixed and verified
  (tests, CI, structural grader) before a second fresh subagent rated the
  result at 78/100 and found a different set of real gaps (distribution,
  OSS scaffolding, an untested branch). The second run's transcript is
  committed verbatim at [docs/example-rate-run.md](docs/example-rate-run.md).
  Further hardening followed that second rating.
- **What this does and doesn't mean:** the independent-rating step is real
  and its findings were real (both scores and every listed gap can be
  checked against this repo's git history). It does not mean the *current*
  state of the repo has been independently rated - per the skill's own
  anti-priming rule, a past score is not evidence about the present. If you
  want a current number, run `/rate` yourself.

## Why this file exists

Because [check_rating.py](rate/scripts/check_rating.py) and
[SKILL.md](rate/SKILL.md) hold every other target to a disclosure standard,
and a tool that enforces honesty on its targets while staying silent about
itself would be exactly the kind of gap this skill exists to catch.
