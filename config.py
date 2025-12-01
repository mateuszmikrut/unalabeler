"""
Env variables import for app
"""
import os
import sys

## UniFi Controller Configuration
UL_UNIFI_HOST = os.getenv("UL_UNIFI_HOST", "")
UL_UNIFI_USER = os.getenv("UL_UNIFI_USER", "")
UL_UNIFI_PASS = os.getenv("UL_UNIFI_PASS", "")
UL_UNIFI_SITE = os.getenv("UL_UNIFI_SITE", "default")
## App Configuration
UL_REFRESH_MIN = os.getenv("UL_REFRESH_MIN", "120")
UL_FIRSTSYNCDELAY_MIN = os.getenv("UL_FIRSTSYNCDELAY_MIN", "2")
UL_SHORTNAMES = os.getenv("UL_SHORTNAMES", "true") in ("1", "true", "yes")
## debug / logging
UL_LOGLEVEL = os.getenv("UL_LOGLEVEL", "INFO").upper()
UL_DRYRUN = os.getenv("UL_DRYRUN", "false").lower() in ("1", "true", "yes")

def validate_config():
  missing = []
  
  if not UL_UNIFI_HOST:
    missing.append("UL_UNIFI_HOST")
  if not UL_UNIFI_USER:
    missing.append("UL_UNIFI_USER")
  if not UL_UNIFI_PASS:
    missing.append("UL_UNIFI_PASS")
  
  if missing:
    print(f"ERROR: Missing mandatory environment variables: {', '.join(missing)}", file=sys.stderr)
    sys.exit(1)
