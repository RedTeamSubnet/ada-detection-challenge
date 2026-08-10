# `_bot_runner.py` — refactor plan

Scope: `api/endpoints/challenge/_bot_runner.py` only. Refactoring only —
behaviour identical, signatures unchanged, tests pass unmodified throughout.

118 lines, two functions that are really two independent HTTP clients pointed at
the same service.

---

## Baseline: the suite is already red

```
tests/test_bot_runner_client.py
  1 failed, 5 passed
  FAILED test_wait_for_run_returns_timeout_after_three_attempts
```

The test asserts 3 polls; `wait_for_run` does `range(5)`. Someone changed the
count and didn't update the test. **Settle this first** (step 0 below) — you
can't use "tests still pass" as your refactor safety net until they do.

---

## The shape to aim for

Three helpers so each public function is one readable loop:

```python
_join_url(base, path)     # unchanged
_auth_kwargs(**extra)     # auth + timeout in one place
_busy_delays()            # the retry schedule, as data
_build_payload(...)       # the request body
```

---

## 0. Fix the red test

Decide which is right — 3 polls or 5 — and make code and test agree.

With `2**attempt` backoff: 3 polls waits 1+2 = 3s, 5 polls waits 1+2+4+8 = 15s.
Neither is enough for an antidetect browser, but that's a behaviour question for
later. For the refactor, just pick one and stop the drift.

---

## 1. One place that knows how to call bot-runner

Both functions rebuild the same three things from config:

```python
# trigger_run                          # wait_for_run
config.challenge.bot_runner            config.challenge.bot_runner
headers=_auth_headers(...api_key...)   headers=_auth_headers(...api_key...)
timeout=...request_timeout_sec         timeout=...request_timeout_sec
```

```python
def _auth_kwargs(**extra) -> dict:
    """Auth header and timeout for any bot-runner call."""
    cfg = config.challenge.bot_runner
    return {
        "headers": {"Authorization": f"Bearer {cfg.api_key.get_secret_value()}"},
        "timeout": cfg.request_timeout_sec,
        **extra,
    }
```

```python
http.post(url, **_auth_kwargs(json=payload))
requests.get(url, **_auth_kwargs())
```

Auth stops being something every call site has to remember, and `_auth_headers`
disappears into it — it was a two-line function used twice.

> **Why not a full `_request(http, method, ...)` wrapper?** The tests mock
> `session.post` and `_bot_runner.requests.get` directly. Routing everything
> through `http.request()` would break four of them, which makes it a rewrite
> rather than a refactor. Keeping `.post`/`.get` at the call sites costs one line
> each and keeps the safety net intact.

---

## 2. Make the retry schedule data, not arithmetic

This is the messiest part of the file. Four variables interact to express
"retry on 429":

```python
max_attempts = busy_retry_count + 1
backoff = busy_backoff_initial_sec
for attempt in range(max_attempts):
    if response.status_code == 429 and attempt < busy_retry_count:
        delay = min(backoff, busy_backoff_max_sec)
        time.sleep(delay)
        backoff = delay * 2 if delay > 0 else 0
        continue
```

To know whether the last attempt sleeps, you have to verify that
`attempt < busy_retry_count` is false exactly when `attempt == max_attempts - 1`.

Yield the delays instead:

```python
def _busy_delays():
    """Yield how long to wait before each retry, longest capped."""
    cfg = config.challenge.bot_runner
    delay = cfg.busy_backoff_initial_sec
    for _ in range(cfg.busy_retry_count):
        yield min(delay, cfg.busy_backoff_max_sec)
        delay *= 2
```

```python
# A trailing None marks the final attempt: report it, don't sleep on it.
for delay in [*_busy_delays(), None]:
    response = _request(http, "POST", server_url, "/api/runs", json=payload)
    if response.status_code != 429 or delay is None:
        break
    logger.info(f"bot-runner is busy for {framework_name}; retrying in {delay:.2f}s")
    time.sleep(delay)
```

No attempt counter, no `max_attempts`, no off-by-one to check. The retry policy
reads as a list of waits, which is what it is.

**Correction to the earlier draft of this plan:** I wrote that
`raise RuntimeError("unreachable bot-runner retry state")` on line 83 was
reachable. It isn't — the final iteration can't `continue`, so the loop always
exits by `return` or by `raise_for_status`. It's dead code. Rather than reword
it, **delete it** — the loop above can't fall through, so nothing needs guarding.

---

## 3. One "is this the last one?" in `wait_for_run`

```python
for attempt in range(5):        # why 5?
    ...
    except requests.RequestException:
        if attempt == 4: raise  # and why 4?
    if attempt < 4:             # ...again
        time.sleep(2**attempt)
```

`4` is `5 - 1` written by hand in two places, so all three must be kept in sync
— which is exactly the drift that left step 0's test red.

```python
_STATUS_POLL_ATTEMPTS = 5   # or 3, per step 0

for attempt in range(_STATUS_POLL_ATTEMPTS):
    is_last = attempt == _STATUS_POLL_ATTEMPTS - 1
    ...
```

One named constant, one derived flag, used twice. The count now lives in exactly
one place, so the next person to change it can't leave a test behind.

---

## 4. Extract the payload

13 of `trigger_run`'s lines are a dict literal. Moving it to `_build_payload()`
leaves the function as: build body, retry loop, read batch id.

Note while you're there: `headless` and `count` appear twice in the body — once
at the top level and again inside `metadata`. That's the wire format bot-runner
records, so **leave it**; it's a behaviour change, not a refactor.

---

## 5. Say what `wait_for_run` returns

```python
"""Check bot-runner status up to five times."""
```

Says what it does, not what it gives back — and the one thing a caller needs to
know is that `"timeout"` is *not* one of `_TERMINAL_STATUSES`.

```python
"""Poll bot-runner until the run reaches a terminal state.

Returns that status, or "timeout" if none was reached.
"""
```

---

## 6. Drop the inert annotation

```python
payload: dict[str, Any] = { ... }   →   payload = { ... }
```

The literal already shows it's a dict of strings to mixed values; the annotation
constrains nothing a reader or checker couldn't see. Remove
`from typing import Any` with it — it's the file's only use.

---

## Order

```
0. fix the red test         ← without this there is no safety net
1. _auth_kwargs             ← everything else sits on top of it
2. _busy_delays + delete the dead raise
3. _STATUS_POLL_ATTEMPTS / is_last
4. _build_payload
5. docstring
6. drop the annotation
```

Each step is independently committable and revertible.

## Verification

After step 0 the suite is green. Steps 1–6 change no behaviour, so
`tests/test_bot_runner_client.py` **must pass unmodified after every one of
them**. That's the check that the refactor stayed a refactor — if a step needs a
test edited, it went too far and should be split or dropped.

Expected size: 118 lines → roughly 100, with the retry logic down from four
interacting variables to one loop over a list.
