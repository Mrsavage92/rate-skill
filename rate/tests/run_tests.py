#!/usr/bin/env python3
"""Cross-platform regression test harness for /rate.

Mirrors run_tests.sh but runs everywhere — PowerShell on Windows, bash on Unix —
without requiring a POSIX shell. Each test prints a single line; the script exits
with the number of failures (0 = all pass).

Test coverage:
    T1  Benign prompt with `100/100` does NOT trigger spurious priming flag (P0 #1)
    T2  Priming prompt without acknowledgement DOES fail priming check
    T3a Real used self-praise ('thorough analysis') IS caught
    T3b Negated self-praise ('not a comprehensive review') IS exempted
    T4  Bundled regression fixtures still grade 14/14 (structural-pass regression guard)
    T5a grade_evals.py runs without crash even when no rating outputs exist for some evals
    T5b grade_evals.py and check_rating.py agree on quote-aware logic (no graders-disagree)
    T6  Bulleted P0 items are detected by check_p0_has_time_estimates
    T7  cost_guard.py on a missing target exits 2 / HALT (not a silent "OK")
    T8  90+ evidence gate is NOT satisfied by a marker token in the Verdict prose

All fixtures are bundled under tests/fixtures/ — this suite has no dependency
on anything outside this repository and runs identically wherever it's cloned.

Usage:
    python run_tests.py
Exit code = number of failed tests.
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
GRADER = SKILL_ROOT / "scripts" / "check_rating.py"
COST_GUARD = SKILL_ROOT / "scripts" / "cost_guard.py"
GRADE_EVALS = SKILL_ROOT / "evals" / "grade_evals.py"
EVALS_JSON = SKILL_ROOT / "evals" / "evals.json"
FIXTURES = SKILL_ROOT / "tests" / "fixtures"


def run(cmd: list[str]) -> tuple[int, str]:
    """Run a python subprocess and capture combined stdout/stderr."""
    proc = subprocess.run(
        [sys.executable, *cmd],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


passed = 0
failed = 0


def assertion(name: str, ok: bool, detail: str = "") -> None:
    global passed, failed
    mark = "PASS" if ok else "FAIL"
    print(f"  {mark}: {name}")
    if not ok and detail:
        for line in detail.splitlines()[:5]:
            print(f"        {line}")
    if ok:
        passed += 1
    else:
        failed += 1


# --- T1: benign prompt should NOT require priming-acknowledged ---
print("[T1] benign '100/100' prompt should pass priming check")
prompt = (FIXTURES / "priming_benign_prompt.txt").read_text(encoding="utf-8")
_, out = run([str(GRADER), str(FIXTURES / "minimal_rating.md"), "--prompt", prompt])
line = next((ln for ln in out.splitlines() if "priming-acknowledged" in ln), "")
assertion(
    "T1: benign prompt -> PASS",
    "[PASS]" in line and "priming-acknowledged" in line,
    out,
)

# --- T2: priming prompt without acknowledgement should FAIL ---
print("[T2] priming prompt without ack should fail priming check")
prompt = (FIXTURES / "priming_attempted_prompt.txt").read_text(encoding="utf-8")
_, out = run([str(GRADER), str(FIXTURES / "minimal_rating.md"), "--prompt", prompt])
line = next((ln for ln in out.splitlines() if "priming-acknowledged" in ln), "")
assertion(
    "T2: priming prompt without ack -> FAIL",
    "[FAIL]" in line and "priming-acknowledged" in line,
    out,
)

# --- T3a: real used self-praise should be CAUGHT ---
print("[T3a] used self-praise ('thorough analysis') should be flagged")
_, out = run([str(GRADER), str(FIXTURES / "self_praise_used.md")])
line = next((ln for ln in out.splitlines() if "no-banned-self-praise" in ln), "")
assertion(
    "T3a: used self-praise -> FAIL",
    "[FAIL]" in line and "no-banned-self-praise" in line,
    out,
)

# --- T3b: negated self-praise should be EXEMPTED ---
print("[T3b] negated self-praise ('not a comprehensive review') should pass")
_, out = run([str(GRADER), str(FIXTURES / "self_praise_correctly_negated.md")])
line = next((ln for ln in out.splitlines() if "no-banned-self-praise" in ln), "")
assertion(
    "T3b: negated self-praise -> PASS",
    "[PASS]" in line and "no-banned-self-praise" in line,
    out,
)

# --- T4: bundled regression fixtures still grade 14/14 ---
print("[T4] bundled regression fixtures should still grade 14/14")
for fixture_name in (
    "regression_fixture_skill.md",
    "regression_fixture_anti_priming.md",
    "regression_fixture_landing_page.md",
):
    rating = FIXTURES / fixture_name
    if not rating.exists():
        assertion(f"T4: {fixture_name} present", False, f"not found at {rating}")
        continue
    _, out = run([str(GRADER), str(rating)])
    summary = next((ln for ln in out.splitlines() if "Result:" in ln), "")
    assertion(f"T4: {fixture_name} -> 14/14", "14/14" in summary, out)

# --- T5a: grade_evals.py handles missing outputs cleanly ---
print("[T5a] grade_evals.py --all on a tmp empty dir exits cleanly")
with tempfile.TemporaryDirectory() as tmp:
    rc, out = run([str(GRADE_EVALS), str(EVALS_JSON), "--all", tmp])
    # No outputs means every eval is SKIP. Should not crash. Exit code 0 (no failures).
    assertion(
        "T5a: empty dir produces SKIPs without crash",
        rc == 0 and "SKIP" in out,
        out,
    )

# --- T5b: graders agree on quoted phrases ---
print("[T5b] check_rating.py and grade_evals.py agree on quote-aware exemption")
# Build a synthetic rating that quotes a banned phrase and run both graders.
# The fixture minimal_rating.md does not quote banned phrases, so we synthesize one inline.
synthetic = """# T5b synthetic — cold rating: **74/100**

This rating discusses the banned phrase "thorough analysis" only in a quoted reference, not as self-praise.

---

## What 100/100 looks like

1. one
2. two
3. three
4. four
5. five
6. six
7. seven

---

## Area-by-area

| Area | Score | Evidence |
|---|---|---|
| A | **70** | foo.md:1 |
| B | **72** | foo.md:2 |
| C | **74** | foo.md:3 |
| D | **76** | foo.md:4 |
| E | **78** | foo.md:5 |

---

## Path to 100

### P0 — Required (74 -> ~82)

1. **Fix.** Specific change. ~30 min. [foo.md](foo.md).

### P1 — Nice-to-have (82 -> ~90)

2. **Another fix.** ~1 hr. [foo.md](foo.md).

---

## Verdict

74/100. T5b verifies the two graders agree on quoted references.
"""
with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as tf:
    tf.write(synthetic)
    synth_path = tf.name

rc_struct, out_struct = run([str(GRADER), synth_path])
# Run eval 1's regex_not_present assertion via grade_evals.py
rc_eval, out_eval = run([str(GRADE_EVALS), str(EVALS_JSON), "--eval-id", "1", "--output", synth_path])

struct_self_praise_pass = "[PASS] no-banned-self-praise" in out_struct
eval_self_praise_assertion = re.search(
    r"\[(PASS|FAIL)\] no-banned-self-praise", out_eval
)
eval_passes_self_praise = (
    eval_self_praise_assertion is not None and eval_self_praise_assertion.group(1) == "PASS"
)
assertion(
    "T5b: both graders treat quoted 'thorough analysis' as exempt",
    struct_self_praise_pass and eval_passes_self_praise,
    f"check_rating self-praise: {struct_self_praise_pass}\n"
    f"grade_evals self-praise: {eval_passes_self_praise}\n\n--- check_rating ---\n{out_struct}\n\n--- grade_evals ---\n{out_eval}",
)
Path(synth_path).unlink(missing_ok=True)

# --- T6: bulleted P0 items detected ---
print("[T6] check_p0_has_time_estimates supports bulleted P0 items")
bulleted = """# T6 bulleted P0 fixture — cold rating: **74/100**

Headline.

---

## What 100/100 looks like

1. one
2. two
3. three
4. four
5. five
6. six
7. seven

---

## Area-by-area

| Area | Score | Evidence |
|---|---|---|
| A | **70** | foo.md:1 |
| B | **72** | foo.md:2 |
| C | **74** | foo.md:3 |
| D | **76** | foo.md:4 |
| E | **78** | foo.md:5 |

---

## Path to 100

### P0 — Required (74 -> ~82)

- **First fix.** Specific change. ~30 min. [foo.md](foo.md).
- **Second fix.** Another specific change. ~45 min. [foo.md](foo.md).

### P1 — Nice-to-have (82 -> ~90)

- **Third fix.** ~1 hr. [foo.md](foo.md).

---

## Verdict

74/100. T6 fixture: bulleted items must be detected.
"""
with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as tf:
    tf.write(bulleted)
    bul_path = tf.name

rc, out = run([str(GRADER), bul_path])
p0_line = next((ln for ln in out.splitlines() if "p0-time-estimates" in ln), "")
assertion(
    "T6: bulleted P0 items detected (not silently skipped)",
    "[PASS]" in p0_line and "all 2 P0 items" in out,
    out,
)
Path(bul_path).unlink(missing_ok=True)

# --- T7: cost_guard on a missing target must HALT (exit 2), not silently pass ---
print("[T7] cost_guard.py on a missing target should exit 2 / HALT")
missing = str(SKILL_ROOT / "this-path-does-not-exist-zzz")
rc, out = run([str(COST_GUARD), missing])
assertion(
    "T7: missing target -> exit 2 + HALT (not '[cost_guard OK]')",
    rc == 2 and "HALT" in out and "[cost_guard OK]" not in out,
    f"rc={rc}\n{out}",
)

# --- T8: 90+ evidence gate must NOT be satisfied by a marker token in the Verdict ---
print("[T8] 90+ evidence marker buried in the Verdict should NOT satisfy the gate")
bypass = """# T8 bypass fixture — cold rating: **96/100**

Headline with no measured evidence in the assessment itself.

---

## What 100/100 looks like

1. one
2. two
3. three
4. five
5. six
6. seven
7. eight

---

## Area-by-area

| Area | Score | Evidence |
|---|---|---|
| A | **95** | foo.md:1 |
| B | **96** | foo.md:2 |
| C | **95** | foo.md:3 |
| D | **96** | foo.md:4 |
| E | **95** | foo.md:5 |

---

## Path to 100

### P0 — Required (96 -> ~98)

- **Fix.** Specific change. ~30 min. [foo.md](foo.md).

### P1 — Nice-to-have (98 -> ~100)

- **Polish.** ~1 hr. [foo.md](foo.md).

---

## Verdict

96/100. This needs convergence testing eventually and a 200 ms latency check.
"""
with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as tf:
    tf.write(bypass)
    bypass_path = tf.name

rc, out = run([str(GRADER), bypass_path])
ev_line = next((ln for ln in out.splitlines() if "high-score-evidence" in ln), "")
assertion(
    "T8: marker in Verdict does NOT unlock a 96 (gate must FAIL)",
    "[FAIL]" in ev_line and "high-score-evidence" in ev_line,
    out,
)
Path(bypass_path).unlink(missing_ok=True)

# --- summary ---
print()
print("===================================")
print(f"Result: {passed} passed, {failed} failed")
print("===================================")
sys.exit(failed)
