#!/usr/bin/env python3
"""Convergence check for /rate.

Takes N rating files produced by independent runs against the SAME target/prompt.
Extracts the headline score from each, reports mean + stddev. If stddev exceeds
the threshold, flags low-convergence — either the prompt is ambiguous or the
skill's calibration band is too loose.

Usage:
    python convergence_check.py path1.md path2.md path3.md ...
    python convergence_check.py path1.md path2.md path3.md --threshold 5

Exit codes:
    0 = convergence ok (stddev <= threshold)
    1 = low convergence (stddev > threshold)
    2 = bad input (file missing, no score parseable, <2 inputs)

Pure stdlib, cross-platform, UTF-8 explicit.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _rate_lib import extract_score  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convergence check across multiple /rate outputs on the same target"
    )
    parser.add_argument("paths", nargs="+", help="Paths to rating markdown files")
    parser.add_argument(
        "--threshold",
        type=float,
        default=5.0,
        help="Max acceptable stddev (default: 5.0). Exit 1 if exceeded.",
    )
    parser.add_argument(
        "--json", action="store_true", help="Emit results as JSON"
    )
    args = parser.parse_args()

    if len(args.paths) < 2:
        print("[convergence] need at least 2 rating files to compute stddev", file=sys.stderr)
        return 2

    scores: list[tuple[str, int]] = []
    for p in args.paths:
        path = Path(p)
        if not path.exists():
            print(f"[convergence] file not found: {p}", file=sys.stderr)
            return 2
        text = path.read_text(encoding="utf-8")
        s = extract_score(text)
        if s is None:
            print(f"[convergence] no `**N/100**` headline found in {p}", file=sys.stderr)
            return 2
        scores.append((p, s))

    values = [s for _, s in scores]
    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    stddev = math.sqrt(variance)
    spread = max(values) - min(values)
    converged = stddev <= args.threshold

    if args.json:
        out = {
            "scores": [{"path": p, "score": s} for p, s in scores],
            "mean": round(mean, 2),
            "stddev": round(stddev, 2),
            "spread": spread,
            "threshold": args.threshold,
            "converged": converged,
            "n_runs": len(values),
        }
        print(json.dumps(out, indent=2))
    else:
        print(f"Runs: {len(values)}")
        for p, s in scores:
            print(f"  {s:3d}/100  {Path(p).name}")
        print()
        print(f"Mean    : {mean:.1f}")
        print(f"Stddev  : {stddev:.2f}")
        print(f"Spread  : {spread} (max - min)")
        print(f"Threshold: {args.threshold:.2f}")
        print()
        if converged:
            print(f"[CONVERGED] stddev {stddev:.2f} <= threshold {args.threshold:.2f}")
        else:
            print(f"[LOW CONVERGENCE] stddev {stddev:.2f} > threshold {args.threshold:.2f}")
            print("Possible causes: ambiguous prompt, loose calibration band, target genuinely hard to score.")

    return 0 if converged else 1


if __name__ == "__main__":
    sys.exit(main())
