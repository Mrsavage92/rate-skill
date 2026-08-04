# POST /api/orders - cold rating: **69/100**

Golden eval fixture standing in for a "rate a REST API endpoint" scenario. Synthetic content built to satisfy eval-7's assertions, not a live model transcript.

---

## What 100/100 looks like

1. Every request is authenticated and authorized before touching data, with no path that trusts a client-supplied user ID
2. Every input field is validated against a schema before use, with a clear 4xx on failure
3. Errors return a consistent envelope shape across every failure mode, never a raw stack trace
4. The endpoint is idempotent under retry - the same request twice produces the same result, not a duplicate side effect
5. Rate limiting is enforced and documented, with a clear response when exceeded
6. The endpoint's contract is documented (request/response shape, error codes) somewhere a consumer can find it
7. The endpoint is versioned so a breaking change doesn't silently break existing callers

---

## Area-by-area

| Area | Score | Evidence |
|---|---|---|
| Auth/RLS | **60** | fixture.py:12 - auth check present but relies on a client-supplied header, not a verified session |
| Input validation | **72** | fixture.py:24 - schema validation present for the body, missing on query params |
| Error envelope | **65** | fixture.py:40 - two of five error paths return raw exception text instead of the shared envelope |
| Idempotency | **58** | fixture.py:31 - no idempotency key handling; a network retry can double-charge |
| Rate limit | **70** | fixture.py:8 - rate limiting middleware applied but threshold undocumented |
| Documentation | **75** | fixture.py:1 - docstring present but no OpenAPI/schema file committed |
| Versioning | **68** | Route is unversioned (`/api/orders`, no `/v1/`) |

---

## Path to 100 - ordered by cost-to-fix vs value

### P0 - Required (69 -> ~78)

1. **Add idempotency-key handling.** A retried request currently creates a duplicate order. ~40 min. [fixture.py](fixture.py).
2. **Stop leaking raw exception text in error responses.** Route every failure through the shared error envelope. ~30 min. [fixture.py](fixture.py).

### P1 - Nice-to-have (78 -> ~88)

3. **Validate query params against the same schema as the body.** ~20 min. [fixture.py](fixture.py).

---

## Verdict

69/100. Golden fixture used only to test the eval-assertion logic end to end; no real target was inspected.
