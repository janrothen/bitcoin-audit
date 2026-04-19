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
config.toml              # runtime config (non-secret settings)
.env                     # credentials/secrets (not committed)
state.json               # persists previous block height, block time + total
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
The cron file sets `TZ=Europe/Zurich`, so `0 0 * * *` fires at Swiss midnight.
See `deploy/cron/README.md` for full installation steps.

## Log rotation
See `deploy/logrotate.d/bitcoin-audit` — copy it to `/etc/logrotate.d/` on the Pi.
Rotates `/var/log/bitcoin-audit-cron.log` weekly, keeping 4 compressed copies.
See `deploy/logrotate.d/README.md` for full installation steps.
