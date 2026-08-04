# Changelog

All notable changes to this project are documented here. Format loosely
follows [Keep a Changelog](https://keepachangelog.com/).

## [0.1.0] - 2026-08-04

Initial public release.

### Added

- `/rate` skill ([rate/SKILL.md](rate/SKILL.md)): cold, independently-delegated
  0-100 rating with a fixed output contract (measurable 100/100 definition,
  evidence-backed area scores, cost-ranked path to 100).
- Non-negotiable independence contract: the coordinating agent must delegate
  scoring to a fresh evaluator and may not assign, adjust, or soften the
  score itself; fails closed with `NEEDS_HUMAN` when that separation can't be
  established.
- Structural grader (`scripts/check_rating.py`) enforcing shape, banned
  phrases, priming acknowledgement, P0 time estimates, and the 90+
  evidence-required rule.
- Priming-check auto-fallback: `--prompt` can be omitted if
  `.last-prompt.txt` is present, closing the gap where a coordinator could
  silently skip the anti-priming check.
- Cost guard (`scripts/cost_guard.py`) and convergence checker
  (`scripts/convergence_check.py`).
- Optional cross-platform Python hooks (`hooks/`) for automatic grader
  enforcement in Claude Code or any harness with equivalent hook points.
- Cross-platform regression suite (`tests/run_tests.py`, 17 assertions),
  fully self-contained — no fixtures or paths outside this repository.
- Eval suite (`evals/`) with synthetic golden fixtures keeping the
  assertion-checking logic under CI regression coverage.
- GitHub Actions matrix: Windows/macOS/Linux x Python 3.9/3.13.
- MIT license.

### Known limitations (see [README.md](README.md#the-important-difference))

- The independence contract is enforced by instruction and by the structural
  grader's output checks, not by anything the tooling can use to verify a
  coordinating agent actually launched an isolated evaluator.
- The eval suite's golden fixtures are synthetic, not captured live-model
  transcripts — they validate the grading logic, not real model behavior.
