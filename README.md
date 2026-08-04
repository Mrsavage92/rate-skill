# /rate

[![Tests](https://github.com/Mrsavage92/rate-skill/actions/workflows/tests.yml/badge.svg)](https://github.com/Mrsavage92/rate-skill/actions/workflows/tests.yml)

A cold 0-100 rating skill built on one rule: the agent that produced the work does not get to score it. A fresh, isolated evaluator does.

Point it at code, a landing page, a plan, a prompt, a document, a repository, a design, or another agent skill.

```text
/rate <target>
```

A valid run returns:

1. **A measurable definition of 100/100**
2. **A current score backed by evidence**
3. **An ordered path to 100**, ranked by value gained versus AI execution time

## The important difference

The coordinating agent is not allowed to assign, adjust, average, soften, or rewrite the score.

`/rate` requires a fresh evaluator that:

- has not seen the conversation that produced the target
- receives no previous scores or approval claims
- uses the same model capability tier as the producer, or a stronger one, when the producer model is known
- uses at least a Sonnet-equivalent reasoning model for non-AI targets
- inspects the actual target before scoring

If the environment cannot create that separation, `/rate` fails closed with:

```text
NEEDS_HUMAN - independent evaluator unavailable
```

It never labels a same-session self-review as independent.

The structural grader checks whether a report follows the output contract. It cannot prove that the host genuinely launched an isolated evaluator or that the numeric judgment is correct. Rating quality still depends on inspection, evaluator capability, domain knowledge, and truthful runtime disclosure.

## What each rating contains

### 1. A measurable 100/100

Not "feels polished" or "looks professional". The evaluator must define observable criteria, such as:

- Lighthouse mobile score of at least 95
- every route passes an accessibility scan
- all public functions have tested error paths
- every action in a plan has an owner and falsifiable completion check

### 2. A score with a paper trail

Every assessment area must cite something inspectable:

- a file and line
- observed behaviour
- a test result
- a measured value
- a relevant external comparator

Prior ratings and claims that the work is finished are not evidence.

### 3. A path to 100

Fixes are ordered by the value they recover compared with the time required. Each item includes a concrete change, affected location, and AI wall-clock estimate.

## Install

Choose either installation route below.

### One command and the clean `/rate` name

This installs the standalone skill to `~/.claude/skills/rate` on Windows, macOS, or Linux:

```bash
npx -y github:Mrsavage92/rate-skill
```

Restart Claude Code, then run:

```text
/rate <target>
```

Run the same command again to update the installation.

Verify it without changing anything:

```bash
npx -y github:Mrsavage92/rate-skill -- --verify
```

Uninstall it:

```bash
npx -y github:Mrsavage92/rate-skill -- --uninstall
```

The installer requires Node.js 18 or newer. The installed skill still uses Python 3.9 or newer and has no pip dependencies.

### Managed Claude Code plugin

Use this route for Claude Code's plugin management and update commands:

```bash
claude plugin marketplace add Mrsavage92/rate-skill
claude plugin install rate@rate-skill
```

The same commands can be run inside Claude Code with a leading `/`.

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

Clone or download this repository, then copy the `rate/` directory into your Claude Code skills folder.

#### macOS or Linux

```bash
mkdir -p ~/.claude/skills/rate
cp -R rate/. ~/.claude/skills/rate/
```

#### Windows PowerShell

```powershell
$destination = Join-Path $HOME ".claude\skills\rate"
New-Item -ItemType Directory -Force $destination | Out-Null
Copy-Item ".\rate\*" $destination -Recurse -Force
```

## Enforcement layer

The repository includes pure Python standard-library tooling:

- **Structural grader** - checks required sections, banned phrases, priming acknowledgement, P0 time estimates, and evidence for high scores
- **Cost guard** - warns when a target is too large for one meaningful pass
- **Convergence checker** - compares multiple independent ratings and flags high variance
- **Optional hooks** - can block a response that breaks the output contract
- **Regression tests and evals** - protect the deterministic enforcement layer as the skill changes

For optional post-response enforcement, see [rate/hooks/README.md](rate/hooks/README.md).

## Other agent harnesses

The core skill is [rate/SKILL.md](rate/SKILL.md). It can work in another harness when that environment provides:

- file or content inspection
- Python execution
- a fresh isolated subagent or task call
- a model at least equivalent to Claude Sonnet for the evaluator

A harness without isolated delegation can use the supporting scripts, but it cannot claim a fully independent `/rate` run.

## See it run

[docs/example-rate-run.md](docs/example-rate-run.md) is a real, unedited transcript of `/rate` rating this repository's own `v0.1.0` tag. It shows the output shape, evidence style, and independence-disclosure block a real run produces.

## Requirements

- Python 3.9 or newer
- no pip dependencies
- an agent with file-read and Python execution access
- isolated subagent or task support for independent ratings
- Sonnet-equivalent or stronger evaluator model
- Node.js 18 or newer only when using the one-command installer

## Run the tests

Python regression suite:

```bash
python rate/tests/run_tests.py
```

Expected result:

```text
Result: 21 passed, 0 failed
```

Installer suite:

```bash
node tests/test-installer.js
```

GitHub Actions runs the Python suite across Python 3.9 and 3.13, plus the installer suite across Node 18 and 22, on Windows, macOS, and Linux.

The deterministic tests cannot verify the behaviour of a model host or prove that an isolated evaluator was actually launched.

## License

[MIT](LICENSE). Use it, fork it, or adapt the calibration rules and target-specific assessment areas for your own workflow.

## Project

[PROVENANCE.md](PROVENANCE.md) discloses how this repo was built and verified. See [CONTRIBUTING.md](CONTRIBUTING.md) before sending a change, and [SECURITY.md](SECURITY.md) to report a vulnerability.
