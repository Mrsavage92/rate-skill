#!/usr/bin/env python3
"""Pre-rating cost guard for /rate.

Inspects the target path and prints a warning if it's too large for a single
strategic rating to cover meaningfully. SKILL.md commits to surfacing this
warning before scoring — this script makes the rule enforceable instead of
prose-only.

Thresholds (from SKILL.md cost-guard section):
    Single file:    >2000 LOC -> warn
    Directory/repo: >50 files -> warn

Usage:
    python cost_guard.py <target-path> [--quiet]

Exit codes:
    0 = no warning needed
    1 = warning issued (target exceeds threshold; rater should surface to user before scoring)
    2 = target not found / unreadable

Pure stdlib. Cross-platform. UTF-8 explicit.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


FILE_LOC_THRESHOLD = 2000
DIR_FILE_THRESHOLD = 50


# Extensions counted as "code-like" files when summing a directory. Lockfiles,
# build artifacts, binary assets, and vendored deps are excluded so the count
# reflects the rateable surface.
COUNTED_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs",
    ".go", ".rs", ".java", ".kt", ".swift", ".rb", ".php",
    ".html", ".css", ".scss", ".sass", ".less",
    ".md", ".mdx", ".rst", ".txt",
    ".json", ".yaml", ".yml", ".toml",
    ".sh", ".ps1", ".bash",
    ".sql", ".graphql",
}

EXCLUDED_DIRS = {
    "node_modules", ".next", ".nuxt", "dist", "build", "out",
    ".git", ".venv", "venv", "__pycache__", ".pytest_cache",
    "vendor", "target", "coverage", ".cache",
}


def count_loc(path: Path) -> int:
    try:
        return sum(1 for _ in path.read_text(encoding="utf-8", errors="replace").splitlines())
    except (OSError, ValueError):
        return 0


def count_dir_files(root: Path) -> tuple[int, list[str]]:
    """Return (count, sample). Walks the tree skipping excluded dirs."""
    sample: list[str] = []
    count = 0
    for child in root.rglob("*"):
        parts_set = set(child.parts)
        if parts_set & EXCLUDED_DIRS:
            continue
        if not child.is_file():
            continue
        if child.suffix.lower() not in COUNTED_EXTENSIONS:
            continue
        count += 1
        if len(sample) < 5:
            sample.append(str(child.relative_to(root)))
    return count, sample


def evaluate(target: Path) -> tuple[str, str]:
    """Return (status, message) where status is one of "ok", "warn", "halt".

    "halt" means the target cannot be inspected at all (missing path, or a path
    that is neither a regular file nor a directory — e.g. a broken symlink or a
    device node). SKILL.md commits to exit 2 / NEEDS_HUMAN in that case; the
    previous version returned a falsey warn and printed "[cost_guard OK] target
    not found", which silently passed the guard. Fixed 2026-06-01.
    """
    if not target.exists():
        return "halt", f"target not found or unreadable: {target}"

    if target.is_file():
        loc = count_loc(target)
        if loc > FILE_LOC_THRESHOLD:
            return "warn", (
                f"Target {target.name} is {loc:,} LOC (threshold: {FILE_LOC_THRESHOLD:,}).\n"
                "A single rating will undersample this file. Options:\n"
                "  - narrow the rating to a specific section / class\n"
                "  - use /full-audit or /parallel-audit for whole-file coverage\n"
                "  - proceed if the user explicitly wants a strategic 1-page overview"
            )
        return "ok", f"file size OK ({loc:,} LOC, threshold {FILE_LOC_THRESHOLD:,})"

    if target.is_dir():
        count, sample = count_dir_files(target)
        if count > DIR_FILE_THRESHOLD:
            sample_text = ", ".join(sample) + ("..." if count > len(sample) else "")
            return "warn", (
                f"Target {target.name}/ contains {count} rateable files "
                f"(threshold: {DIR_FILE_THRESHOLD}). Sample: {sample_text}\n"
                "A single /rate produces ONE strategic rating; it will undersample a repo of this size.\n"
                "Options:\n"
                "  - /full-audit  - 9 specialized audit suites against a URL\n"
                "  - /parallel-audit  - run multiple audit suites in parallel\n"
                "  - narrow the target to a specific subdirectory or top-level file"
            )
        return "ok", f"directory size OK ({count} rateable files, threshold {DIR_FILE_THRESHOLD})"

    return "halt", f"target is neither file nor directory: {target}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Pre-rating cost-guard check for /rate")
    parser.add_argument("target", help="Path to the rating target (file or directory)")
    parser.add_argument("--quiet", action="store_true", help="Suppress 'OK' messages; only print warnings")
    args = parser.parse_args()

    target = Path(args.target)
    try:
        status, message = evaluate(target)
    except OSError as e:
        print(f"[cost_guard HALT] could not inspect target: {e}", file=sys.stderr)
        print("NEEDS_HUMAN: target is unreadable. Verify the path before rating.", file=sys.stderr)
        return 2

    if status == "halt":
        print("[cost_guard HALT]", file=sys.stderr)
        print(message, file=sys.stderr)
        print("NEEDS_HUMAN: cannot rate a target that does not exist. Check the path.", file=sys.stderr)
        return 2
    if status == "warn":
        print("[cost_guard WARNING]")
        print(message)
        return 1
    if not args.quiet:
        print(f"[cost_guard OK] {message}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
