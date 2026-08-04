#!/usr/bin/env python3
"""Stop hook — enforces /rate's structural grader on the rating actually produced.

Reads the last assistant text message from the transcript. If it looks like a
/rate output (H1 headline `# ... **NN/100**` AND a "cold rating" / "Path to 100"
marker), it runs check_rating.py against that exact text, passing the captured
prompt (if present) for the priming check. If the grader fails (exit 1), the
Stop is BLOCKED and the failures are fed back so the rating gets revised before
the turn ends. This makes "run the grader" a real gate instead of honor-system
prose in SKILL.md.

Fail-open on every error path (no transcript, no python, grader missing/
misconfigured, parse error): the gate must never trap the user when something
about the environment is off. It only ever blocks on a genuine grader exit-1
against a genuine rating.

Wiring (Claude Code example, settings.json):
    {
      "hooks": {
        "Stop": [
          {"hooks": [{"type": "command", "command": "python3 <skill-dir>/hooks/rate_grade_gate.py"}]}
        ]
      }
    }

Pure stdlib. Cross-platform (Windows/macOS/Linux) — this replaces a Windows-only
PowerShell implementation so the same hook works everywhere Python does.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import NoReturn

HOOK_DIR = Path(__file__).resolve().parent
SKILL_DIR = HOOK_DIR.parent
GRADER = SKILL_DIR / "scripts" / "check_rating.py"
PROMPT_FILE = SKILL_DIR / ".last-prompt.txt"

HEADLINE_RE = re.compile(r"^#\s+.*\*\*\d{1,3}/100\*\*", re.MULTILINE)
MARKER_RE = re.compile(r"cold rating|^##\s+Path to 100", re.MULTILINE)


def allow() -> NoReturn:
    sys.exit(0)


def last_assistant_text(transcript_path: Path) -> str | None:
    try:
        lines = transcript_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None
    for line in reversed(lines[-250:]):
        if not line.strip():
            continue
        try:
            evt = json.loads(line)
        except json.JSONDecodeError:
            continue
        msg = evt.get("message")
        if not isinstance(msg, dict) or msg.get("role") != "assistant":
            continue
        parts = [
            block.get("text", "")
            for block in msg.get("content", [])
            if isinstance(block, dict) and block.get("type") == "text"
        ]
        text = "\n".join(p for p in parts if p)
        if text.strip():
            return text
    return None


def main() -> None:
    try:
        raw = sys.stdin.read()
        if not raw:
            allow()
        data = json.loads(raw)

        transcript_path = data.get("transcript_path")
        if not transcript_path or not Path(transcript_path).exists():
            allow()

        last_text = last_assistant_text(Path(transcript_path))
        if not last_text:
            allow()

        if not (HEADLINE_RE.search(last_text) and MARKER_RE.search(last_text)):
            allow()

        if not GRADER.exists():
            allow()  # fail-open: grader gone

        cmd_args = [sys.executable, str(GRADER)]
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as tf:
            tf.write(last_text)
            tmp_path = tf.name
        cmd_args.append(tmp_path)

        if PROMPT_FILE.exists():
            prompt = PROMPT_FILE.read_text(encoding="utf-8", errors="replace")
            if prompt:
                cmd_args += ["--prompt", prompt]

        proc = subprocess.run(cmd_args, capture_output=True, text=True, encoding="utf-8")
        Path(tmp_path).unlink(missing_ok=True)

        if proc.returncode in (0, 2):
            allow()  # passed, or grader misconfigured -> fail-open

        # exit 1 -> structural failure. Block the stop and feed the failures back.
        reason = (
            "BLOCKED by /rate's Stop-gate: the rating you just produced FAILED its own "
            "structural grader (check_rating.py exit 1). Fix the issues below and re-emit "
            "the corrected rating before ending the turn.\n\n" + proc.stdout + proc.stderr
        )
        print(json.dumps({"decision": "block", "reason": reason}))
        sys.exit(0)
    except Exception:
        sys.exit(0)  # fail-open on any unexpected error: never trap the user


if __name__ == "__main__":
    main()
