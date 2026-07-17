#!/usr/bin/env bash
# One-time Let's Encrypt certificate bootstrap.
#
# Nginx's production config needs certificates to exist before it can start
# (it references /etc/letsencrypt/live/$DOMAIN/*.pem). Certbot needs Nginx
# running to serve the ACME HTTP-01 challenge. This script breaks that
# chicken-and-egg problem with a temporary self-signed certificate, the
# standard pattern for nginx+certbot in Docker Compose.
#
# Run once, after scripts/setup_vps.sh and before the first
# `docker compose -f docker-compose.yml -f docker-compose.production.yml up`.
#
# Requires DOMAIN and CERTBOT_EMAIL to be set in .env.

set -euo pipefail

if [ ! -f .env ]; then
    echo "ERROR: .env not found. Copy .env.production.example to .env and fill it in first."
    exit 1
fi

# shellcheck disable=SC1091
source .env

if [ -z "${DOMAIN:-}" ] || [ "$DOMAIN" = "your-domain.example.com" ]; then
    echo "ERROR: Set a real DOMAIN in .env first."
    exit 1
fi

COMPOSE="docker compose -f docker-compose.yml -f docker-compose.production.yml"
VOLUME_NAME="aeos_certbot_conf"

echo "==> Creating a temporary self-signed certificate for $DOMAIN"
mkdir -p "certbot-init/live/$DOMAIN"
openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
    -keyout "certbot-init/live/$DOMAIN/privkey.pem" \
    -out "certbot-init/live/$DOMAIN/fullchain.pem" \
    -subj "/CN=$DOMAIN"

echo "==> Seeding the certbot_conf volume with the temporary certificate"
docker run --rm \
    -v "$(pwd)/certbot-init:/tmp/certbot-init" \
    -v "${VOLUME_NAME}:/etc/letsencrypt" \
    alpine sh -c "mkdir -p /etc/letsencrypt/live/$DOMAIN && cp /tmp/certbot-init/live/$DOMAIN/* /etc/letsencrypt/live/$DOMAIN/"

echo "==> Starting nginx with the temporary certificate"
$COMPOSE up -d nginx

echo "==> Requesting the real certificate from Let's Encrypt"
$COMPOSE run --rm certbot certonly \
    --webroot -w /var/www/certbot \
    --email "$CERTBOT_EMAIL" \
    -d "$DOMAIN" \
    --agree-tos \
    --no-eff-email \
    --force-renewal

echo "==> Reloading nginx with the real certificate"
$COMPOSE exec nginx nginx -s reload

rm -rf certbot-init

echo "==> Done. HTTPS is now live for https://$DOMAIN"
echo "Certbot's renew loop (the 'certbot' service) will keep it renewed automatically."
