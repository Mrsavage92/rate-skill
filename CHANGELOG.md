# Changelog

All notable changes to this project are documented here. Format loosely
follows [Keep a Changelog](https://keepachangelog.com/).

## [0.1.2] - 2026-08-04

Prompted by a third independent cold rating (81/100, fresh subagent, no
prior context) run against the tagged `v0.1.1` state.

### Fixed

- The 90+ evidence gate (`evidence_markers_for_high_scores` in
  `rate/references/banned-phrases.json`) was entirely web-performance-shaped
  (Lighthouse/LCP/INP/CLS/ms/kb/axe) with no pattern matching code/repo-shaped
  evidence like test-pass ratios or CI-green confirmation — meaning a
  legitimately well-evidenced 90+ rating of a code repo or skill (this one
  included) could not structurally pass the tool's own contract. Added
  code/repo-shaped markers and a regression test (T16; 21 -> 22 assertions).
- README's manual-install path implied grader enforcement happens
  automatically. It doesn't, unless the `Stop` hook is also wired - the exact
  honor-system gap this skill exists to close elsewhere. Now disclosed
  explicitly in the install section.

### Added

- `.github/PULL_REQUEST_TEMPLATE.md` restating the pre-PR checklist from
  `CONTRIBUTING.md` in the PR UI itself.

## [0.1.1] - 2026-08-04

Prompted by a second independent cold rating (78/100, fresh subagent, no
prior context) run against the tagged `v0.1.0` state - see
[docs/example-rate-run.md](docs/example-rate-run.md) for the full transcript.

### Added

- One-command plugin install: `.claude-plugin/marketplace.json` and
  `.claude-plugin/plugin.json`, validated with
  `claude plugin validate . --strict`. Manual copy-paste install kept as a
  documented fallback for locked-down environments.
- Test coverage for the two branches the second rating found untested:
  `cost_guard.py`'s WARN path and all of `convergence_check.py` (4 new
  assertions; 17 -> 21).
- `docs/example-rate-run.md` - a real, unedited `/rate` transcript (not a
  synthetic fixture) so a new user can see actual model behavior before
  installing.
- `SECURITY.md`, `CODE_OF_CONDUCT.md`, `.github/ISSUE_TEMPLATE/bug_report.md`.
- `PROVENANCE.md` disclosing how this repo was built and independently
  verified, since `/rate`'s own contract asks every target it rates to
  disclose the same.
- GitHub topics set for discoverability (`claude-code`, `claude-code-skill`,
  `llm-evaluation`, `ai-agents`, `prompt-engineering`).

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
