#!/usr/bin/env python3
"""UserPromptSubmit hook — captures the raw user prompt for /rate's anti-priming check.

Writes the prompt verbatim to .last-prompt.txt next to this skill's SKILL.md so
the Stop-gate grader (rate_grade_gate.py) can pass it to check_rating.py
--prompt without the model having to remember or restate it. Emits NO stdout
(would pollute prompt context). Fails open (and silent) always.

Wiring (Claude Code example, settings.json):
    {
      "hooks": {
        "UserPromptSubmit": [
          {"hooks": [{"type": "command", "command": "python3 <skill-dir>/hooks/rate_capture_prompt.py"}]}
        ]
      }
    }

Pure stdlib. Cross-platform (Windows/macOS/Linux).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
OUT_FILE = SKILL_DIR / ".last-prompt.txt"


def main() -> None:
    try:
        raw = sys.stdin.read()
        if not raw:
            return
        data = json.loads(raw)
        prompt = data.get("prompt")
        if prompt is None:
            return
        OUT_FILE.write_text(str(prompt), encoding="utf-8")
    except Exception:
        pass


if __name__ == "__main__":
    main()
    sys.exit(0)
