# Automated Scheduling with Cron

The project includes a cron file (`bitcoin-audit`) that runs the bot once a day at midnight.

## Installation steps

### 1. Set the repo path

Update the `HOME` and `BITCOIN_AUDIT_HOME` variables at the top of `bitcoin-audit` to match where you cloned the repo.

### 2. Copy the scheduling file
```bash
sudo cp bitcoin-audit /etc/cron.d/
```

### 3. Set proper permissions
```bash
sudo chmod 644 /etc/cron.d/bitcoin-audit
sudo chown root:root /etc/cron.d/bitcoin-audit
```

### 4. Create the log file
The cron job runs as user `pi` which cannot create files in `/var/log/` by default:
```bash
sudo touch /var/log/bitcoin-audit-cron.log
sudo chown pi:pi /var/log/bitcoin-audit-cron.log
```

### 5. Verify cron picked it up
```bash
sudo systemctl status cron
```

## Logs

Output is appended to `/var/log/bitcoin-audit-cron.log`:
```bash
tail -f /var/log/bitcoin-audit-cron.log
```
