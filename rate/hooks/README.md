# /rate hooks (optional)

The skill's contract is fully satisfied by running `scripts/check_rating.py`
manually after every rating (see SKILL.md, rule 10). These two hooks make that
automatic instead of relying on the model to remember.

- **`rate_capture_prompt.py`** — a `UserPromptSubmit` hook. Writes the raw user
  prompt to `.last-prompt.txt` next to `SKILL.md`, so the priming-acknowledgement
  check in the grader always runs against the real prompt.
- **`rate_grade_gate.py`** — a `Stop` hook. Reads the assistant's last message
  from the transcript; if it looks like a `/rate` output, runs the grader
  against that exact text. If the grader fails, the turn is **blocked** and the
  failures are fed back so the rating gets revised before it ends.

Both are pure-stdlib Python — no PowerShell- or bash-only logic — so the same
two files work on Windows, macOS, and Linux.

## Wiring into Claude Code

Add to `settings.json` (project or user level), substituting the actual path
this skill is installed at:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      { "hooks": [{ "type": "command", "command": "python3 <skill-dir>/hooks/rate_capture_prompt.py" }] }
    ],
    "Stop": [
      { "hooks": [{ "type": "command", "command": "python3 <skill-dir>/hooks/rate_grade_gate.py" }] }
    ]
  }
}
```

On Windows, `python3` may need to be `python` depending on how Python is
installed — check `python3 --version` / `python --version` in your shell first.

## Wiring into other harnesses

Both scripts read a single JSON object from stdin and (for the Stop hook)
write a JSON `{"decision": "block", "reason": "..."}` object to stdout when
blocking. If your harness has an equivalent "before the turn ends" /
"on user prompt" hook point that follows the same stdin-JSON convention, these
scripts should work as-is or with a thin adapter. If it doesn't, skip the hooks
entirely and just run the grader manually per SKILL.md rule 10 — nothing else
in this skill depends on the hooks existing.

## Fail-open by design

Every error path (missing transcript, no Python on PATH, grader file missing,
malformed JSON) causes the hook to allow silently. These hooks only ever block
on a genuine grader failure against a genuine `/rate` output — never on
infrastructure being unavailable.
