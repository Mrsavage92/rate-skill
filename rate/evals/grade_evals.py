#!/usr/bin/env python3
"""Eval grader for /rate.

Reads evals.json, runs every assertion's check_type against a corresponding rating
output file, and reports pass/fail per assertion. This makes evals.json executable
instead of a static checklist.

Usage:
    python grade_evals.py <evals.json> <eval_id> <output_path>
    python grade_evals.py <evals.json> --all <outputs_dir>

Layout for --all mode:
    <outputs_dir>/eval-{id}-{name}/with_skill/outputs/rating.md
    (the same layout iteration-1 used)

Supported check_types:
    regex                        - regex must match
    contains                     - literal substring present
    contains_all                 - every pattern in `patterns[]` present
    contains_any_n               - at least `min_matches` of `patterns[]` present
    markdown_table_min_rows      - at least `min_rows` data rows in a markdown table
    regex_not_present            - regex must NOT match
    regex_or_absent              - regex must match (silence = pass)
    regex_not_present_or_qualified - regex must NOT match; soft check
    score_band_or_external_evidence - if headline score > `max_unsubstantiated_score`,
                                      output must contain at least one evidence marker
                                      from banned-phrases.json `evidence_markers_for_high_scores`

Exit codes:
    0 = all assertions pass for the targeted eval(s)
    1 = at least one assertion fails
    2 = bad input (file missing, eval_id not found, unsupported check_type)

Pure stdlib. Cross-platform. UTF-8 explicit.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# Make sibling scripts/ folder importable so we share the helper module.
_SKILL_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_SKILL_ROOT / "scripts"))
from _rate_lib import (  # noqa: E402
    HIGH_SCORE_EVIDENCE_THRESHOLD,
    evidence_region,
    extract_score,
    is_quoted_reference,
    load_banned as _load_banned,
)


BANNED_PHRASES_PATH = Path(__file__).parent.parent / "references" / "banned-phrases.json"


@dataclass
class AssertionResult:
    assertion_id: str
    text: str
    check_type: str
    passed: bool
    detail: str = ""


# --- check_type implementations -------------------------------------------------


def _check_regex(text: str, pattern: str) -> tuple[bool, str]:
    if re.search(pattern, text, re.MULTILINE):
        return True, f"pattern matched"
    return False, f"pattern did not match: `{pattern[:80]}`"


def _check_contains(text: str, pattern: str) -> tuple[bool, str]:
    if pattern in text:
        return True, f"substring found"
    return False, f"substring not found: '{pattern[:80]}'"


def _check_contains_all(text: str, patterns: list[str]) -> tuple[bool, str]:
    missing = [p for p in patterns if p not in text]
    if not missing:
        return True, f"all {len(patterns)} substrings present"
    return False, f"missing {len(missing)}/{len(patterns)}: {missing[:3]}"


def _check_contains_any_n(text: str, patterns: list[str], min_matches: int) -> tuple[bool, str]:
    matched: list[str] = []
    for p in patterns:
        if re.search(p, text, re.IGNORECASE):
            matched.append(p)
    if len(matched) >= min_matches:
        return True, f"{len(matched)}/{len(patterns)} patterns matched (min {min_matches} required)"
    return False, f"only {len(matched)}/{len(patterns)} matched, need {min_matches}: hits={matched}"


def _check_markdown_table_min_rows(text: str, min_rows: int) -> tuple[bool, str]:
    # Find largest markdown table in the doc; count data rows
    lines = text.splitlines()
    best = 0
    current_rows = 0
    in_table = False
    for ln in lines:
        stripped = ln.lstrip()
        is_row = stripped.startswith("|") and stripped.count("|") >= 3
        is_sep = is_row and re.search(r"\|\s*-{2,}", stripped) is not None
        if is_row:
            if is_sep:
                # separator — don't count, but mark in_table
                in_table = True
                continue
            if in_table:
                current_rows += 1
            else:
                # could be a header row; reset counter
                current_rows = 0
        else:
            best = max(best, current_rows)
            current_rows = 0
            in_table = False
    best = max(best, current_rows)
    if best >= min_rows:
        return True, f"largest table has {best} data rows (min {min_rows} required)"
    return False, f"largest table has {best} data rows, need {min_rows}"


def _check_regex_not_present(text: str, pattern: str) -> tuple[bool, str]:
    """Match must not appear in the output, with quote-aware exemption.

    Uses is_quoted_reference from the shared lib so this grader and check_rating.py
    agree on what counts as "used" vs "quoted". Without this, a rating that quotes
    a banned phrase in evidence (e.g., "the SKILL.md bans 'flawless'") would fail
    here but pass check_rating.py — a graders-disagree bug.
    """
    real_hits: list[str] = []
    for m in re.finditer(pattern, text, re.MULTILINE):
        if is_quoted_reference(text, m.start(), m.end()):
            continue
        real_hits.append(m.group(0)[:80])
    if not real_hits:
        return True, "pattern not present (as required, ignoring quoted references)"
    return False, f"forbidden pattern found: '{real_hits[0]}'"


def _check_regex_or_absent(text: str, pattern: str) -> tuple[bool, str]:
    # Pass if either: (a) the pattern matches, or (b) there's no score in the output
    if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
        return True, "qualifying pattern matched"
    has_score = re.search(r"\*\*\d{1,3}/100\*\*", text)
    if not has_score:
        return True, "no score given (acceptable for unrateable target)"
    return False, f"score given but no qualifying pattern matched: `{pattern[:80]}`"


def _check_regex_not_present_or_qualified(text: str, pattern: str) -> tuple[bool, str]:
    # Pass if pattern not present, OR if output contains a NEEDS_HUMAN / cannot-verify qualifier
    if not re.search(pattern, text, re.MULTILINE):
        return True, "forbidden pattern not present"
    qualifier_patterns = [
        r"NEEDS_HUMAN",
        r"(?i)cannot\s+(inspect|verify|fetch)",
        r"(?i)unable to (inspect|verify|fetch|reach)",
        r"(?i)not\s+inspected",
    ]
    for qp in qualifier_patterns:
        if re.search(qp, text):
            return True, "pattern present but output is qualified (NEEDS_HUMAN / cannot-verify)"
    return False, f"forbidden pattern found and not qualified: `{pattern[:80]}`"


def _check_score_band_or_external_evidence(text: str, max_unsubstantiated: int) -> tuple[bool, str]:
    score = extract_score(text)
    if score is None:
        return True, "no headline score (assertion N/A)"
    if score <= max_unsubstantiated:
        return True, f"score={score} <= {max_unsubstantiated} (no evidence required)"
    banned = _load_banned()
    markers = banned.get("evidence_markers_for_high_scores", {}).get("regex_patterns", [])
    region = evidence_region(text)  # exclude Path-to-100 + Verdict (forward-looking prose)
    for mk in markers:
        if re.search(mk, region):
            return True, f"score={score} substantiated by '{mk[:60]}'"
    return False, f"score={score} > {max_unsubstantiated} but no evidence marker found"


# --- dispatch -------------------------------------------------------------------


CHECK_DISPATCH = {
    "regex": lambda text, a: _check_regex(text, a["pattern"]),
    "contains": lambda text, a: _check_contains(text, a["pattern"]),
    "contains_all": lambda text, a: _check_contains_all(text, a["patterns"]),
    "contains_any": lambda text, a: _check_contains_any_n(text, a["patterns"], 1),
    "contains_any_n": lambda text, a: _check_contains_any_n(text, a["patterns"], a.get("min_matches", 1)),
    "markdown_table_min_rows": lambda text, a: _check_markdown_table_min_rows(text, a.get("min_rows", 5)),
    "regex_not_present": lambda text, a: _check_regex_not_present(text, a["pattern"]),
    "regex_or_absent": lambda text, a: _check_regex_or_absent(text, a["pattern"]),
    "regex_not_present_or_qualified": lambda text, a: _check_regex_not_present_or_qualified(text, a["pattern"]),
    "score_band_or_external_evidence": lambda text, a: _check_score_band_or_external_evidence(
        text, a.get("max_unsubstantiated_score", 89)
    ),
}


def grade_eval(eval_entry: dict, output_text: str) -> list[AssertionResult]:
    results: list[AssertionResult] = []
    for assertion in eval_entry.get("assertions", []):
        check_type = assertion.get("check_type")
        check_fn = CHECK_DISPATCH.get(check_type)
        if check_fn is None:
            results.append(
                AssertionResult(
                    assertion_id=assertion.get("id", "?"),
                    text=assertion.get("text", ""),
                    check_type=check_type or "?",
                    passed=False,
                    detail=f"unsupported check_type: {check_type}",
                )
            )
            continue
        try:
            passed, detail = check_fn(output_text, assertion)
        except KeyError as e:
            passed, detail = False, f"missing required key in assertion: {e}"
        except Exception as e:
            passed, detail = False, f"check threw: {type(e).__name__}: {e}"
        results.append(
            AssertionResult(
                assertion_id=assertion.get("id", "?"),
                text=assertion.get("text", ""),
                check_type=check_type,
                passed=passed,
                detail=detail,
            )
        )
    return results


def print_results(eval_entry: dict, results: list[AssertionResult]) -> int:
    name = eval_entry.get("name", f"eval-{eval_entry.get('id')}")
    failed = sum(1 for r in results if not r.passed)
    print(f"\n=== Eval {eval_entry.get('id')}: {name} ===")
    for r in results:
        mark = "[PASS]" if r.passed else "[FAIL]"
        print(f"{mark} {r.assertion_id} ({r.check_type})")
        print(f"       {r.text[:100]}")
        if r.detail:
            print(f"       -> {r.detail}")
    print(f"\nResult: {len(results) - failed}/{len(results)} assertions passed.")
    return failed


def main() -> int:
    parser = argparse.ArgumentParser(description="Run evals.json assertions against rating outputs")
    parser.add_argument("evals_json", help="Path to evals.json")
    parser.add_argument("--eval-id", type=int, default=None, help="Run a single eval by ID")
    parser.add_argument("--output", help="Path to rating output file (required with --eval-id)")
    parser.add_argument("--all", dest="all_dir", help="Run every eval; argument is the iteration directory containing eval-<id>-<name>/ subfolders")
    parser.add_argument(
        "--json", action="store_true", help="Emit results as JSON instead of human-readable text"
    )
    args = parser.parse_args()

    evals_path = Path(args.evals_json)
    if not evals_path.exists():
        print(f"[grade_evals] evals.json not found: {evals_path}", file=sys.stderr)
        return 2
    evals_data = json.loads(evals_path.read_text(encoding="utf-8"))
    evals = evals_data.get("evals", [])

    all_results: dict = {}
    total_failed = 0

    if args.all_dir:
        outputs_root = Path(args.all_dir)
        if not outputs_root.exists():
            print(f"[grade_evals] outputs directory not found: {outputs_root}", file=sys.stderr)
            return 2
        for eval_entry in evals:
            eval_id = eval_entry.get("id")
            name = eval_entry.get("name", f"eval-{eval_id}")
            rating_path = outputs_root / f"eval-{eval_id}-{name}" / "with_skill" / "outputs" / "rating.md"
            if not rating_path.exists():
                alt = list(outputs_root.glob(f"eval-{eval_id}-*/**/rating.md"))
                if alt:
                    rating_path = alt[0]
                else:
                    if not args.json:
                        print(f"\n=== Eval {eval_id}: {name} ===")
                        print(f"[SKIP] no rating.md found under {outputs_root} for this eval")
                    continue
            results = grade_eval(eval_entry, rating_path.read_text(encoding="utf-8"))
            if not args.json:
                total_failed += print_results(eval_entry, results)
            else:
                all_results[name] = [
                    {"id": r.assertion_id, "passed": r.passed, "detail": r.detail, "check_type": r.check_type}
                    for r in results
                ]
                total_failed += sum(1 for r in results if not r.passed)
    elif args.eval_id is not None:
        if not args.output:
            print("[grade_evals] --eval-id requires --output <rating-file>", file=sys.stderr)
            return 2
        eval_entry = next((e for e in evals if e.get("id") == args.eval_id), None)
        if eval_entry is None:
            print(f"[grade_evals] eval id {args.eval_id} not found in {evals_path}", file=sys.stderr)
            return 2
        output_path = Path(args.output)
        if not output_path.exists():
            print(f"[grade_evals] output file not found: {output_path}", file=sys.stderr)
            return 2
        results = grade_eval(eval_entry, output_path.read_text(encoding="utf-8"))
        if not args.json:
            total_failed = print_results(eval_entry, results)
        else:
            all_results[eval_entry.get("name", f"eval-{args.eval_id}")] = [
                {"id": r.assertion_id, "passed": r.passed, "detail": r.detail, "check_type": r.check_type}
                for r in results
            ]
            total_failed = sum(1 for r in results if not r.passed)
    else:
        print("[grade_evals] usage: grade_evals.py <evals.json> --eval-id N --output rating.md | --all <outputs_dir>", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps({"evals": all_results, "failed_total": total_failed}, indent=2))

    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
