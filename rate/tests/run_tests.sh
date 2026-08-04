#!/usr/bin/env bash
# Run grader correctness tests. Cross-platform: bash on Unix, Git Bash / WSL on Windows.
# Verifies:
#   T1: Benign prompt with "100/100" does NOT trigger spurious priming acknowledgement requirement
#   T2: Priming prompt with "previously scored 80/80" DOES require acknowledgement
#   T3a: Real used self-praise ("thorough analysis") IS caught
#   T3b: Negated self-praise ("not a comprehensive review") IS exempted (it's self-criticism)
#   T4: The 3 bundled regression fixtures still grade 14/14 (regression guard)
# All fixtures are bundled under tests/fixtures/ — no dependency outside this repo.
set -u
fail=0
pass=0
SKILL_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
GRADER="${SKILL_ROOT}/scripts/check_rating.py"

note() { echo "[test] $*"; }
must_pass() { ((pass+=1)); echo "  PASS: $*"; }
must_fail() { ((fail+=1)); echo "  FAIL: $*"; }

# --- T1: benign prompt should NOT require priming-acknowledged ---
note "T1: benign prompt with '100/100' should pass without priming acknowledgement"
PROMPT="$(cat "${SKILL_ROOT}/tests/fixtures/priming_benign_prompt.txt")"
OUT=$(python "${GRADER}" "${SKILL_ROOT}/tests/fixtures/minimal_rating.md" --prompt "${PROMPT}" 2>&1)
if echo "${OUT}" | grep "priming-acknowledged" | grep -q "PASS"; then
  must_pass "T1: benign prompt passes priming check (no false positive)"
else
  must_fail "T1: benign prompt incorrectly flagged"
  echo "${OUT}" | grep -A1 "priming-acknowledged"
fi

# --- T2: priming prompt without acknowledgement should FAIL ---
note "T2: priming prompt without acknowledgement should fail priming check"
PROMPT="$(cat "${SKILL_ROOT}/tests/fixtures/priming_attempted_prompt.txt")"
OUT=$(python "${GRADER}" "${SKILL_ROOT}/tests/fixtures/minimal_rating.md" --prompt "${PROMPT}" 2>&1)
if echo "${OUT}" | grep "priming-acknowledged" | grep -q "FAIL"; then
  must_pass "T2: priming prompt correctly flagged as unacknowledged"
else
  must_fail "T2: priming prompt was NOT flagged"
  echo "${OUT}" | grep -A1 "priming-acknowledged"
fi

# --- T3a: real used self-praise should be CAUGHT ---
note "T3a: 'thorough analysis' used as praise should fail banned-self-praise"
OUT=$(python "${GRADER}" "${SKILL_ROOT}/tests/fixtures/self_praise_used.md" 2>&1)
if echo "${OUT}" | grep "no-banned-self-praise" | grep -q "FAIL"; then
  must_pass "T3a: used self-praise correctly caught"
else
  must_fail "T3a: used self-praise NOT caught"
  echo "${OUT}" | grep -A1 "no-banned-self-praise"
fi

# --- T3b: negated self-praise should be EXEMPTED ---
note "T3b: 'not a comprehensive review' should pass (self-criticism, not self-praise)"
OUT=$(python "${GRADER}" "${SKILL_ROOT}/tests/fixtures/self_praise_correctly_negated.md" 2>&1)
if echo "${OUT}" | grep "no-banned-self-praise" | grep -q "PASS"; then
  must_pass "T3b: negated self-praise correctly exempted"
else
  must_fail "T3b: negated phrase wrongly flagged as self-praise"
  echo "${OUT}" | grep -A1 "no-banned-self-praise"
fi

# --- T4: bundled regression fixtures still grade clean ---
note "T4: bundled regression fixtures still pass 14/14"
for fixture_name in regression_fixture_skill.md regression_fixture_anti_priming.md regression_fixture_landing_page.md; do
  RATING_PATH="${SKILL_ROOT}/tests/fixtures/${fixture_name}"
  if [ ! -f "${RATING_PATH}" ]; then
    must_fail "T4: ${fixture_name} not found at ${RATING_PATH}"
    continue
  fi
  result=$(python "${GRADER}" "${RATING_PATH}" 2>&1 | tail -1)
  if echo "${result}" | grep -q "14/14"; then
    must_pass "T4: ${fixture_name} -> 14/14"
  else
    must_fail "T4: ${fixture_name} -> ${result}"
  fi
done

echo
echo "==================================="
echo "Result: ${pass} passed, ${fail} failed"
echo "==================================="
[ "${fail}" -eq 0 ]
