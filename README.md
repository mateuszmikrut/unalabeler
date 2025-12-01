# UniFi Netowrk Application device name (alias) labeler

[![AGPL v3](https://shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0.en.html)
[![Image Build](https://github.com/mateuszmikrut/unalabeler/actions/workflows/docker-build.yml/badge.svg
)](https://github.com/mateuszmikrut/unalabeler/actions/workflows/docker-build.yml)
[![GitHub last commit](https://img.shields.io/github/last-commit/mateuszmikrut/unalabeler)](https://github.com/mateuszmikrut/unalabeler/commit/main)
[![X Follow](https://img.shields.io/twitter/follow/mateusz_mikrut)](https://x.com/mateusz_mikrut)

Automatically sync devices DNS hostnames to UniFi Network Application client aliases using reverse DNS lookups. This tool queries DNS PTR records for each device present in UniFI Network Application and updates their names (labels) accordingly.
Suming up:

- 🔄 Synchronization of DNS names to UniFi client aliases  
- 🔍 Reverse DNS lookup for client identification
- 🏷️ Optional short name mode (removes domain suffix)
- 🧪 Dry-run mode for testing without making changes

## Configuration

All configuration is done via environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `UL_UNIFI_HOST` | Y | - | UniFi controller URL (e.g., `https://unifi.example.com`) |
| `UL_UNIFI_USER` | Y | - | UniFi controller username |
| `UL_UNIFI_PASS` | Y | - | UniFi controller password |
| `UL_UNIFI_SITE` | N | `default` | UniFi site name |
| `UL_REFRESH_MIN` | N | `120` | Refresh interval in minutes (not in DRYRUN) |
| `UL_FIRSTSYNCDELAY_MIN` | N | `2` | Time waiting before first sync. Useful when starting together with Unifi App |
| `UL_SHORTNAMES` | N | `true` | Use short hostnames (strip domain suffix) |
| `UL_LOGLEVEL` | N | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `UL_DRYRUN` | N | `false` | Dry-run mode - log changes without applying them - It runs and exit|


## Running

### Using Docker command

```bash
docker run -ti \
  -e UL_UNIFI_HOST="https://unifi.example.com" \
  -e UL_UNIFI_PASS="SuperSecretLoooongP@sSw0rd" \
  -e UL_UNIFI_USER="username" \
  -e UL_DRYRUN=true \
  ghcr.io/mateuszmikrut/unalabeler:latest
```

### Using Docker Compose

See [compose.yml](https://github.com/mateuszmikrut/unalabeler/blob/main/compose.yaml) for a complete example.

```bash
docker compose up -d
```

### Manual Python Execution (debug)

```bash
python -m venv venv
. ./venv/bin/activate
pip install -r requirements.txt
export UL_LOGLEVEL=debug
export UL_UNIFI_HOST="https://unifi.example.com"
export UL_UNIFI_PASS="SuperSecretLoooongP@sSw0rd"
export UL_UNIFI_USER="username"
python ./main.py
```

## DNS Requirements

- Reverse DNS zone (PTR records) must be configured for your network
- The DNS server must be accessible from where this tool runs
- Hostnames should follow standard DNS naming conventions
- For larger network with many DNS zones I recommend to not shorter names

## MultiSite

Not developed yet. Just run another container with different setup  
