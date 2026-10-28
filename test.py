#!/usr/bin/env python3
"""
Sync DNS entries with UNIFI device labels
"""
import logging
import sys
from pathlib import Path
from time import sleep

from unifiapi import UniFiAPI
from config import UL_UNIFI_HOST, UL_UNIFI_API_KEY, UL_UNIFI_SITE, UL_LOGLEVEL, UL_DRYRUN, UL_REFRESH_MIN, UL_SHORTNAMES, UL_FIRSTSYNCDELAY_MIN, validate_config
from dnsquery import lookup

## Logging
logging.basicConfig(
    level = getattr(logging, UL_LOGLEVEL, logging.INFO),
    format = '%(asctime)s - %(levelname)s - %(message)s'
)  
logger = logging.getLogger(__name__)
logger.debug(f"Log level set to: {UL_LOGLEVEL}")

logger.debug("Validating configuration")
validate_config()

# Connect to UniFi
unifi = UniFiAPI(UL_UNIFI_HOST, UL_UNIFI_API_KEY, UL_UNIFI_SITE)
print(unifi.get_clients())
exit()


  