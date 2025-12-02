#!/usr/bin/env bash
set -euo pipefail

# Let's Encrypt SSL Certificate Auto-Renewal Script
# Renews SSL certificates using certbot standalone mode
# Designed to run via cron every 88 days

LOG_FILE="/var/log/letsencrypt-renewal.log"
NGINX_SERVICE="nginx"

# List of domains to renew
DOMAINS=(
    "dadgan.com"
    "www.dadgan.com"
    # Add more domains as needed
)

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $*" | tee -a "$LOG_FILE" >&2
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    error "This script must be run as root"
    exit 1
fi

log "Starting SSL certificate renewal process"

# Check if nginx is running
if systemctl is-active --quiet "$NGINX_SERVICE"; then
    NGINX_WAS_RUNNING=true
    log "Stopping nginx service..."
    systemctl stop "$NGINX_SERVICE"
    
    # Wait a bit to ensure port 80 is free
    sleep 2
    
    if systemctl is-active --quiet "$NGINX_SERVICE"; then
        error "Failed to stop nginx"
        exit 1
    fi
    log "Nginx stopped successfully"
else
    NGINX_WAS_RUNNING=false
    log "Nginx is not running"
fi

# Renew certificates
RENEWAL_SUCCESS=true

for domain in "${DOMAINS[@]}"; do
    log "Renewing certificate for: $domain"
    
    if certbot certonly \
        --standalone \
        --non-interactive \
        --agree-tos \
        --email admin@${domain} \
        --domains "$domain" \
        --force-renewal; then
        log "✓ Successfully renewed certificate for $domain"
    else
        error "Failed to renew certificate for $domain"
        RENEWAL_SUCCESS=false
    fi
done

# Restart nginx if it was running
if [ "$NGINX_WAS_RUNNING" = true ]; then
    log "Starting nginx service..."
    systemctl start "$NGINX_SERVICE"
    
    sleep 2
    
    if systemctl is-active --quiet "$NGINX_SERVICE"; then
        log "✓ Nginx started successfully"
    else
        error "Failed to start nginx"
        exit 1
    fi
fi

# Verify nginx configuration and reload
if [ "$NGINX_WAS_RUNNING" = true ]; then
    if nginx -t 2>&1 | tee -a "$LOG_FILE"; then
        log "Nginx configuration is valid, reloading..."
        systemctl reload "$NGINX_SERVICE"
        log "✓ Nginx reloaded"
    else
        error "Nginx configuration test failed"
        exit 1
    fi
fi

if [ "$RENEWAL_SUCCESS" = true ]; then
    log "✓ SSL certificate renewal completed successfully"
    
    # Display certificate expiry dates
    log "Certificate expiry dates:"
    for domain in "${DOMAINS[@]}"; do
        if [ -f "/etc/letsencrypt/live/$domain/cert.pem" ]; then
            EXPIRY=$(openssl x509 -enddate -noout -in "/etc/letsencrypt/live/$domain/cert.pem" | cut -d= -f2)
            log "  $domain: expires on $EXPIRY"
        fi
    done
    
    exit 0
else
    error "Some certificate renewals failed. Check logs for details."
    exit 1
fi
