---
name: Bug report
about: Something in /rate's scripts, hooks, or contract behaved incorrectly
title: ''
labels: bug
assignees: ''
---

**What happened**
A clear description of the incorrect behavior.

**Which piece**
- [ ] `scripts/check_rating.py` (structural grader)
- [ ] `scripts/cost_guard.py`
- [ ] `scripts/convergence_check.py`
- [ ] `hooks/rate_capture_prompt.py` or `hooks/rate_grade_gate.py`
- [ ] `evals/grade_evals.py` or an eval/golden fixture
- [ ] `SKILL.md` process/contract itself
- [ ] Something else

**Steps to reproduce**
Exact command(s) run, or the rating/prompt text that triggered the issue.
Attach the offending rating.md if the bug is grader-related - the grader's
own reasoning depends on exact text, so a paraphrase often won't reproduce it.

**Expected vs actual**
What should have happened vs what did.

**Environment**
- OS:
- Python version (`python --version`):
- Claude Code version (`claude --version`), if relevant:
