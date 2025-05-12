#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Optional: log to a file
LOG_FILE="/var/log/macvlan_setup.log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "Setting up macvlan interface..."

# Create macvlan interface
sudo ip link add macvlan0 link eth0 type macvlan mode bridge
echo "Created macvlan0 interface"

# Assign IP address
sudo ip addr add 192.168.18.9/24 dev macvlan0
echo "Assigned IP to macvlan0"

# Bring up the interface
sudo ip link set macvlan0 up
echo "Interface macvlan0 is up"

# Add route to specific IP via macvlan
sudo ip route add 192.168.18.40/32 dev macvlan0
echo "Added static route via macvlan0"

echo "Macvlan setup completed successfully!"
