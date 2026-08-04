# Example `/rate` output

This is a shortened excerpt from a real rating of an earlier version of this repository. It is included to show the output format, not to describe the current version.

# rate-skill - cold rating: **78/100**

The core idea and structural grader were working, but the public package still had clear gaps. Two documented scripts were not properly covered by tests, installation required manual copying, and the repository lacked a practical example for new users.

## Evaluation independence

- **Evaluator:** Fresh isolated evaluator
- **Prior scores supplied:** No
- **Originating conversation supplied:** No

## What 100/100 looks like

1. Every bundled script has meaningful regression coverage
2. Installation works with one command on Windows, macOS, and Linux
3. CI passes across the declared Python and Node versions
4. The README accurately explains what the grader can and cannot enforce
5. A new user can see a realistic example before installing

## Area-by-area

| Area | Score | Evidence |
|---|---|---|
| Skill contract | **88** | The independence rules were explicit and failed closed when isolation was unavailable |
| Structural grader | **90** | The grader enforced the required sections, evidence rules, and banned patterns |
| Test coverage | **62** | The convergence checker and cost guard warning path were not covered |
| Installation | **48** | Installation required manually copying the skill directory |
| Documentation | **90** | The README clearly disclosed the limits of deterministic enforcement |

## Path to 100 - ordered by value compared with cost

### P0 - Required

1. Add regression coverage for the untested scripts
2. Add a one-command installer

### P1 - Value multipliers

3. Add a concise real-world example
4. Add basic contribution and security guidance

## Verdict

78/100. The skill worked, but packaging and test coverage stopped it being a strong public release. The first priority was closing those gaps before promoting it more widely.

The repository has changed since this rating. Run `/rate` against the current version for a current assessment.
