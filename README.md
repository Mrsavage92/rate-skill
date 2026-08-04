# /rate

[![Tests](https://github.com/Mrsavage92/rate-skill/actions/workflows/tests.yml/badge.svg)](https://github.com/Mrsavage92/rate-skill/actions/workflows/tests.yml)
[![Version](https://img.shields.io/github/v/tag/Mrsavage92/rate-skill?label=version&sort=semver)](https://github.com/Mrsavage92/rate-skill/tags)

A cold 0-100 rating skill built on one rule: the agent that produced the work does not get to score it. A fresh evaluator does.

Point it at code, a landing page, a plan, a prompt, a document, a repository, a design, or another agent skill.

```text
/rate <target>
```

A valid run returns:

1. **A measurable definition of 100/100**
2. **A current score backed by evidence**
3. **An ordered path to 100**, ranked by value compared with execution time

## How it works

The coordinating agent is not allowed to assign, adjust, average, soften, or rewrite the score.

`/rate` requires a fresh evaluator that:

- has not seen the conversation that produced the target
- receives no previous scores or approval claims
- uses the same model capability tier as the producer, or a stronger one, when known
- inspects the actual target before scoring
- supports each area score with evidence

When that separation cannot be created, `/rate` returns:

```text
NEEDS_HUMAN - independent evaluator unavailable
```

The included grader checks whether a report follows the output contract. It cannot prove that a host genuinely launched an isolated evaluator or that the numeric judgment is correct.

## Install

### One command with the clean `/rate` name

Installs the standalone skill to `~/.claude/skills/rate` on Windows, macOS, or Linux:

```bash
npx -y github:Mrsavage92/rate-skill
```

Restart Claude Code, then run:

```text
/rate <target>
```

Run the same command again to update.

Verify the installation:

```bash
npx -y github:Mrsavage92/rate-skill -- --verify
```

Uninstall:

```bash
npx -y github:Mrsavage92/rate-skill -- --uninstall
```

The installer requires Node.js 18 or newer. The installed skill uses Python 3.9 or newer and has no pip dependencies.

### Managed Claude Code plugin

```bash
claude plugin marketplace add Mrsavage92/rate-skill
claude plugin install rate@rate-skill
```

Plugin skills are namespaced, so the explicit command is:

```text
/rate:rate <target>
```

Update later with:

```bash
claude plugin marketplace update rate-skill
claude plugin update rate@rate-skill
```

### Manual fallback

Clone or download the repository, then copy the `rate/` directory into your Claude Code skills folder.

macOS or Linux:

```bash
mkdir -p ~/.claude/skills/rate
cp -R rate/. ~/.claude/skills/rate/
```

Windows PowerShell:

```powershell
$destination = Join-Path $HOME ".claude\skills\rate"
New-Item -ItemType Directory -Force $destination | Out-Null
Copy-Item ".\rate\*" $destination -Recurse -Force
```

## Enforcement tools

The repository includes:

- **Structural grader** - checks required sections, banned phrases, priming acknowledgement, time estimates, and evidence for high scores
- **Cost guard** - warns when a target is too large for one meaningful pass
- **Convergence checker** - compares multiple independent ratings and flags high variance
- **Optional hooks** - can block a response that breaks the output contract
- **Regression tests and evals** - protect the deterministic checks as the skill changes

None of the installation methods automatically wire the optional Stop hook. Follow [rate/hooks/README.md](rate/hooks/README.md) to enable automatic grader enforcement. Without the hook, the coordinating agent must run the grader manually as instructed by [rate/SKILL.md](rate/SKILL.md).

## Other AI agent platforms

The core workflow is in [rate/SKILL.md](rate/SKILL.md). It can be adapted to other agent platforms when they provide:

- reusable instructions or skills
- file or content inspection
- Python execution
- a fresh isolated agent or task call
- an evaluator model capable of making the required judgment

A platform without isolated delegation can use the supporting scripts, but it cannot claim a fully independent rating.

## Example

[docs/example-rate-run.md](docs/example-rate-run.md) shows a real `/rate` output, including its evidence table and path to 100.

## Run the tests

Python regression suite:

```bash
python rate/tests/run_tests.py
```

Expected result:

```text
Result: 22 passed, 0 failed
```

Installer suite:

```bash
node tests/test-installer.js
```

GitHub Actions runs the Python and installer suites across Windows, macOS, and Linux.

## License

[MIT](LICENSE). Use it, fork it, or adapt it for your own workflow.

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md). Security reports are covered in [SECURITY.md](SECURITY.md).
