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
    clients/
        bitcoin_client.py  # connects to local Bitcoin node via RPC
        x_client.py        # posts to X via tweepy v2
tests/
config.toml              # runtime config (fill in credentials)
state.json               # persists previous block height + total
pyproject.toml
```

## Dev/test
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Run
```bash
python -m audit
```

## Cron (daily at midnight)
```
0 9 * * * cd /path/to/bitcoin-audit && .venv/bin/python -m audit
```
