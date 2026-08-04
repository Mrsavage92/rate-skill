#!/usr/bin/env python3
"""Structural grader for /rate output.

Usage:
    python check_rating.py <path-to-rating.md>
    python check_rating.py <path-to-rating.md> --prompt "<user-prompt-text>"

Exit codes:
    0 = all structural rules pass
    1 = one or more rules fail (details printed to stderr)
    2 = file not found / unreadable

The grader validates the contract /rate's SKILL.md commits to producing.
It is not a quality grader (the score's correctness is a judgment call) —
it enforces shape, banned phrases, and the 90+-needs-evidence rule.

Cross-platform: pure stdlib, no shell-outs, UTF-8 explicit on every write.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# Make sibling _rate_lib importable when this script is run directly.
sys.path.insert(0, str(Path(__file__).parent))
from _rate_lib import (  # noqa: E402
    HIGH_SCORE_EVIDENCE_THRESHOLD,
    evidence_region,
    extract_score,
    is_quoted_reference,
    iter_phrase_matches,
    load_banned as _load_banned,
)


def load_banned() -> dict:
    try:
        return _load_banned()
    except FileNotFoundError as e:
        print(f"[grader] {e}", file=sys.stderr)
        sys.exit(2)


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str = ""

    def fmt(self) -> str:
        mark = "[PASS]" if self.passed else "[FAIL]"
        line = f"{mark} {self.name}"
        if self.detail:
            line += f"\n       {self.detail}"
        return line


def check_headline_score(text: str) -> CheckResult:
    score = extract_score(text)
    if score is None:
        return CheckResult(
            "headline-score",
            False,
            "No `# ... **N/100**` headline found in the first 30 lines.",
        )
    if not 0 <= score <= 100:
        return CheckResult("headline-score", False, f"Score {score} outside 0-100 range.")
    return CheckResult("headline-score", True, f"score={score}")


def check_section(text: str, heading_substr: str, level: int = 2) -> CheckResult:
    pat = r"^" + ("#" * level) + r"\s+.*" + re.escape(heading_substr)
    found = re.search(pat, text, re.MULTILINE)
    return CheckResult(
        f"section-{heading_substr.lower().replace(' ', '-').replace('/', '-')}",
        bool(found),
        "" if found else f"missing `{('#' * level)} ... {heading_substr}` heading",
    )


def check_area_table_rows(text: str, min_rows: int = 5) -> CheckResult:
    """Find the Area-by-area table and count data rows (excluding header + separator)."""
    # Find the Area-by-area section
    sect = re.search(
        r"^##\s+Area-by-area.*?(?=^##\s|\Z)", text, re.MULTILINE | re.DOTALL
    )
    if not sect:
        return CheckResult("area-table-rows", False, "Area-by-area section not found")
    block = sect.group(0)
    # Count rows that look like markdown table data (start with `|`, have at least 2 `|`)
    rows = [
        ln
        for ln in block.splitlines()
        if ln.lstrip().startswith("|") and ln.count("|") >= 3
    ]
    # Exclude header row and separator row (the one with `---`)
    data_rows = [r for r in rows if not re.search(r"\|\s*-{2,}", r)]
    data_rows = data_rows[1:] if data_rows else []  # drop header
    passed = len(data_rows) >= min_rows
    return CheckResult(
        "area-table-rows",
        passed,
        f"{len(data_rows)} data rows found (min {min_rows} required)",
    )


def check_p0_p1_p2(text: str) -> CheckResult:
    """Path to 100 must have at least P0 and P1 tiers (P2 optional but recommended)."""
    path_sect = re.search(
        r"^##\s+Path to 100.*?(?=^##\s|\Z)", text, re.MULTILINE | re.DOTALL
    )
    if not path_sect:
        return CheckResult("p0-p1-tiers", False, "Path to 100 section not found")
    block = path_sect.group(0)
    has_p0 = bool(re.search(r"###\s*P0\b", block))
    has_p1 = bool(re.search(r"###\s*P1\b", block))
    if has_p0 and has_p1:
        return CheckResult("p0-p1-tiers", True, "P0 and P1 tiers both present")
    missing = []
    if not has_p0:
        missing.append("P0")
    if not has_p1:
        missing.append("P1")
    return CheckResult("p0-p1-tiers", False, f"missing tier(s): {', '.join(missing)}")


def check_p0_has_time_estimates(text: str) -> CheckResult:
    """Every P0 item must include an AI wall-clock time estimate.

    Supports BOTH numbered (`1. **fix.**`) and bulleted (`- **fix.**` / `* **fix.**`) P0 item
    formats — the previous version silently passed any rating that used bullets, which is a
    fail-by-omission. Patched 2026-05-19.
    """
    p0_sect = re.search(
        r"###\s*P0\b.*?(?=###\s*P[12]\b|^##\s|\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if not p0_sect:
        return CheckResult("p0-time-estimates", False, "P0 section not found")
    block = p0_sect.group(0)
    # Numbered (1. **) or bulleted (-/* **) items, both formats accepted.
    item_start_pattern = r"^\s*(?:\d+\.|[-*])\s+\*\*"
    items = re.findall(
        item_start_pattern + r".+?(?=" + item_start_pattern + r"|\Z)",
        block,
        re.MULTILINE | re.DOTALL,
    )
    if not items:
        return CheckResult(
            "p0-time-estimates",
            False,
            "no P0 items found (expected `N. **...**` or `- **...**` format)",
        )
    time_pattern = re.compile(
        r"(\d+\s*(min|minutes?|hr|hrs|hours?))|(this\s+turn)|(this\s+session)",
        re.IGNORECASE,
    )
    missing = []
    for i, item in enumerate(items, 1):
        if not time_pattern.search(item):
            first_line = item.strip().splitlines()[0][:80]
            missing.append(f"item {i}: '{first_line}...'")
    if missing:
        return CheckResult(
            "p0-time-estimates",
            False,
            f"{len(missing)}/{len(items)} P0 items lack a time estimate: {'; '.join(missing[:3])}",
        )
    return CheckResult("p0-time-estimates", True, f"all {len(items)} P0 items have time estimates")


def check_banned_phrases(text: str, banned: dict) -> list[CheckResult]:
    results: list[CheckResult] = []
    for category in ("self_praise", "priming_framing", "human_time_units", "hedge_numbers"):
        cat = banned.get(category, {})
        literal = cat.get("patterns", [])
        regex_pats = cat.get("regex_patterns", [])
        hits: list[str] = []
        for m_start, m_end, p in iter_phrase_matches(text, literal, regex_pats):
            if is_quoted_reference(text, m_start, m_end):
                continue
            start = max(0, m_start - 30)
            end = min(len(text), m_end + 30)
            ctx = text[start:end].replace("\n", " ")
            matched_text = text[m_start:m_end]
            hits.append(f"'{matched_text}' (via `{p}`) in: ...{ctx}...")
            if len(hits) >= 3:
                break
        results.append(
            CheckResult(
                f"no-banned-{category.replace('_', '-')}",
                passed=(len(hits) == 0),
                detail="" if not hits else f"{len(hits)} hit(s): {hits[0]}",
            )
        )
    return results


def check_high_score_evidence(text: str, banned: dict) -> CheckResult:
    """If score >= HIGH_SCORE_EVIDENCE_THRESHOLD, output must contain at least one external-comparator or measured-metric marker.

    Threshold is imported from _rate_lib so all scripts agree. Patched 2026-05-19 to fix
    the divergence between check_rating.py (was 90) and evals/evals.json eval-2 (was 94).
    """
    score = extract_score(text)
    if score is None or score < HIGH_SCORE_EVIDENCE_THRESHOLD:
        return CheckResult(
            "high-score-evidence",
            True,
            f"N/A (score={score}, threshold={HIGH_SCORE_EVIDENCE_THRESHOLD})",
        )
    patterns = banned.get("evidence_markers_for_high_scores", {}).get("regex_patterns", [])
    region = evidence_region(text)  # exclude Path-to-100 + Verdict (forward-looking prose)
    for p in patterns:
        if re.search(p, region):
            return CheckResult(
                "high-score-evidence",
                True,
                f"score={score} substantiated by evidence marker '{p}'",
            )
    return CheckResult(
        "high-score-evidence",
        False,
        f"score={score} (>={HIGH_SCORE_EVIDENCE_THRESHOLD}) but no external comparator or measured metric found. "
        "Required patterns: Lighthouse N, LCP/INP/CLS, Nms, Nkb, axe-clean, 'matches X docs', 'beats most', stddev<N, etc.",
    )


def check_priming_attempts_in_prompt(prompt: str | None, output: str, banned: dict) -> CheckResult:
    """If the user prompt contains priming markers, the output must log them in a 'Priming attempts ignored' block."""
    if not prompt:
        return CheckResult(
            "priming-acknowledged", True, "skipped (no --prompt provided)"
        )
    primed_patterns = banned.get("primed_input_markers", {}).get("regex_patterns", [])
    priming_found = [p for p in primed_patterns if re.search(p, prompt)]
    if not priming_found:
        return CheckResult(
            "priming-acknowledged", True, "no priming markers in prompt"
        )
    # Priming WAS attempted — output must acknowledge it
    ack_patterns = [
        r"(?i)priming",
        r"(?i)ignored?\s+(the\s+)?(prior|primed)",
        r"(?i)does not transfer",
        r"(?i)not\s+used\s+as\s+evidence",
        r"(?i)(reject|rejected)\s+the\s+(primed|prior)",
    ]
    acknowledged = any(re.search(p, output) for p in ack_patterns)
    return CheckResult(
        "priming-acknowledged",
        acknowledged,
        f"prompt contained priming markers ({priming_found[:2]}); "
        + (
            "output acknowledges the priming attempt"
            if acknowledged
            else "output does NOT log the priming attempt in the verdict"
        ),
    )


def run_all_checks(text: str, prompt: str | None = None) -> tuple[list[CheckResult], int]:
    banned = load_banned()
    results: list[CheckResult] = []
    results.append(check_headline_score(text))
    results.append(check_section(text, "What 100/100 looks like"))
    results.append(check_section(text, "Area-by-area"))
    results.append(check_section(text, "Path to 100"))
    results.append(check_section(text, "Verdict"))
    results.append(check_area_table_rows(text))
    results.append(check_p0_p1_p2(text))
    results.append(check_p0_has_time_estimates(text))
    results.extend(check_banned_phrases(text, banned))
    results.append(check_high_score_evidence(text, banned))
    results.append(check_priming_attempts_in_prompt(prompt, text, banned))
    failed = sum(1 for r in results if not r.passed)
    return results, failed


def main() -> int:
    parser = argparse.ArgumentParser(description="Structural grader for /rate output")
    parser.add_argument("path", help="Path to the rating markdown file")
    parser.add_argument(
        "--prompt",
        default=None,
        help="Optional: the user prompt that produced this rating (enables priming-acknowledgement check)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit results as JSON instead of human-readable text",
    )
    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"[grader] file not found: {path}", file=sys.stderr)
        return 2
    text = path.read_text(encoding="utf-8")

    results, failed = run_all_checks(text, args.prompt)

    if args.json:
        out = {
            "path": str(path),
            "passed": failed == 0,
            "failed_count": failed,
            "total_count": len(results),
            "checks": [
                {"name": r.name, "passed": r.passed, "detail": r.detail}
                for r in results
            ],
        }
        print(json.dumps(out, indent=2))
    else:
        for r in results:
            print(r.fmt())
        print()
        print(f"Result: {len(results) - failed}/{len(results)} checks passed.")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
