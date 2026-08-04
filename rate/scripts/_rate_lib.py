"""Shared helpers for /rate's bundled scripts.

Single source of truth for:
  - extract_score:        find the headline N/100 in a rating output
  - is_quoted_reference:  quote-aware exemption used by all banned-phrase checks
  - load_banned:          read references/banned-phrases.json
  - iter_phrase_matches:  iterate literal + regex hits in a category

Imported by check_rating.py, convergence_check.py, and evals/grade_evals.py.
Pure stdlib. Cross-platform. UTF-8 explicit.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterator


BANNED_PHRASES_PATH = Path(__file__).parent.parent / "references" / "banned-phrases.json"

# Score band thresholds — single source of truth, referenced by SKILL.md.
# Output rated >= HIGH_SCORE_EVIDENCE_THRESHOLD must contain an external
# comparator or measured metric (banned_phrases.evidence_markers_for_high_scores).
HIGH_SCORE_EVIDENCE_THRESHOLD = 90


def load_banned() -> dict:
    if not BANNED_PHRASES_PATH.exists():
        raise FileNotFoundError(f"banned-phrases.json not found at {BANNED_PHRASES_PATH}")
    return json.loads(BANNED_PHRASES_PATH.read_text(encoding="utf-8"))


def extract_score(text: str) -> int | None:
    """Find the headline `**N/100**` score in the first 30 lines of a rating output."""
    head = "\n".join(text.splitlines()[:30])
    m = re.search(r"^#\s+.*\*\*(\d{1,3})/100\*\*", head, re.MULTILINE)
    return int(m.group(1)) if m else None


def evidence_region(text: str) -> str:
    """Return the portion of a rating where evidence for the CURRENT score must live.

    Evidence that substantiates a 90+ score belongs in the assessment — the headline,
    the "What 100/100 looks like" criteria, and the Area-by-area table — NOT in the
    forward-looking "Path to 100" ladder or the closing Verdict, where measured-metric
    tokens naturally appear as *future* work ("run Lighthouse", "needs convergence
    testing"). Counting those toward the gate let a stray token unlock a 96. So the
    evidence region is everything before the "## Path to 100" heading.

    Falls back to the whole document if that heading is absent (a malformed rating
    will already fail the section-presence checks).

    Added 2026-06-01 to close the high-score-evidence bypass.
    """
    m = re.search(r"^##\s+Path to 100", text, re.MULTILINE)
    return text[: m.start()] if m else text


def is_quoted_reference(text: str, start: int, end: int) -> bool:
    """Return True if the match at [start, end] is a quoted reference rather than a used quality claim.

    Heuristics — match is "quoted" if any of:
      1. Immediately wrapped in ASCII double quotes: `"phrase"`
      2. Inside a backtick code span: `phrase`
      3. Part of a comma-separated quoted list like `, "phrase",` or `"phrase", `
      4. Preceded within 12 chars by a negation marker AND that marker is in the SAME SENTENCE
         (no `.`, `!`, `?` between marker and match).

    Tightened 2026-05-19: heuristic 4 used to be 30 chars / any sentence (too permissive).
    """
    # 1. Immediate quote wrap
    if start > 0 and end < len(text):
        if text[start - 1] == '"' and text[end] == '"':
            return True
    # 2. Backtick code span — same line
    line_start = text.rfind("\n", 0, start) + 1
    line_end = text.find("\n", end)
    if line_end == -1:
        line_end = len(text)
    line = text[line_start:line_end]
    rel_start = start - line_start
    rel_end = end - line_start
    ticks_before = line[:rel_start].count("`")
    ticks_after = line[rel_end:].count("`")
    if ticks_before % 2 == 1 and ticks_after >= 1:
        return True
    # 3. Comma-separated quoted list
    pre = text[max(0, start - 5):start]
    post = text[end:min(len(text), end + 5)]
    if '"' in pre and ('"' in post or '",' in post):
        return True
    # 4. Negation within 12 chars before AND same sentence
    pre_context = text[max(0, start - 30):start]
    for marker in (" not ", " ban ", " reject ", " avoid ", " forbid ", "instead of ", "rather than ", "do not use ", "no ", "ignore "):
        idx = pre_context.lower().rfind(marker)
        if idx == -1:
            continue
        distance = len(pre_context) - (idx + len(marker))
        if distance > 12:
            continue
        between = pre_context[idx + len(marker):]
        if re.search(r"[.!?]\s", between):
            continue
        return True
    return False


def iter_phrase_matches(text: str, literal_patterns: list[str], regex_patterns: list[str]) -> Iterator[tuple[int, int, str]]:
    """Yield (start, end, pattern_repr) for every match.

    Literal patterns are matched case-insensitive via re.escape.
    Regex patterns are used as-is (callers supply `(?i)` if needed).
    """
    for p in literal_patterns:
        for m in re.finditer(re.escape(p), text, re.IGNORECASE):
            yield m.start(), m.end(), p
    for p in regex_patterns:
        for m in re.finditer(p, text):
            yield m.start(), m.end(), p
