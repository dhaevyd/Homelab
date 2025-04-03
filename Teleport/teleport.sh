#!/bin/bash

# Disable Firewall  
sudo iptables -F
sudo iptables -X
sudo iptables -t nat -F
sudo iptables -t mangle -F
sudo iptables -t nat -X
sudo iptables -t mangle -X
sudo iptables -P INPUT ACCEPT
sudo iptables -P FORWARD ACCEPT
sudo iptables -P OUTPUT ACCEPT
sudo apt-get install iptables-persistent -y
sudo netfilter-persistent save

# Install Tailscale
curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/jammy.noarmor.gpg | sudo tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null
curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/jammy.tailscale-keyring.list | sudo tee /etc/apt/sources.list.d/tailscale.list
sudo apt-get update -y
sudo apt-get install tailscale -y
sudo systemctl enable --now tailscaled
sudo tailscale up --authkey tskey-auth


# Setup Teleport
TELEPORT_EDITION="oss"
TELEPORT_VERSION="17.3.3"
curl https://goteleport.com/static/install.sh | bash -s ${TELEPORT_VERSION?} ${TELEPORT_EDITION?}
sudo mkdir -p /var/lib/teleport/
sudo cp ~/files/teleport.yaml /etc/teleport.yaml
sudo cp ~/files/.privkey.pem /var/lib/teleport/privkey.pem
sudo cp ~/files/.fullchain.pem /var/lib/teleport/fullchain.pem
sudo chmod 600 /var/lib/teleport/privkey.pem
sudo chmod 600 /var/lib/teleport/fullchain.pem
sudo systemctl enable teleport
sudo systemctl start teleport
