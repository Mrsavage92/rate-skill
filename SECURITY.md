# Security Policy

This repository ships pure-Python stdlib scripts (no pip dependencies) plus
markdown skill definitions. Nothing here handles secrets, network requests, or
untrusted user input beyond reading local files the invoking agent is already
pointed at.

## Reporting a vulnerability

If you find a security issue - a path traversal in a bundled script, a way
for a crafted rating file or hook payload to execute unintended code, or
anything else that violates the "reads local files, does not phone home"
scope above - open a [GitHub issue](https://github.com/Mrsavage92/rate-skill/issues)
marked `security`, or contact the maintainer directly via the profile on this
repository if you'd rather not disclose it publicly first.

## Scope notes

- The two optional hooks (`rate/hooks/*.py`) read JSON from stdin and are
  designed to fail open on malformed input - see
  [rate/hooks/README.md](rate/hooks/README.md#failure-behaviour). A crash or
  hang in either script on adversarial stdin is in scope.
- The structural grader and cost guard only read files the invoking agent
  already has access to; they do not fetch URLs or execute the content they
  inspect.
