## What changed and why

<!-- The why matters more than the what — the diff already shows what changed. -->

## Pre-PR checklist

Both of these must exit 0 before this PR is ready for review (see [CONTRIBUTING.md](../CONTRIBUTING.md)):

```bash
python rate/tests/run_tests.py
python rate/evals/grade_evals.py rate/evals/evals.json --all rate/evals/golden
```

- [ ] Ran both commands above locally and they passed
- [ ] If this changes what `check_rating.py` requires, updated all four places [CONTRIBUTING.md](../CONTRIBUTING.md#changing-check_ratingpys-contract) lists: SKILL.md, the script, a regression test, and any fixture the new rule would now fail
- [ ] If this adds a banned phrase or priming pattern, it went into [rate/references/banned-phrases.json](../rate/references/banned-phrases.json), not hardcoded in a script

CI runs the same two commands across Windows/macOS/Linux x Python 3.9/3.13 — a change that only passes on one OS or Python version will fail here even if it passed locally.
