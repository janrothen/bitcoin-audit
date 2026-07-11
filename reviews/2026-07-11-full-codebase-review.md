# Code Review — Full Codebase

- **Date:** 2026-07-11
- **Scope:** full codebase at `main` @ `ecd1792` (working tree clean; no diff, so this reviews the files themselves)
- **Reviewer prompt:** CODE_REVIEW_PROMPT.md (kept outside the repo)
- **Status:** all 7 suggestions fixed on branch `fix/code-review-findings`
  (2026-07-11). For 2.4 the friendlier option was implemented: a legacy
  pre-`block_time` state file now re-bootstraps with a warning instead of
  crashing nightly. For 2.1 the cron file and docs now state the real
  mechanism (system timezone); **still verify `timedatectl` on the Pi shows
  `Europe/Zurich`.**

---

## 1. Critical

**None found.** The paths that matter most here — Decimal money math, the
power-safe `_save_state` sequence, bootstrap-vs-corrupt state handling, and
secret handling — are all correct as written and covered by tests. The items
below are real but none silently corrupts a post or loses state on the current
happy path.

## 2. Suggestions

### 2.1 `TZ` in the cron file does not control *scheduling* on Debian's default cron

`deploy/cron/bitcoin-audit:10,13` — the file sets `TZ=Europe/Zurich` and the
project docs (CLAUDE.md, deploy README) claim this makes `0 0 * * *` fire at
Swiss midnight. On Debian's default `cron` (vixie-derived), `TZ` in a crontab
only affects the **job's environment**; the schedule is matched against the
daemon's (system) timezone. Timezone-aware scheduling needs cronie's `CRON_TZ`
or a systemd timer.

- **Failure scenario:** Pi system timezone is `UTC` (a common server default)
  → the job fires at 00:00 UTC = 01:00/02:00 Swiss time, and `block_time`
  deltas drift from the intended midnight-to-midnight cadence.
- **Minimal fix:** verify `timedatectl` on the Pi shows `Europe/Zurich`. If it
  does, the job already fires correctly — update the comment/docs to say the
  *system* timezone is the mechanism, since the `TZ` line only affects the
  job's environment. If it doesn't, set the system timezone (or switch to
  cronie + `CRON_TZ`).

### 2.2 `State.from_dict` silently accepts a float `total` and inherits binary junk

[state.py:22](../src/audit/state.py) — `Decimal(data["total"])` is exact when
`total` is a string (the format `to_dict` writes), but if a state file ever
contains a bare JSON number (hand-edit, manual restore, a future serializer
change), `json.loads` yields a `float` and `Decimal(float)` expands it to its
full binary representation (`Decimal(19243704.10556611)` →
`19243704.1055661104619503021240234375`).

- **Failure scenario:** someone restores `state.json` by hand with
  `"total": 19243704.10556611` (no quotes) → next run computes the supply
  delta against the junk-precision value and **silently posts wrong digits** —
  the worst failure class in this project, and the monotonicity guard won't
  catch it.
- **Minimal fix:** `total=Decimal(str(data["total"]))` — same defensive
  pattern `bitcoin_client.get_total_amount` already uses. One line, and
  `from_dict` is already lenient (`int(...)`) for the other fields, so this is
  consistent.

### 2.3 `TypeError` escapes the corrupt-state taxonomy

[audit_bot.py:67](../src/audit/audit_bot.py) — `_fetch_previous` catches
`(KeyError, InvalidOperation, ValueError)` and re-raises as
`RuntimeError("Corrupt state file …")`. But valid-JSON-wrong-shape content
raises `TypeError` instead:

- `null` or `[1, 2]` as file content → `data["block_height"]` → `TypeError`
- `{"block_height": null, …}` → `int(None)` → `TypeError`

- **Failure scenario:** a truncated-then-partially-restored file containing
  `null` crashes the cron run with a raw `TypeError` traceback instead of the
  designed `Corrupt state file at <path>` message. Same operational outcome
  (crash, no bogus post — good), but the log line you'd read at 7am no longer
  tells you what happened or where.
- **Minimal fix:** add `TypeError` to the except tuple at
  [audit_bot.py:67](../src/audit/audit_bot.py), plus one parametrized case
  (`"null"`) in `test_corrupt_state_file_raises`.

### 2.4 Legacy pre-`block_time` state files are treated as corrupt, with no migration path

[state.py:21](../src/audit/state.py) / [audit_bot.py:67](../src/audit/audit_bot.py)
— `block_time` was added to the schema recently (commit `5972868` era). A state
file written by the previous version lacks it and now raises
`RuntimeError: Corrupt state file` — evidence such files exist: the untracked
`state.json` in this working tree is exactly one
(`{"block_height": 769026, "total": "19243704.10556611"}`).

- **Failure scenario:** deploy the current code onto the Pi over a
  pre-migration `state.json` → the job crashes **every night** until someone
  notices the log and deletes the file by hand. Unattended cron + no retry
  makes this a silent multi-day outage.
- **Minimal fix:** if the Pi has already been migrated (likely, if the new
  code has run successfully since the schema change), just delete the stale
  local `state.json` and document in `state.py` that schema changes require
  deleting the Pi's state file (accepting one bootstrap day). A friendlier
  option: treat a missing `block_time` key specifically as "legacy →
  re-bootstrap" (log a warning, return `None`) rather than corrupt.

### 2.5 Misleading comment in the Bitcoin client test fixture

[test_bitcoin_client.py:10](../tests/test_bitcoin_client.py) — the mock sets
`"total_amount": 20006091.78041419  # float, matching the real RPC response type`.
The comment is wrong: `python-bitcoinrpc` parses JSON with
`parse_float=decimal.Decimal` (authproxy.py:190), so the real response type is
`Decimal`, not `float`. The production code is robust either way
(`Decimal(str(...))` handles both), but the comment codifies a false belief
about the RPC boundary that a future refactor might act on (e.g. "it's already
a float, so `Decimal(str())` is pointless — simplify to `Decimal(x)`" would be
exactly the wrong move if the mock were then also "fixed" to float).

- **Minimal fix:** change the comment to note the real type is `Decimal`
  (via `parse_float`), and that the float in the mock deliberately exercises
  the defensive `Decimal(str(...))` path.

### 2.6 No test for temp-file cleanup on a failed write

[audit_bot.py:95-97](../src/audit/audit_bot.py) — the `except: tmp.unlink(...)`
cleanup branch in `_save_state` is untested.
`test_no_tmp_file_left_after_successful_run` covers the happy path only.

- **Minimal fix:** one test that patches `os.replace` (or `json.dumps`) to
  raise, asserts the exception propagates, `state.json` still holds the old
  content, and no `state.tmp` remains.

### 2.7 Minor: cron sets `HOME` to the project directory

`deploy/cron/bitcoin-audit:7` — `HOME=/home/pi/raspberry/bitcoin-audit` is used
as a cd target, but `HOME` semantically means the user's home; any tool the job
transitively invokes that reads `~/.config` or `~/.cache` will look inside the
project dir. Harmless today, surprising later.

- **Minimal fix:** use a differently-named variable
  (`APP=/home/pi/raspberry/bitcoin-audit` … `cd $APP`) and leave `HOME` alone.

## 3. What works well

- **`_save_state`** ([audit_bot.py:75-97](../src/audit/audit_bot.py)) is a
  textbook power-safe write — tmp + file `fsync` + `os.replace` + parent-dir
  `fsync`, with the *why* documented inline. Don't let anyone "simplify" it.
- **Money discipline:** `Decimal` end to end, `Decimal(str(...))` at the RPC
  boundary, `ROUND_DOWN` on the mined percentage so it never overstates, and
  string serialization in `to_dict`.
- **Bootstrap vs. corrupt** semantics in `_fetch_previous` are exactly right:
  missing file warns and skips the post; bad file refuses to post. The
  parametrized corruption tests lock this in.
- **Monotonicity guards** in `PostCreator.__init__` catch out-of-order/corrupt
  state before anything reaches X.
- **Ordering of `run()`** (post before save) gives at-least-once posting with
  no lost deltas — the right trade-off for an unattended bot.
- **Protocols + constructor injection** keep the tests fast and mock-free at
  the seam that matters; `MockBitcoinClient`/`MockXClient` are pleasantly dumb.
- **Secrets:** `.env`-only via `env()` which fails loudly, and
  `quote(..., safe="")` on RPC credentials so a `@`/`:` in a password can't
  break or leak through the URL.
- The **25-hour duration threshold** and its rationale are documented *and*
  pinned by boundary tests (`25*3600 - 1` / `25*3600`).

---

*7 suggestions, 0 critical. Suggested priority: 2.1 (verify Pi timezone — five
minutes, affects every post's timing) → 2.2 / 2.3 (two one-line hardening
fixes) → 2.4 (delete stale local state.json, document migration) → rest.*
