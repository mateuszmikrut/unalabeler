"""
Env Configuration import for unalabeler
It also checks mandatory variables
"""
import os
import sys

# UniFi Controller Configuration
UL_UNIFI_HOST = os.getenv("UL_UNIFI_HOST", "")
UL_UNIFI_USER = os.getenv("UL_UNIFI_USER", "")
UL_UNIFI_PASS = os.getenv("UL_UNIFI_PASS", "")
UL_UNIFI_SITE = os.getenv("UL_UNIFI_SITE", "default")
UL_REFRESH_MIN = os.getenv("UL_REFRESH_MIN", "120")
UL_FIRSTSYNCDELAY_MIN = os.getenv("UL_FIRSTSYNCDELAY_MIN", "2")
UL_LOGLEVEL = os.getenv("UL_LOGLEVEL", "INFO").upper()
UL_SHORTNAMES = os.getenv("UL_SHORTNAMES", "true") in ("1", "true", "yes")
UL_DRYRUN = os.getenv("UL_DRYRUN", "false").lower() in ("1", "true", "yes")

def validate_config():
  """
  Exits with error if required parameters are missing.
  """
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
