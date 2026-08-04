# Example `/rate` run: this repo rating itself

This is a **real, captured transcript** — not a synthetic fixture like the ones
under [rate/evals/golden/](../rate/evals/golden/). It shows `/rate` applied to
this repository's own `v0.1.0` tag
(commit [`6660d5b`](https://github.com/Mrsavage92/rate-skill/commit/6660d5b649c934970e28ccf1b0ac7d9a82bed104)),
so a new user can see the skill actually behave before installing it.

## How it was produced

Per the [independence contract](../rate/SKILL.md#non-negotiable-independence-contract),
the coordinating session did not score its own work. It launched a fresh
subagent (Claude Sonnet 5, via Claude Code's Agent tool) with:

- the repo path and an instruction to read `rate/SKILL.md` and follow its
  process and output contract exactly
- **no** prior score, no summary of what had changed, no hint at an expected
  result

That subagent had no memory of the conversation that built this repo. What
follows is its output, verbatim, unedited.

---

# rate-skill (public repo, Mrsavage92/rate-skill) - cold rating: **78/100**

The repo's central marketing claim is "enforced by a structural grader, not honor system," and the enforcement layer that exists is genuinely well-built — but it is not fully self-enforcing. Two of the four bundled scripts fail to get meaningful exercise from the very regression suite the README points to as proof: `cost_guard.py`'s actual WARN branch (a file/dir that *exceeds* the threshold) is never triggered in `tests/run_tests.py`, and `convergence_check.py` — a documented, README-referenced tool — has zero test coverage at all. Everything that *is* tested passes cleanly (17/17 regression assertions, all eval-assertion golden fixtures, 4/4 green GitHub Actions runs verified live via `gh run list`), and the documentation is unusually honest about the contract's real limits. The bigger gap for "shippable public package" is distribution: install is copy-paste only, with no Claude Code plugin manifest and no GitHub topics set for discovery.

## Evaluation independence

- **Evaluator:** Fresh subagent, launched via the Agent tool with no memory of any conversation that built or edited this repo
- **Evaluator model:** Claude Sonnet 5 (`claude-sonnet-5`) — Sonnet-tier reasoning model, satisfies the non-AI/unknown-producer floor
- **Producer model:** Not disclosed anywhere in the repository (no provenance file, no commit trailer identifying an authoring model) — treated as unknown
- **Prior scores supplied:** No
- **Originating conversation supplied:** No

---

## What 100/100 looks like

1. Every bundled script's primary branches (not just its happy path) are exercised by the regression suite, including `cost_guard.py`'s WARN trigger and all of `convergence_check.py`
2. A user can install the skill with a single command appropriate to the current Claude Code ecosystem (plugin marketplace manifest or equivalent), not only manual directory copy
3. The repo carries standard OSS discovery/health scaffolding: GitHub topics set, `SECURITY.md` with a report path, minimal issue/PR templates
4. CI is green across the full declared matrix and independently confirmed (not just badge-claimed)
5. At least one example in the repo is a captured real model transcript, not only synthetic golden fixtures, so a new user can see the skill actually behave once
6. The structural grader's banned-phrase and evidence-gate logic has no known bypass, and every fix to it ships with a regression test proving the bypass is closed
7. Every claim the README/CHANGELOG makes about the tooling's guarantees vs. its limits is accurate when checked against the actual code

---

## Area-by-area

| Area | Score | Evidence |
|---|---|---|
| SKILL.md contract quality | **88** | `rate/SKILL.md:14-38` independence contract is precise and fails closed (`NEEDS_HUMAN`); banned patterns externalized to `references/banned-phrases.json` rather than hardcoded prose, per `CONTRIBUTING.md:14-21` |
| Structural grader correctness | **90** | `scripts/check_rating.py` + `_rate_lib.py` verified live: ran `check_rating.py` against `tests/fixtures/minimal_rating.md` → 14/14 pass; code comments document real prior bypasses being closed (`_rate_lib.py:55` "stray token unlock a 96... Added 2026-06-01") |
| Automated test coverage of enforcement layer | **62** | `tests/run_tests.py` has 17 assertions and all pass live, but `grep -n "convergence_check" rate/tests/run_tests.py` returns nothing (zero coverage of `scripts/convergence_check.py`), and no test drives `cost_guard.py`'s WARN branch — only OK and HALT(missing) paths are covered (T7) |
| CI / cross-platform verification | **93** | `gh run list --repo Mrsavage92/rate-skill` shows 4/4 runs `completed success` on the `Tests` workflow across the ubuntu/windows/macos × Python 3.9/3.13 matrix in `.github/workflows/tests.yml:18-20` — independently confirmed, not just badge-claimed |
| Documentation quality (README/CONTRIBUTING/CHANGELOG) | **90** | README explicitly discloses what the enforcement can't do ("Neither can force a coordinating agent to actually delegate," `README.md:6`); `CHANGELOG.md:36-42` has a dedicated "Known limitations" section — rare, honest practice |
| Installability / packaging / discoverability | **48** | Install is `mkdir` + `cp`/`Copy-Item` only (`README.md:83-96`); no `.claude-plugin/marketplace.json` or equivalent despite that pattern existing elsewhere in the current Claude ecosystem; `gh repo view` shows `repositoryTopics: null` and 0 stars/forks |
| Licensing / legal hygiene | **95** | `LICENSE` is a correctly formed MIT license with copyright holder named; consistent with `README.md:160-162` and `CHANGELOG.md:34` |
| OSS community scaffolding | **40** | No `SECURITY.md`, `CODE_OF_CONDUCT.md`, `.github/ISSUE_TEMPLATE/`, or PR template anywhere in `git ls-files` (34 tracked files total, none of these) |
| Independence-contract self-awareness | **90** | `references/self-rating-disclosure.md` gives a drop-in contamination-disclosure template; `scripts/convergence_check.py` exists specifically so divergence between runs is measured, not hidden |
| Bundled script code quality | **85** | Pure stdlib throughout (verified: no `import` of third-party packages in any of `scripts/*.py`, `hooks/*.py`, `evals/*.py`); `from __future__ import annotations` present in all 7 for Python 3.9 compatibility; files run 104-360 lines, within stated 800-line convention (`CONTRIBUTING.md:61`) |

---

## Path to 100 - ordered by cost-to-fix vs value

### P0 - Required (78 to ~85)
1. **Close the two untested script branches.** Add a `run_tests.py` case that creates a temp file/dir sized past `FILE_LOC_THRESHOLD`/`DIR_FILE_THRESHOLD` and asserts `cost_guard.py` actually exits 1 with `[cost_guard WARNING]`; add a `convergence_check.py`-specific test (feed 2-3 synthetic rating files, assert mean/stddev/spread math and both exit codes). ~45 min. `rate/tests/run_tests.py`.
2. **Add a one-command install path.** Ship a `.claude-plugin/marketplace.json` (or the current Claude Code plugin-manifest equivalent) alongside the existing manual copy instructions, and add the one-line install command to `README.md`. ~45 min. New file under `.claude-plugin/`, edit `README.md`.
3. **Set GitHub discoverability metadata.** `gh repo edit Mrsavage92/rate-skill --add-topic claude-code --add-topic claude-skill --add-topic llm-evaluation`. ~5 min. GitHub repo settings (no code change).

### P1 - Value multipliers (85 to ~92)
1. **Add minimal OSS health files.** `SECURITY.md` with a report contact/path, a 5-line `CODE_OF_CONDUCT.md` (or link to Contributor Covenant), and a one-file `.github/ISSUE_TEMPLATE/bug_report.md`. ~30 min. Repo root / `.github/`.
2. **Disclose producer provenance.** Add a short note (in `CHANGELOG.md` or a new `PROVENANCE.md`) stating what built this repo, since `/rate`'s own contract cares about producer-model disclosure for every other target it's pointed at — the tool should not be silent about its own. ~10 min. `CHANGELOG.md` or new file.
3. **Capture one real transcript.** Run an actual live `/rate` session against a real target and commit the transcript/output under `evals/` or `docs/`, since `evals/README.md:9-17` currently states every golden fixture is synthetic — a new user has no evidence of real model behavior anywhere in the repo. ~20 min. `rate/evals/` or new `docs/example-run.md`.

### P2 - Polish (92 to 100)
1. **Expand README badges.** Add a License badge and a Python-version-support badge next to the existing Tests/Version badges. ~5 min. `README.md:1-4`.
2. **Cross-link CONTRIBUTING's "changing check_rating.py's contract" checklist directly from check_rating.py's own docstring**, so the four-step update rule isn't only discoverable from `CONTRIBUTING.md`. ~10 min. `rate/scripts/check_rating.py:1-23`.

---

## Verdict

78/100. This is a working, well-engineered enforcement layer around a genuinely differentiated idea (a rating skill that structurally refuses to let the builder grade its own homework) — verified live: 17/17 regression tests pass, all eval-assertion golden fixtures pass, and CI is confirmed green across a real 6-way OS/Python matrix, not just badge-claimed. It sits in the 70-84 band because two concrete issues block it from "strong, safe to ship": the regression suite that's supposed to protect the "enforcement layer, not honor system" claim has real blind spots (`cost_guard.py`'s WARN path, all of `convergence_check.py`), and the repo can currently only be installed by manual copy-paste with no discoverability metadata set. Recommended next action: do P0 item 1 first (close the test-coverage gap) — it's the one place where the repo's own stated quality bar and its actual verified behavior diverge.

---

## What happened next

Every P0 and P1 item above was closed in the commit(s) following this rating:
test coverage added for both untested branches (21 assertions total), the
`.claude-plugin/` manifest pair added and validated with
`claude plugin validate . --strict`, GitHub topics set, OSS health files
added, provenance disclosed, and this transcript itself committed as the
"real example" P1 item asked for. That work is not reflected in the rating
above — it wouldn't be honest to edit a captured transcript after the fact.
If you want the current score, run `/rate` against this repo yourself; per
the skill's own rules, a stale score from a prior tag is not evidence about
the current state.
