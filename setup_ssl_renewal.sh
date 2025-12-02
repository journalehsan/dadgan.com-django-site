#!/usr/bin/env bash
set -euo pipefail

# SSL Certificate Setup and Cron Installation Script
# This script installs the SSL renewal script and sets up automatic renewal

REMOTE_USER="rocky"
REMOTE_HOST="37.32.13.22"
REMOTE_PASS='Trk@#1403'

print() { printf "%s\n" "$*"; }
err() { printf "ERROR: %s\n" "$*" >&2; }

print "═══════════════════════════════════════════════════════════"
print "  Let's Encrypt SSL Auto-Renewal Setup"
print "═══════════════════════════════════════════════════════════"
print ""

# Step 1: Upload renewal script to server
print "[1/4] Uploading SSL renewal script to server..."
sshpass -p "$REMOTE_PASS" scp -P 22 -o StrictHostKeyChecking=no \
  ./renew_ssl.sh "$REMOTE_USER@$REMOTE_HOST:/tmp/" 2>&1 | grep -v "WARNING" || true

print "✓ Script uploaded"
print ""

# Step 2: Install script and make it executable
print "[2/4] Installing script on server..."
sshpass -p "$REMOTE_PASS" ssh -p 22 -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST" bash -c "'
set -e
sudo mv /tmp/renew_ssl.sh /usr/local/bin/renew_ssl.sh
sudo chmod +x /usr/local/bin/renew_ssl.sh
sudo chown root:root /usr/local/bin/renew_ssl.sh
echo \"✓ Script installed at /usr/local/bin/renew_ssl.sh\"
'" 2>&1 | grep -v "WARNING" || true

print ""

# Step 3: Run renewal now for expired certificates
print "[3/4] Running SSL renewal now (for expired certificates)..."
print "This will stop nginx, renew certificates, and restart nginx"
read -p "Continue? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sshpass -p "$REMOTE_PASS" ssh -p 22 -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST" \
      "sudo /usr/local/bin/renew_ssl.sh" 2>&1 | grep -v "WARNING" || true
    print ""
    print "✓ Manual renewal complete"
else
    print "Skipped manual renewal"
fi

print ""

# Step 4: Set up cron job
print "[4/4] Setting up cron job for automatic renewal (every 88 days)..."
sshpass -p "$REMOTE_PASS" ssh -p 22 -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST" bash -c "'
set -e

# Create cron job entry
CRON_JOB=\"0 3 */88 * * /usr/local/bin/renew_ssl.sh >> /var/log/letsencrypt-renewal.log 2>&1\"

# Check if cron job already exists
if sudo crontab -l 2>/dev/null | grep -q \"renew_ssl.sh\"; then
    echo \"Cron job already exists, updating...\"
    sudo crontab -l 2>/dev/null | grep -v \"renew_ssl.sh\" | sudo crontab -
fi

# Add new cron job
(sudo crontab -l 2>/dev/null; echo \"\$CRON_JOB\") | sudo crontab -

echo \"✓ Cron job installed\"
echo \"\"
echo \"Current cron jobs:\"
sudo crontab -l | grep renew_ssl.sh || true
'" 2>&1 | grep -v "WARNING" || true

print ""
print "═══════════════════════════════════════════════════════════"
print "  ✓ SSL Auto-Renewal Setup Complete!"
print "═══════════════════════════════════════════════════════════"
print ""
print "Configuration:"
print "  - Renewal script: /usr/local/bin/renew_ssl.sh"
print "  - Log file: /var/log/letsencrypt-renewal.log"
print "  - Cron schedule: Every 88 days at 3:00 AM"
print ""
print "Manual commands:"
print "  Run renewal now: sudo /usr/local/bin/renew_ssl.sh"
print "  View logs:       sudo tail -f /var/log/letsencrypt-renewal.log"
print "  Check cron:      sudo crontab -l"
print ""
print "To add more domains, edit the DOMAINS array in:"
print "  /usr/local/bin/renew_ssl.sh"
print ""
