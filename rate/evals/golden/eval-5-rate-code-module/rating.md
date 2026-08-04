# check_rating.py - cold rating: **77/100**

Golden eval fixture standing in for a "rate a Python utility module" scenario. Synthetic content built to satisfy eval-5's assertions, not a live model transcript.

---

## What 100/100 looks like

1. Every public function has a docstring describing inputs, outputs, and exit-code contract
2. Every check function has at least one direct regression test
3. No function exceeds 50 lines
4. Cross-platform behavior is verified, not just claimed in a comment
5. Type hints are present on every public function signature
6. Error handling never silently swallows a malformed input
7. Naming is consistent between the CLI flags and the internal variables they populate

---

## Area-by-area

| Area | Score | Evidence |
|---|---|---|
| Public API ergonomics | **80** | check_rating.py:286 - `main()` has a clear single entry point with `--prompt`, `--no-prompt-file`, `--json` flags |
| Test coverage | **74** | check_rating.py:63 - `check_headline_score` has direct coverage via the regression suite |
| Error handling | **78** | check_rating.py:301 - missing file path returns exit 2 with a clear stderr message rather than raising |
| Naming | **76** | Consistent `check_*` prefix across all check functions |
| Cross-platform | **80** | Pure stdlib, `pathlib`-based, UTF-8 explicit reads and writes throughout |

---

## Path to 100 - ordered by cost-to-fix vs value

### P0 - Required (77 -> ~85)

1. **Add type hints to every check function's return value.** Several functions rely on inference rather than an explicit `-> CheckResult` annotation. ~20 min. [check_rating.py](check_rating.py).

### P1 - Nice-to-have (85 -> ~92)

2. **Add a one-line docstring to every `check_*` function** describing exactly which rule it enforces. ~25 min. [check_rating.py](check_rating.py).

---

## Verdict

77/100. Golden fixture used only to test the eval-assertion logic end to end; no real target was inspected.
