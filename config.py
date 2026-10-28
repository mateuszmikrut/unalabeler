"""
Env variables import for app
"""
import os
import math

## UniFi Controller Configuration
UL_UNIFI_HOST = os.getenv("UL_UNIFI_HOST", "")
UL_UNIFI_API_KEY = os.getenv("UL_UNIFI_API_KEY", "")

UL_UNIFI_SITE = os.getenv("UL_UNIFI_SITE", "default")
UL_VERIFY_SSL = os.getenv("UL_VERIFY_SSL", "true").strip().lower() in ("1", "true", "yes")
## App Configuration
UL_REFRESH_MIN = os.getenv("UL_REFRESH_MIN", "120")
UL_FIRSTSYNCDELAY_MIN = os.getenv("UL_FIRSTSYNCDELAY_MIN", "2")
UL_SHORTNAMES = os.getenv("UL_SHORTNAMES", "false").strip().lower() in ("1", "true", "yes")
## debug / logging
UL_LOGLEVEL = os.getenv("UL_LOGLEVEL", "INFO").upper()
UL_DRYRUN = os.getenv("UL_DRYRUN", "false").strip().lower() in ("1", "true", "yes")

def validate_config():
  missing = []
  if not UL_UNIFI_HOST.strip():
    missing.append("UL_UNIFI_HOST")
  if not UL_UNIFI_API_KEY.strip():
    missing.append("UL_UNIFI_API_KEY")
  if missing:
    raise ValueError(f"Missing mandatory environment variables: {', '.join(missing)}")
  for name, value, allow_zero in (
      ("UL_REFRESH_MIN", UL_REFRESH_MIN, False),
      ("UL_FIRSTSYNCDELAY_MIN", UL_FIRSTSYNCDELAY_MIN, True),
  ):
    try:
      minutes = float(value)
    except ValueError:
      raise ValueError(f"{name} must be a number of minutes") from None
    if not math.isfinite(minutes) or minutes < 0 or (minutes == 0 and not allow_zero):
      raise ValueError(f"{name} must be {'non-negative' if allow_zero else 'positive'}")
  for name in ("UL_DRYRUN", "UL_SHORTNAMES", "UL_VERIFY_SSL"):
    value = os.getenv(name)
    if value is not None and value.strip().lower() not in ("1", "true", "yes", "0", "false", "no"):
      raise ValueError(f"{name} must be true or false")
