# /rate hooks (optional)

The main `/rate` workflow requires the coordinating agent to run `scripts/check_rating.py` after every rating. These hooks automate that structural check instead of relying on the agent to remember it.

They do **not** create, launch, or verify the fresh evaluator required by the independence contract. The coordinating agent must establish that separation before a numeric score is produced.

- **`rate_capture_prompt.py`** - a `UserPromptSubmit` hook. Writes the raw user prompt to `.last-prompt.txt` next to `SKILL.md`, so the grader can check whether priming was acknowledged.
- **`rate_grade_gate.py`** - a `Stop` hook. Reads the assistant's last message from the transcript and, when it looks like a `/rate` output, runs the structural grader against that exact text. A genuine grader failure blocks the turn and feeds the failures back for revision.

Both scripts use only the Python standard library and contain no PowerShell-only or bash-only logic.

## Wiring into Claude Code

Add the following to `settings.json` at project or user level, replacing `<skill-dir>` with the directory containing this `hooks` folder:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 <skill-dir>/hooks/rate_capture_prompt.py"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 <skill-dir>/hooks/rate_grade_gate.py"
          }
        ]
      }
    ]
  }
}
```

On Windows, `python3` may need to be replaced with `python`, depending on how Python is installed:

```powershell
python --version
```

## Wiring into other harnesses

Both scripts read one JSON object from standard input. The Stop hook writes a JSON block decision when the structural grader fails:

```json
{"decision": "block", "reason": "..."}
```

Another harness can use the scripts directly when it provides equivalent user-prompt and pre-stop hook points. Otherwise, skip the hooks and run the grader manually:

```bash
python scripts/check_rating.py <path-to-rating.md> --prompt "<raw-user-prompt>"
```

## Failure behaviour

The hooks fail open on infrastructure errors such as a missing transcript, malformed hook input, or Python not being available. This prevents a broken optional hook from trapping every Claude Code response.

That does not change the main skill's independence requirement. `/rate` must still fail closed with `NEEDS_HUMAN - independent evaluator unavailable` when a fresh, isolated evaluator cannot be created.

The hooks enforce report structure only. They do not prove that the score is correct or that the evaluator was genuinely independent.
