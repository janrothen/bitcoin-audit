# Bitcoin Audit

A bot on X (@BitcoinAudit) that posts the current Bitcoin block height and circulating supply once a day at midnight via cron.

## Target environment
- Hardware: Raspberry Pi 4, 8 GB RAM
- OS: Debian GNU/Linux 13 (trixie), aarch64
- Python: 3.13.5

## Structure
```
src/audit/
    __main__.py          # entry point: python -m audit
    config.py            # tomllib config loader
    audit_bot.py         # AuditBot
    post_creator.py
    protocols.py         # BitcoinClientProtocol, XClientProtocol (test seams)
    state.py             # State dataclass (state.json contract)
    clients/
        bitcoin_client.py  # connects to local Bitcoin node via RPC
        x_client.py        # posts to X via tweepy v2
tests/
assets/
    post.png             # example X post (used in README)
deploy/
    cron/
        bitcoin-audit    # cron file — copy to /etc/cron.d/ on the Pi
        README.md        # installation steps
    logrotate.d/
        bitcoin-audit    # logrotate drop-in — copy to /etc/logrotate.d/
        README.md        # installation steps
reviews/                 # code review reports (dated .md files)
config.toml              # runtime config (non-secret settings)
.env                     # credentials/secrets (not committed)
state.json               # persists previous block height, block time + total
CODE_REVIEW_PROMPT.md    # project-specific code review prompt
pyproject.toml
```

## Dev/test
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Run
```bash
python -m audit
```

## Cron (daily at midnight, Europe/Zurich)
See `deploy/cron/bitcoin-audit` — copy it to `/etc/cron.d/` on the Pi.
Debian's cron matches `0 0 * * *` against the **system** timezone, so the Pi
must be set to `Europe/Zurich` (`timedatectl`); the `TZ` variable in the cron
file only affects the job's environment.
See `deploy/cron/README.md` for full installation steps.

## State file semantics
- First run (no `state.json`): save state, don't post — first post is on run two.
- Legacy schema (missing `block_time`): warn and re-bootstrap, don't crash.
- Corrupt file (bad JSON, missing other keys, wrong types): raise, never post a bogus delta.
- Writes are power-safe: tmp file + fsync + `os.replace` + parent-dir fsync. Don't simplify this.

## Log rotation
See `deploy/logrotate.d/bitcoin-audit` — copy it to `/etc/logrotate.d/` on the Pi.
Rotates `/var/log/bitcoin-audit-cron.log` weekly, keeping 4 compressed copies.
See `deploy/logrotate.d/README.md` for full installation steps.
