# Automated Scheduling with Cron

The project includes a cron file (`etc/cron.d/bitcoinaudit`) that runs the bot once a day at 09:00.

## Installation steps

### 1. Copy the scheduling file
```bash
sudo cp etc/cron.d/bitcoinaudit /etc/cron.d/
```

### 2. Set proper permissions
```bash
sudo chmod 644 /etc/cron.d/bitcoinaudit
sudo chown root:root /etc/cron.d/bitcoinaudit
```

### 3. Verify cron picked it up
```bash
sudo systemctl status cron
```

## Logs

Output is appended to `/var/log/bitcoinaudit-cron.log`:
```bash
tail -f /var/log/bitcoinaudit-cron.log
```
