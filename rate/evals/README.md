# /rate evals

`evals.json` defines behavioral checks for how a live model, running the `/rate`
skill, should respond to specific prompts (an anti-priming attempt, an
unfetchable target, a cross-domain rating request, and so on). `grade_evals.py`
turns each eval's `assertions` into an executable check against a rating
output.

## `golden/`

`golden/eval-{id}-{name}/rating.md` are **synthetic structural fixtures**, not
captured transcripts from a real model run. Each one is hand-built to satisfy
its eval's assertions, the same way `tests/fixtures/regression_*.md` validates
`check_rating.py`'s structural checks. They exist to keep `grade_evals.py`'s
assertion-checking *logic* under CI regression coverage — regex drift, a typo
in a `check_type`, an assertion that stops matching after a refactor — not to
prove that a live model actually behaves this way when it runs `/rate`.

Verifying real model behavior against `evals.json` requires running an actual
`/rate` session against each prompt and grading the transcript it produces —
a manual step, since it needs a live LLM call this repository's CI does not
make. A real captured transcript (this skill rating its own repo) is
committed at [../../docs/example-rate-run.md](../../docs/example-rate-run.md)
if you want to see actual model behavior before running your own. Run a new
one yourself with:

```bash
python evals/grade_evals.py evals/evals.json --eval-id <id> --output <path-to-real-rating.md>
```

## What CI actually checks

```bash
python evals/grade_evals.py evals/evals.json --all evals/golden
```

This confirms every eval's assertions still parse and match against a
known-good synthetic fixture. It is a regression guard on the eval-grading
code, not a benchmark of the skill's real-world rating quality.
