#!/usr/bin/env bash
# One-time VPS bootstrap for Ubuntu 24.04.
# Run as a user with sudo privileges: ./scripts/setup_vps.sh
#
# After this completes, log out and back in (for the docker group to take
# effect), then follow docs/deployment.md for the rest of the launch steps.

set -euo pipefail

echo "==> Updating packages"
sudo apt-get update -y
sudo apt-get upgrade -y

echo "==> Installing Docker Engine + Compose plugin"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sudo sh
fi
sudo usermod -aG docker "$USER"

echo "==> Installing UFW firewall and fail2ban"
sudo apt-get install -y ufw fail2ban

echo "==> Configuring firewall (SSH, HTTP, HTTPS only)"
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

echo "==> Enabling fail2ban (SSH brute-force protection)"
sudo systemctl enable --now fail2ban

echo "==> Checking for swap (recommended on small VPS tiers)"
if ! swapon --show | grep -q .; then
    echo "No swap detected. Creating a 2G swap file..."
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo "/swapfile none swap sw 0 0" | sudo tee -a /etc/fstab > /dev/null
else
    echo "Swap already configured; skipping."
fi

echo "==> Done."
echo "Next: log out/in for docker group membership, then clone the repo and"
echo "run scripts/init_letsencrypt.sh followed by scripts/deploy.sh."
echo "See docs/deployment.md for the full runbook."
