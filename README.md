# Bitcoin Audit

Posts the current Bitcoin block height and circulating supply once a day at midnight to X ([@BitcoinAudit](https://x.com/BitcoinAudit)) via cron.

## Configuration

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

```dotenv
BITCOIN_RPC_USER=your_rpc_username
BITCOIN_RPC_PASSWORD=your_rpc_password

X_CONSUMER_KEY=...
X_CONSUMER_SECRET=...
X_ACCESS_TOKEN=...
X_ACCESS_TOKEN_SECRET=...
```

X credentials are obtained from the [X Developer Portal](https://console.x.com/). Create a project and app there, then generate the consumer keys and access tokens with read/write permissions.

Edit `config.toml` to customise the behaviour (the `state` section controls where the state file is stored — see [State file](#state-file) below):

```toml
[bitcoin.rpc]
ip      = "192.168.2.100"
port    = 8332
timeout = 900

[state]
file = "state.json"
```

## Requirements

- Raspberry Pi (tested on Pi 4, 8 GB RAM)
- Running Bitcoin Core node (local RPC access)
- Python 3.13+

## Install & run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m audit
```

## Run as a cron job (daily at midnight)

```bash
# Install the cron file
sudo cp etc/cron.d/bitcoinaudit /etc/cron.d/
sudo chmod 644 /etc/cron.d/bitcoinaudit
sudo chown root:root /etc/cron.d/bitcoinaudit

# Create the log file (cron runs as user pi)
sudo touch /var/log/bitcoinaudit-cron.log
sudo chown pi:pi /var/log/bitcoinaudit-cron.log

# Verify cron picked it up
sudo systemctl status cron
```

To follow logs:
```bash
tail -f /var/log/bitcoinaudit-cron.log
```

## State file

`state.json` persists the block height and circulating supply from the previous run. It is used to calculate the delta shown in each post.

The file is created automatically on first run — no post is made that time, since there is no previous state to compare against. The second run proceeds normally.

If the file is deleted, the bot bootstraps itself again on the next run.
