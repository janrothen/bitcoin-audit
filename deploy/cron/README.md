# Automated Scheduling with Cron

The project includes a cron file (`bitcoin-audit`) that runs the bot once a day at midnight.

## Installation steps

### 1. Set the repo path

Update the `BITCOIN_AUDIT_HOME` variable at the top of `bitcoin-audit` to match where you cloned the repo.

### 2. Verify the system timezone

Debian's default cron matches schedules against the **system** timezone — the `TZ` variable in the cron file only sets the job's environment. For the job to fire at Swiss midnight:

```bash
timedatectl                                        # should show Europe/Zurich
sudo timedatectl set-timezone Europe/Zurich        # if it doesn't
```

### 3. Copy the scheduling file
```bash
sudo cp bitcoin-audit /etc/cron.d/
```

### 4. Set proper permissions
```bash
sudo chmod 644 /etc/cron.d/bitcoin-audit
sudo chown root:root /etc/cron.d/bitcoin-audit
```

### 5. Create the log file
The cron job runs as user `pi` which cannot create files in `/var/log/` by default:
```bash
sudo touch /var/log/bitcoin-audit-cron.log
sudo chown pi:pi /var/log/bitcoin-audit-cron.log
```

### 6. Verify cron picked it up
```bash
sudo systemctl status cron
```

## Updating an existing deployment

The cron job runs `.venv/bin/python -m audit`, which uses the installed package in the venv — **not** the working tree. After pulling new code you must reinstall, otherwise cron keeps executing the old version:

```bash
cd $BITCOIN_AUDIT_HOME
git pull
.venv/bin/pip install .
```

## Logs

Output is appended to `/var/log/bitcoin-audit-cron.log`:
```bash
tail -f /var/log/bitcoin-audit-cron.log
```
