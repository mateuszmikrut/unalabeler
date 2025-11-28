#!/usr/bin/env python3
"""
Sync dnsmasq DHCP lease hostnames to UniFi Network Application client aliases.
Reads /var/lib/dnsmasq/dnsmasq.leases and updates UniFi client names via API.
"""
import logging
import sys
from pathlib import Path

from unifiapi import UniFiAPI
from config import UL_UNIFI_HOST, UL_UNIFI_USER, UL_UNIFI_PASS, UL_UNIFI_SITE, UL_LOGLEVEL, UL_DRYRUN, validate_config
from dnsquery import lookup


## Logging
logging.basicConfig(
    level = getattr(logging, UL_LOGLEVEL),
    format = '%(asctime)s - %(levelname)s - %(message)s'
)  
logger = logging.getLogger(__name__)
if UL_LOGLEVEL == "DEBUG":
  logger.info("Debug logging is enabled")

def main():
  logger.info("Starting UniFi hostname sync")
  logger.debug("Validating configuration")
  validate_config()

  # Connect to UniFi
  logger.debug("Logging in to UniFi controller")
  unifi = UniFiAPI(UL_UNIFI_HOST, UL_UNIFI_USER, UL_UNIFI_PASS, UL_UNIFI_SITE)
  if not unifi.login():
    logger.error("Failed to login to UniFi controller")
    sys.exit(1)
  
  try:
    logger.debug("Fetching clients from UniFi controller")
    clients = unifi.get_clients()
    
    for client in clients:
      name = client.get('name', 'N/A')
      ip = client.get('ip', 'N/A')
      mac = client.get('mac', 'N/A')
      client_id = client.get('_id', 'N/A')
      logger.debug(f"Processing client: {name} <{ip}> ({client_id})")

      dnsname = lookup(ip)
      if dnsname == None:
        logger.debug(f"No DNS name found for IP {ip}, skipping client")
        continue

      if dnsname != name:
        if not UL_DRYRUN:
          # TODO: Update names in Unifi
          pass
        else:
          logger.info(f"[DRY RUN] Would update client with {ip} ({mac}) label to '{dnsname}'")
      

  finally:
    # Always logout
    unifi.logout()
  
  logger.info("Sync completed successfully")


if __name__ == "__main__":
  main()
