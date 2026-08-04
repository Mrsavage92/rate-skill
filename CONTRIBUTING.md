# Contributing

## Before you send a change

```bash
python rate/tests/run_tests.py
python rate/evals/grade_evals.py rate/evals/evals.json --all rate/evals/golden
```

Both must exit 0. CI runs the same two commands on Windows, macOS, and Linux
against Python 3.9 and 3.13 — a change that only passes on one OS or one
Python version will fail CI even if it passes locally.

## Adding a banned phrase or priming pattern

Edit [rate/references/banned-phrases.json](rate/references/banned-phrases.json)
only — `check_rating.py`, `grade_evals.py`, and the eval assertions all read
from it via `_rate_lib.load_banned()`, so a pattern added there is
automatically enforced everywhere. Do not hardcode a new pattern directly in
a script; that creates exactly the kind of grader-disagreement bug T5b exists
to catch.

## Adding a regression test

Add a new `T{n}` block to
[rate/tests/run_tests.py](rate/tests/run_tests.py), following the existing
`assertion(name, ok, detail)` pattern. If the test needs a fixture file rather
than an inline string, put it under
[rate/tests/fixtures/](rate/tests/fixtures/). Every fixture must be
self-contained — no path outside this repository — so the suite runs
identically on a fresh clone.

## Adding an eval

Add an entry to [rate/evals/evals.json](rate/evals/evals.json) describing the
prompt and the assertions a correct `/rate` response must satisfy. Then add a
golden fixture at `rate/evals/golden/eval-{id}-{name}/rating.md` that
satisfies those assertions, so `grade_evals.py --all` has something to check
in CI. See [rate/evals/README.md](rate/evals/README.md) for what a golden
fixture proves and what it doesn't.

## Changing `check_rating.py`'s contract

If you change what the structural grader requires (a new mandatory section, a
new banned category, a different evidence threshold), update in the same
change:

1. [rate/SKILL.md](rate/SKILL.md) — the contract description the model reads
2. [rate/scripts/check_rating.py](rate/scripts/check_rating.py) — the enforcement
3. [rate/tests/run_tests.py](rate/tests/run_tests.py) — a test proving the new rule actually fires
4. [rate/tests/fixtures/](rate/tests/fixtures/) or `regression_fixture_*.md` — update any fixture the new rule would now fail

A contract change that updates only the prose (step 1) without the code (step
2) is not a real change — see [README.md](README.md#the-important-difference)
for why that gap matters here specifically.

## Style

Pure Python stdlib in every bundled script — no pip dependencies, no
shell-outs, no OS-specific syntax. UTF-8 explicit on every file read/write.
Keep functions under ~50 lines and files under ~800.
