# UniFi OS Network client name (alias) labeler

[![AGPL v3](https://shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0.en.html)
[![Image Build](https://github.com/mateuszmikrut/unalabeler/actions/workflows/docker-build.yml/badge.svg
)](https://github.com/mateuszmikrut/unalabeler/actions/workflows/docker-build.yml)
[![GitHub last commit](https://img.shields.io/github/last-commit/mateuszmikrut/unalabeler)](https://github.com/mateuszmikrut/unalabeler/commit/main)
[![X Follow](https://img.shields.io/twitter/follow/mateusz_mikrut)](https://x.com/mateusz_mikrut)

Sync reverse DNS hostnames to connected clients names on UniFi OS console. 

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

## DNS Requirements

- Reverse DNS zone (PTR records) must be configured for your network
- The DNS server must be accessible from where this tool runs
- Hostnames should follow standard DNS naming conventions
- The process uses the operating system's resolver; Docker must also have access to your internal DNS server
- For larger networks with multiple DNS zones, use `UL_SHORTNAMES=false`

## MultiSite

Run one container per site with a different `UL_UNIFI_SITE` setting.

