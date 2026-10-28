# UniFi OS Network client name (alias) labeler

[![AGPL v3](https://shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0.en.html)
[![Image Build](https://github.com/mateuszmikrut/unalabeler/actions/workflows/docker-build.yml/badge.svg
)](https://github.com/mateuszmikrut/unalabeler/actions/workflows/docker-build.yml)
[![GitHub last commit](https://img.shields.io/github/last-commit/mateuszmikrut/unalabeler)](https://github.com/mateuszmikrut/unalabeler/commit/main)
[![X Follow](https://img.shields.io/twitter/follow/mateusz_mikrut)](https://x.com/mateusz_mikrut)

Sync reverse DNS hostnames to connected clients' names in UniFi Network on a UniFi OS console. Clients without a valid IP address or reverse DNS result are skipped. Only the client `name` field is updated; matching names are left alone.

## UniFi OS and API keys

Create a local API key in your console's **Network → Settings → Control Plane → Integrations** (the menu location varies by Network version). Set `UL_UNIFI_API_KEY` to that key, with permission to read and update clients. Username/password login is no longer used.

Use the console's local HTTPS address, such as `https://unifi.example.com` or `192.168.1.1`, without a `/network` or `/proxy/network` suffix. Bare hostnames and IP addresses automatically use HTTPS. A port is allowed, for example `https://unifi.example.com:443`.

Client renaming uses the Network API through the UniFi OS proxy:

- Read connected clients: `GET /proxy/network/api/s/{site}/stat/sta`
- Update a client name: `PUT /proxy/network/api/s/{site}/rest/user/{_id}` with `{"name": "hostname"}`

These are legacy Network endpoints. The [public integration API](https://developer.ui.com/network) uses different IDs and does not currently list a client-renaming operation. This project therefore requires a Network version that accepts local API keys on the legacy endpoints. `UL_UNIFI_SITE` is the legacy site name (usually `default`), not an integration API site UUID. Direct standalone Network controllers without the UniFi OS proxy are not supported by this version.

Live-tested with Network 10.6.106: connected-client reads, reverse DNS lookup, a client-name update, and read-back verification.

## Configuration

All configuration is done via environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `UL_UNIFI_HOST` | Y | - | UniFi OS console hostname or HTTPS URL |
| `UL_UNIFI_API_KEY` | Y | - | Local Network API key with client-update permission |
| `UL_UNIFI_SITE` | N | `default` | Legacy Network site name |
| `UL_VERIFY_SSL` | N | `true` | Verify the console's TLS certificate |
| `UL_REFRESH_MIN` | N | `120` | Refresh interval in minutes (not in DRYRUN) |
| `UL_FIRSTSYNCDELAY_MIN` | N | `2` | Time waiting before first sync. Useful when starting together with Unifi App |
| `UL_SHORTNAMES` | N | `true` | Use short hostnames (strip domain suffix) |
| `UL_LOGLEVEL` | N | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `UL_DRYRUN` | N | `false` | Log proposed changes without applying them, then exit |

Boolean values accept `true`/`false`, `yes`/`no`, or `1`/`0`, ignoring case. For full DNS names such as `printer.lan`, set `UL_SHORTNAMES=false`. Short names are the default and will replace existing full names with their first label. A trailing DNS root dot is always removed.

TLS verification is enabled by default. For a private CA, set `REQUESTS_CA_BUNDLE` to its certificate bundle (mount that file when running in Docker). For a self-signed console you can explicitly set `UL_VERIFY_SSL=false`.


## Running

### Using Docker command

Export `UL_UNIFI_API_KEY` in your shell before running this command. To test code from this checkout, use the Compose build below instead of the published image.

```bash
docker run --rm \
  -e UL_UNIFI_HOST="https://unifi.example.com" \
  -e UL_UNIFI_API_KEY \
  -e UL_DRYRUN=true \
  ghcr.io/mateuszmikrut/unalabeler:latest
```

### Using Docker Compose

Copy [.env.example](.env.example) to `.env` and set your console address and API key. `.env` is ignored by Git and excluded from the Docker build context. Compose reads it automatically.

```bash
docker compose build
docker compose run --rm -e UL_DRYRUN=true unifi-labeler
```

After reviewing the proposed names, set `UL_DRYRUN=false` in `.env` and start the scheduled sync:

```bash
docker compose up -d --build
```

### Manual Python execution

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt

# Load your .env into the shell; Python uses the exported environment.
set -a
. ./.env
set +a

# Preview immediately and exit.
UL_DRYRUN=true python main.py --once

# Apply one sync immediately and exit.
UL_DRYRUN=false python main.py --once

# Run repeatedly, using UL_FIRSTSYNCDELAY_MIN and UL_REFRESH_MIN.
UL_DRYRUN=false python main.py
```

`--once` skips the initial delay and respects `UL_DRYRUN`. Single runs exit nonzero on configuration, connection, or update errors. Missing PTR records are skipped and reported in the summary.

## DNS Requirements

- Reverse DNS zone (PTR records) must be configured for your network
- The DNS server must be accessible from where this tool runs
- Hostnames should follow standard DNS naming conventions
- The process uses the operating system's resolver; Docker must also have access to your internal DNS server
- For larger networks with multiple DNS zones, use `UL_SHORTNAMES=false`

## MultiSite

Run one container per site with a different `UL_UNIFI_SITE` setting.

## Tests

The regression tests use mocked HTTP and DNS responses and do not contact your console:

```bash
python -m unittest discover -s tests -v
```
