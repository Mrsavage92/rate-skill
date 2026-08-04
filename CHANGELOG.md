# Changelog

Notable changes to `/rate` are recorded here.

## [0.1.3] - 2026-08-04

### Added

- Published GitHub releases for the existing version tags
- Added command metadata and an argument hint to `rate/SKILL.md`
- Added API endpoint eval coverage and a matching golden fixture

## [0.1.2] - 2026-08-04

### Added

- One-command cross-platform installation with:

  ```bash
  npx -y github:Mrsavage92/rate-skill
  ```

- Safe install, update, verify, and uninstall flows
- Installer tests across Windows, macOS, and Linux on Node 18 and 22
- npm package metadata for direct execution from GitHub
- Pull request template

### Fixed

- Expanded the high-score evidence gate to recognise code and repository evidence such as passing tests and green CI
- Clarified that automatic grader enforcement requires the optional Stop hook
- Prevented Python cache files from entering the npm package

## [0.1.1] - 2026-08-04

### Added

- Claude Code marketplace and plugin manifests
- Test coverage for the cost guard warning path and convergence checker
- Real example rating output under `docs/`
- Security policy, contribution guidance, issue template, and code of conduct
- GitHub repository topics for discoverability

## [0.1.0] - 2026-08-04

### Added

- `/rate` skill with an independent evaluator contract
- Measurable 100/100 definition, evidence-backed scoring, and a ranked path to 100
- Structural grader, cost guard, convergence checker, and optional hooks
- Cross-platform regression tests and eval fixtures
- GitHub Actions test matrix
- MIT licence

## Known limitations

- The deterministic tooling cannot prove that a host actually launched an isolated evaluator
- Structural checks cannot prove that the evaluator's numeric judgment is correct
- Golden eval fixtures validate the assertion logic, not live model behaviour
