# Automated Scheduling with Cron

The project includes a cron file (`etc/cron.d/bitcoin-audit`) that runs the bot once a day at midnight.

## Installation steps

### 1. Copy the scheduling file
```bash
sudo cp etc/cron.d/bitcoin-audit /etc/cron.d/
```

### 2. Set proper permissions
```bash
sudo chmod 644 /etc/cron.d/bitcoin-audit
sudo chown root:root /etc/cron.d/bitcoin-audit
```

### 3. Create the log file
The cron job runs as user `pi` which cannot create files in `/var/log/` by default:
```bash
sudo touch /var/log/bitcoin-audit-cron.log
sudo chown pi:pi /var/log/bitcoin-audit-cron.log
```

### 4. Verify cron picked it up
```bash
sudo systemctl status cron
```

## Logs

Output is appended to `/var/log/bitcoin-audit-cron.log`:
```bash
tail -f /var/log/bitcoin-audit-cron.log
```
