# Log rotation with logrotate

The project includes a logrotate drop-in (`bitcoin-audit`) that keeps
`/var/log/bitcoin-audit-cron.log` from growing unbounded on the Pi.

Rotation schedule:
- weekly, keeping 4 compressed copies (~one month of history)
- skipped if the log is missing or empty
- rotated file recreated as `pi:pi` (the cron user) so writes still succeed

## Installation steps

### 1. Copy the drop-in
```bash
sudo cp bitcoin-audit /etc/logrotate.d/
```

### 2. Set proper permissions
```bash
sudo chmod 644 /etc/logrotate.d/bitcoin-audit
sudo chown root:root /etc/logrotate.d/bitcoin-audit
```

### 3. Dry-run to verify
```bash
sudo logrotate -d /etc/logrotate.d/bitcoin-audit
```
The `-d` flag simulates rotation without touching any files — inspect the
output for errors or unexpected actions before relying on it.

### 4. Force a first rotation (optional)
```bash
sudo logrotate -f /etc/logrotate.d/bitcoin-audit
```
Subsequent rotations happen automatically via `/etc/cron.daily/logrotate`.
