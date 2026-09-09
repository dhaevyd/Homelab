# Homelab

A multi-node self-hosted infrastructure platform for running, securing,
monitoring and recovering real services across local hardware, cloud VMs
and a remote homelab.

##  🎯 Goals

- Repeatable service deployment
- Secure remote access
- Centralised routing and TLS
- DNS filtering and redundancy
- Metrics, logs and health monitoring
- Off-host backup and recovery
- Safe experimentation with production-style systems

## 🗺️  Architecture

....diagram coming soon....

Traffic generally follows:

Users and devices
→ VPN / Teleport / Cloudflare Tunnel
→ Traefik edge routing and TLS
→ Docker services
→ Persistent volumes and databases
→ Monitoring and off-host backups

## 🖥️ Hardware and nodes

| Icon | Name | Role | CPU | RAM | Storage | GPU / VRAM | Location |
|---|---|---|---|---:|---:|---|---|
| 🖥️ | d4rkcyber-pro | Primary homelab host | Ryzen 5 | 48 GB DDR4 | 9.5 TiB SSD | 12GB VRAM | Homelab |
| 🖥️ | d4rkcyber | Secondary host | Intel Core i7 | 32 GB DDR4 | 1.5 TiB SSD | — | Homelab |
| ☁️ | d4rkcloud | Cloud VM | ARM | 12 GB | 50 GB | — | OCI VPS |
| ☁️ | d4rkcloud-2 | Cloud VM | ARM | 12 GB | 50 GB | — | OCI VPS |
| 💾 | sentinel | Backup/recovery VM | Intel | 1 GB | 50 GB | — | OCI VPS |
| 🧰 | the-4th | Utility VM | Intel | 1 GB | 50 GB | — | OCI VPS |
| 🌐 | zabuza | Remote homelab node | Intel | 10 GB | 20 GB | — | Remote homelab |
| 🪟 | Winning-11 | Windows lab client | Intel Core i7 | 32 GB DDR5 | 1 TB SSD | 4 GB VRAM | Homelab |



## Platform layers

### 🔐 Edge and access
- 🚦 Traefik
- ☁️ Cloudflare Tunnel
- 🔒 Cloudflare DNS challenge
- 🛂 Teleport
- 🔗 Tailscale
- 🛡️ WireGuard

### 🧩 Core services
- ⚙️ n8n
- 💬 Mattermost
- ☁️ Nextcloud
- 📝 AFFiNE
- 🧱 AdGuard Home

### 📊 Operations
- 📈 Prometheus
- 📊 Grafana
- ❤️ Uptime Kuma
- 🖥️ Glances
- 📡 Beszel
- 📜 Dozzle
- 🐳 Portainer
- 🏠 Homepage

### 💾 Data and recovery
- 🗄️ Persistent Docker volumes
- 🐘 PostgreSQL-backed services
- 🔄 AdGuard configuration replication
- 🌙 Nightly off-host backups
- 🛟 Sentinel and Flash-NAS recovery targets

## 📁  Repository structure
- Apps/       Application projects
- Docker/     Docker Compose service deployments
- Teleport/   Teleport access configuration

## 🚀  Deployment pattern

Each service is isolated in its own directory and normally includes:

- `compose.yaml`
- Environment variable template
- Persistent data paths
- Reverse-proxy labels where required
- External `proxy` network integration
- Restart and health-check configuration

## 🛡️  Security notes

- Secrets belong in `.env` files and must never be committed.
- Public services should be routed through the approved access layer.
- TLS certificates are issued through the Cloudflare DNS challenge.
- Services are not exposed by default unless explicitly configured.
- Backups must be tested through restoration, not only confirmed by file presence.

## 🧭  Current roadmap

- Add a complete architecture diagram
- Document service ownership and dependencies
- Add restore procedures
- Add health-check and monitoring standards
- Add disaster-recovery runbooks
- Add service inventory with production/development status
