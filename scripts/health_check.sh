#!/usr/bin/env bash
# Basic health check, run manually or from deploy.sh / an external monitor
# (e.g. UptimeRobot hitting the same paths). No extra monitoring
# infrastructure is stood up for this MVP — see docs/deployment.md.

set -uo pipefail

if [ -f .env ]; then
    # shellcheck disable=SC1091
    source .env
fi
DOMAIN="${DOMAIN:-localhost}"

status=0

check() {
    local name="$1"
    local url="$2"
    if curl -fsS -o /dev/null -m 5 "$url"; then
        echo "OK   - $name ($url)"
    else
        echo "FAIL - $name ($url)"
        status=1
    fi
}

check "Backend health" "http://localhost:8000/health"
check "Frontend" "http://localhost:3000"

if [ "$DOMAIN" != "localhost" ]; then
    check "HTTPS (public)" "https://$DOMAIN/api/v1/health"
fi

exit $status
