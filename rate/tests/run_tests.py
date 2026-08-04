#!/usr/bin/env python3
"""Cross-platform regression test harness for /rate.

The sole canonical test suite — runs everywhere (Windows, macOS, Linux) without
requiring a POSIX shell or any interpreter beyond Python itself. Each test
prints a single line; the script exits with the number of failures (0 = all
pass).

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
    T9  check_rating.py auto-loads .last-prompt.txt when --prompt is omitted
    T10 --no-prompt-file disables the .last-prompt.txt fallback even if it exists
    T11 hooks/rate_capture_prompt.py writes the prompt from stdin JSON
    T12 hooks/rate_grade_gate.py BLOCKS a structurally-failing rating
    T13 hooks/rate_grade_gate.py allows a structurally-passing rating silently
    T14 cost_guard.py WARNs (exit 1) on a file over the LOC threshold
    T15a convergence_check.py converges (exit 0) on close bundled fixture scores
    T15b convergence_check.py flags low convergence (exit 1) under a tight threshold
    T15c convergence_check.py exits 2 on fewer than 2 input paths
    T16 90+ evidence gate accepts code/repo-shaped evidence ("21/21 tests pass", "CI green")

All fixtures are bundled under tests/fixtures/ — this suite has no dependency
on anything outside this repository and runs identically wherever it's cloned.

Usage:
    python run_tests.py
Exit code = number of failed tests.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
GRADER = SKILL_ROOT / "scripts" / "check_rating.py"
COST_GUARD = SKILL_ROOT / "scripts" / "cost_guard.py"
CONVERGENCE_CHECK = SKILL_ROOT / "scripts" / "convergence_check.py"
GRADE_EVALS = SKILL_ROOT / "evals" / "grade_evals.py"
EVALS_JSON = SKILL_ROOT / "evals" / "evals.json"
FIXTURES = SKILL_ROOT / "tests" / "fixtures"
HOOKS = SKILL_ROOT / "hooks"
CAPTURE_PROMPT_HOOK = HOOKS / "rate_capture_prompt.py"
GRADE_GATE_HOOK = HOOKS / "rate_grade_gate.py"
PROMPT_FILE = SKILL_ROOT / ".last-prompt.txt"

# A stray .last-prompt.txt from a prior manual run (it's gitignored, so a fresh
# clone never has one) would make the fallback in T9/T10 non-deterministic and
# could leak into T1-T8's no-prompt calls. Clear it before this run and let
# each test that needs one write and clean up its own.
PROMPT_FILE.unlink(missing_ok=True)


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


def run_with_stdin(cmd: list[str], stdin_text: str) -> tuple[int, str]:
    """Run a python subprocess feeding stdin_text on stdin, capture combined stdout/stderr."""
    proc = subprocess.run(
        [sys.executable, *cmd],
        input=stdin_text,
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

# --- T9: check_rating.py auto-loads .last-prompt.txt when --prompt is omitted ---
print("[T9] check_rating.py falls back to .last-prompt.txt when --prompt is omitted")
priming_prompt = (FIXTURES / "priming_attempted_prompt.txt").read_text(encoding="utf-8")
PROMPT_FILE.write_text(priming_prompt, encoding="utf-8")
rc, out = run([str(GRADER), str(FIXTURES / "minimal_rating.md")])
line = next((ln for ln in out.splitlines() if "priming-acknowledged" in ln), "")
assertion(
    "T9: priming file auto-loaded -> priming-acknowledged FAILs without --prompt",
    "[FAIL]" in line and "priming-acknowledged" in line and "auto-loaded" in out,
    out,
)
PROMPT_FILE.unlink(missing_ok=True)

# --- T10: --no-prompt-file disables the fallback ---
print("[T10] --no-prompt-file disables the .last-prompt.txt fallback")
PROMPT_FILE.write_text(priming_prompt, encoding="utf-8")
rc, out = run([str(GRADER), str(FIXTURES / "minimal_rating.md"), "--no-prompt-file"])
line = next((ln for ln in out.splitlines() if "priming-acknowledged" in ln), "")
assertion(
    "T10: --no-prompt-file -> priming check skipped despite file present",
    "[PASS]" in line and "skipped (no --prompt provided)" in out,
    out,
)
PROMPT_FILE.unlink(missing_ok=True)

# --- T11: rate_capture_prompt.py writes the prompt from stdin JSON ---
print("[T11] rate_capture_prompt.py writes .last-prompt.txt from stdin JSON")
PROMPT_FILE.unlink(missing_ok=True)
stdin_payload = json.dumps({"prompt": "T11 synthetic prompt, rate this out of 100"})
rc, out = run_with_stdin([str(CAPTURE_PROMPT_HOOK)], stdin_payload)
written = PROMPT_FILE.read_text(encoding="utf-8") if PROMPT_FILE.exists() else None
assertion(
    "T11: hook writes exact prompt text, no stdout",
    rc == 0 and written == "T11 synthetic prompt, rate this out of 100" and out.strip() == "",
    f"rc={rc} written={written!r} stdout/stderr={out!r}",
)
PROMPT_FILE.unlink(missing_ok=True)

# --- T12: rate_grade_gate.py BLOCKS a structurally-failing rating ---
print("[T12] rate_grade_gate.py blocks a structurally-failing rating")
bad_rating_text = "# Something — cold rating: **50/100**\n\nNo other required sections at all."
with tempfile.NamedTemporaryFile(
    mode="w", suffix=".jsonl", delete=False, encoding="utf-8"
) as tf:
    transcript_line = json.dumps(
        {"message": {"role": "assistant", "content": [{"type": "text", "text": bad_rating_text}]}}
    )
    tf.write(transcript_line + "\n")
    transcript_path = tf.name
rc, out = run_with_stdin(
    [str(GRADE_GATE_HOOK)], json.dumps({"transcript_path": transcript_path})
)
assertion(
    "T12: malformed /rate-shaped output -> decision=block",
    rc == 0 and '"decision": "block"' in out,
    f"rc={rc}\n{out}",
)
Path(transcript_path).unlink(missing_ok=True)

# --- T13: rate_grade_gate.py allows a structurally-passing rating silently ---
print("[T13] rate_grade_gate.py allows a structurally-passing rating silently")
good_rating_text = (FIXTURES / "minimal_rating.md").read_text(encoding="utf-8")
with tempfile.NamedTemporaryFile(
    mode="w", suffix=".jsonl", delete=False, encoding="utf-8"
) as tf:
    transcript_line = json.dumps(
        {"message": {"role": "assistant", "content": [{"type": "text", "text": good_rating_text}]}}
    )
    tf.write(transcript_line + "\n")
    transcript_path = tf.name
rc, out = run_with_stdin(
    [str(GRADE_GATE_HOOK)], json.dumps({"transcript_path": transcript_path})
)
assertion(
    "T13: well-formed /rate output -> silent allow, no block decision",
    rc == 0 and '"decision"' not in out and out.strip() == "",
    f"rc={rc}\n{out}",
)
Path(transcript_path).unlink(missing_ok=True)
PROMPT_FILE.unlink(missing_ok=True)  # in case T12/T13 or an earlier failure left one behind

# --- T14: cost_guard.py WARNs (exit 1) on a file over the LOC threshold ---
print("[T14] cost_guard.py WARNs on a file over the 2000-LOC threshold")
with tempfile.NamedTemporaryFile(
    mode="w", suffix=".py", delete=False, encoding="utf-8"
) as tf:
    tf.write("\n".join(f"# line {i}" for i in range(2001)))
    big_file = tf.name
rc, out = run([str(COST_GUARD), big_file])
assertion(
    "T14: oversized file -> exit 1 + [cost_guard WARNING]",
    rc == 1 and "[cost_guard WARNING]" in out and "threshold" in out,
    f"rc={rc}\n{out}",
)
Path(big_file).unlink(missing_ok=True)

# --- T15a: convergence_check.py converges on close bundled fixture scores ---
print("[T15a] convergence_check.py converges (exit 0) at the default threshold")
convergence_inputs = [
    str(FIXTURES / "regression_fixture_skill.md"),  # 76
    str(FIXTURES / "regression_fixture_landing_page.md"),  # 71
    str(FIXTURES / "regression_fixture_anti_priming.md"),  # 68
]
rc, out = run([str(CONVERGENCE_CHECK), *convergence_inputs])
assertion(
    "T15a: default threshold (5.0) -> CONVERGED",
    rc == 0 and "[CONVERGED]" in out,
    f"rc={rc}\n{out}",
)

# --- T15b: convergence_check.py flags low convergence under a tight threshold ---
print("[T15b] convergence_check.py flags low convergence (exit 1) under --threshold 1")
rc, out = run([str(CONVERGENCE_CHECK), *convergence_inputs, "--threshold", "1"])
assertion(
    "T15b: threshold 1.0 -> LOW CONVERGENCE",
    rc == 1 and "[LOW CONVERGENCE]" in out,
    f"rc={rc}\n{out}",
)

# --- T15c: convergence_check.py exits 2 on fewer than 2 input paths ---
print("[T15c] convergence_check.py exits 2 with only 1 input path")
rc, out = run([str(CONVERGENCE_CHECK), convergence_inputs[0]])
assertion(
    "T15c: single path -> exit 2, needs at least 2",
    rc == 2 and "at least 2" in out,
    f"rc={rc}\n{out}",
)

# --- T16: 90+ evidence gate accepts code/repo-shaped evidence ---
print("[T16] 90+ evidence gate accepts test-pass ratios and CI-green confirmation")
code_evidence = """# check_rating.py - cold rating: **92/100**

Verified live: 21/21 tests pass in the regression suite, and CI is green across the full matrix.

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
| A | **92** | 21/21 tests pass, confirmed by running the suite directly |
| B | **92** | CI is confirmed green across the declared matrix |
| C | **90** | foo.md:3 |
| D | **91** | foo.md:4 |
| E | **93** | foo.md:5 |

---

## Path to 100

### P0 - Required (92 -> ~96)

1. **Polish.** Specific change. ~30 min. [foo.md](foo.md).

### P1 - Nice-to-have (96 -> ~100)

2. **Final polish.** ~1 hr. [foo.md](foo.md).

---

## Verdict

92/100. T16 fixture: code/repo-shaped evidence (test-pass ratio, CI-green) must satisfy the high-score-evidence gate.
"""
with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as tf:
    tf.write(code_evidence)
    code_evidence_path = tf.name

rc, out = run([str(GRADER), code_evidence_path])
ev_line = next((ln for ln in out.splitlines() if "high-score-evidence" in ln), "")
assertion(
    "T16: '21/21 tests pass' + 'CI green' satisfies the evidence gate",
    "[PASS]" in ev_line and "high-score-evidence" in ev_line,
    out,
)
Path(code_evidence_path).unlink(missing_ok=True)

# --- summary ---
print()
print("===================================")
print(f"Result: {passed} passed, {failed} failed")
print("===================================")
sys.exit(failed)
