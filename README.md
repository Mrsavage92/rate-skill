# /rate

A cold 0-100 rating skill that does not let the agent that produced the work mark its own homework.

Point it at code, a landing page, a plan, a prompt, a document, a repository, a design, or another agent skill. A valid run launches a fresh evaluator and returns:

1. **A concrete definition of 100/100** using observable criteria.
2. **A current score with evidence** for every assessment area.
3. **An ordered path to 100** ranked by value gained versus AI execution time.

## The important difference

The coordinating agent is not allowed to assign, adjust, or soften the score.

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

## What each rating contains

### 1. A measurable 100/100

Not "feels polished" or "looks professional". The evaluator must define observable criteria such as:

- Lighthouse mobile score of at least 95
- every route passes an accessibility scan
- all public functions have tested error paths
- every action in a plan has an owner and falsifiable completion check

### 2. A score with a paper trail

Every assessment area must cite something inspectable:

- a file and line
- observed behavior
- a test result
- a measured value
- a relevant external comparator

Prior ratings and claims that the work is finished are not evidence.

### 3. A path to 100

Fixes are ordered by the amount of score and value they recover for the time required. Each item includes a concrete change, affected location, and AI wall-clock estimate.

## Enforcement layer

The repository includes pure Python standard-library tooling:

- **Structural grader** - checks required sections, banned phrases, priming acknowledgement, P0 time estimates, and evidence for high scores
- **Cost guard** - warns when a target is too large for one meaningful pass
- **Convergence checker** - compares multiple independent ratings and flags high variance
- **Optional hooks** - automatically block a response that breaks the output contract
- **Regression tests and evals** - protect the contract as the skill changes

The structural grader checks whether a report follows the contract. It does not prove that the numeric judgment is correct. Rating quality still depends on inspection, evaluator capability, and domain knowledge.

## Install in Claude Code

Copy the `rate/` directory into your skills folder:

```bash
cp -r rate ~/.claude/skills/rate
```

Then run:

```text
/rate <target>
```

The target can be a file path, directory, URL, or inline content.

For automatic post-response enforcement, see [rate/hooks/README.md](rate/hooks/README.md).

## Other agent harnesses

The core skill is [rate/SKILL.md](rate/SKILL.md). It can work in another harness when that environment provides:

- file or content inspection
- Python execution
- a fresh isolated subagent or task call
- a model at least equivalent to Claude Sonnet for the evaluator

A harness without isolated delegation can use the supporting scripts, but it cannot claim a fully independent `/rate` run.

## Requirements

- Python 3.9 or newer
- no pip dependencies
- an agent with file-read and Python execution access
- isolated subagent or task support for independent ratings
- Sonnet-equivalent or stronger evaluator model

## Verify the repository

```bash
cd rate
python tests/run_tests.py
```

Expected result:

```text
Result: 12 passed, 0 failed
```

The suite is self-contained and uses no fixtures outside this repository.

## License

MIT. Use it, fork it, or adapt the calibration rules and target-specific assessment areas for your own workflow.