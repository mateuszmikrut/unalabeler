# UniFi Labeler

Automatically sync devices DNS hostnames to UniFi Network Application client aliases using reverse DNS lookups. This tool queries DNS PTR records for each device present in UniFI Network Applicationand updates their names (labels) accordingly.
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
| `UL_LOGLEVEL` | N | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `UL_SHORTNAMES` | N | `true` | Use short hostnames (strip domain suffix) |
| `UL_DRYRUN` | N | `false` | Dry-run mode - log changes without applying them - It runs and exit|


## Running

### Using Docker Compose

See [docker-compose.yml](docker-compose.yml) for a complete example.

```bash
docker-compose up -d
```

### Manual Python Execution (debug)

```bash
# VirtualENV and dependencies
python -m venv venv
. ./venv/activate
pip install -r requirements.txt
export UL_LOGLEVEL=debug
export UL_UNIFI_HOST="https://unifi.example.com"
export UL_UNIFI_PASS="SuperSecreatLoooongP@sSw0rd"
export UL_UNIFI_USER=unifiusername
python ./main.py
```

## DNS Requirements

- Reverse DNS zone (PTR records) must be configured for your network
- The DNS server must be accessible from where this tool runs
- Hostnames should follow standard DNS naming conventions
- For larger network with many DNS zones I recommend to not shorter names

## MultiSite

Not developed yet. Just run another container with different setup  
