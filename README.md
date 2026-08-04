# /rate

A cold, unbiased 0-100 rating skill for Claude Code (or any agent harness that supports loadable skills / system-prompt instructions and can run Python).

Point it at anything - a skill, a code module, a landing page, a plan, a prompt, a repo - and it returns three things, in a fixed order, every time:

1. **A concrete, observable definition of 100/100.** Not "feels polished" - measurable thresholds like "Lighthouse mobile >= 95" or "every route passes an axe accessibility scan."
2. **A current score with per-area evidence.** Every number is backed by a specific file:line, observed behavior, or measured value - never a vibe.
3. **An ordered path to 100**, ranked by cost-to-fix vs value, with concrete AI wall-clock time estimates on every item.

## Why this exists

Agentic self-assessment is structurally biased toward "looks good, ship it." This skill exists to be the opposite: it defaults to FIND-BUGS mode rather than VERIFY-SUCCESS, refuses to accept a prior score (from this session or anywhere else) as evidence the target is fine, and bans hedge language and self-praise in its own output.

It backs that up with a real enforcement layer, not just prose the model is supposed to follow:

- **A structural grader** ([rate/scripts/check_rating.py](rate/scripts/check_rating.py)) checks every rating against the contract - required sections, banned phrases, time estimates on every P0 item, evidence required for any score >= 90.
- **A cost guard** ([rate/scripts/cost_guard.py](rate/scripts/cost_guard.py)) warns before rating a target too large for one pass to meaningfully cover.
- **A convergence checker** ([rate/scripts/convergence_check.py](rate/scripts/convergence_check.py)) compares N independent runs against the same target and flags high variance.
- **Optional hooks** ([rate/hooks/](rate/hooks/)) make the grader run automatically and block the turn if a rating fails its own contract, instead of relying on the model to remember.
- **A regression test suite** ([rate/tests/](rate/tests/)) and an **eval set** ([rate/evals/](rate/evals/)) so changes to the skill can be checked against known-good and known-bad behavior.

All bundled scripts are pure Python stdlib - no OS-specific shell syntax - so the enforcement layer runs the same way on Windows, macOS, and Linux.

## Install (Claude Code)

Copy the `rate/` directory into your skills folder:

```bash
cp -r rate ~/.claude/skills/rate
```

Then invoke it with `/rate <target>` - a file path, a directory, a URL, or inline text/prose to evaluate.

Optional: wire the hooks for automatic grader enforcement. See [rate/hooks/README.md](rate/hooks/README.md).

## Install (other agent harnesses)

The skill itself is a single Markdown file ([rate/SKILL.md](rate/SKILL.md)) written as instructions for an LLM agent with file-read and bash/Python execution access. Any harness that can load a system prompt or skill file and let the model run `python scripts/*.py` should work - adjust the install step to wherever your harness looks for skill definitions.

## Requirements

- Python 3.9+ (pure stdlib - no pip installs required for any bundled script)
- An agent with file-read access and the ability to run shell commands
- A model at least as capable as Claude Sonnet for the rating judgment itself (see SKILL.md rule 9) - a lighter/faster model will under-inspect and reproduce the exact overconfidence problem this skill exists to correct

## Verify it works

```bash
cd rate
python tests/run_tests.py
```

Should print `Result: 12 passed, 0 failed`. The suite is fully self-contained - no fixtures or paths outside this repository.

## License

MIT. Use it, fork it, adapt the calibration bands and area templates to your own domain.
