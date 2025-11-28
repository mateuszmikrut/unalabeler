#!/usr/bin/env python3
"""
Sync DNS entries with UNIFI device labels
"""
import logging
import sys
from pathlib import Path
from time import sleep

from unifiapi import UniFiAPI
from config import UL_UNIFI_HOST, UL_UNIFI_USER, UL_UNIFI_PASS, UL_UNIFI_SITE, UL_LOGLEVEL, UL_DRYRUN, UL_REFRESH_MIN, UL_SHORTNAMES, validate_config
from dnsquery import lookup

## Logging
logging.basicConfig(
    level = getattr(logging, UL_LOGLEVEL, logging.INFO),
    format = '%(asctime)s - %(levelname)s - %(message)s'
)  
logger = logging.getLogger(__name__)
logger.info(f"Log level set to: {UL_LOGLEVEL}")

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

      if UL_SHORTNAMES:
          logger.debug(f"Using shortname for DNS name '{dnsname}'")
          dnsname = dnsname.split('.')[0]
          logger.debug(f"Shortened DNS name to: {dnsname}")

      if dnsname != name:
        if not UL_DRYRUN:
          ## Set the name in Unifi
          try:
            unifi.set_client_alias(client_id, dnsname)
            logger.info(f"Updated client with {ip} ({mac}) label to '{dnsname}'")
          except Exception as e:
            logger.error(f"Error updating client with {ip} ({mac}) label to '{dnsname}': {e}")
        else:
          logger.info(f"[DRY RUN] Would update client with {ip} ({mac}) label to '{dnsname}'")
      else:
        logger.debug(f"Client name '{name}' already matches DNS name '{dnsname}', no update needed")
      
      
  finally:
    logger.debug("Logging out from UniFi controller")
    unifi.logout()

  logger.info(f"Sync completed successfully - processed {len(clients)} devices")


if __name__ == "__main__":
  try:
    if UL_DRYRUN:
      logger.debug("DRY RUN only - single execution")
      main()
    else:
      while True:
        main()
        logger.debug(f"Sleeping for {UL_REFRESH_MIN} minutes before next sync")
        sleep(int(UL_REFRESH_MIN) * 60)
  except KeyboardInterrupt:
    logger.info("Received keyboard interrupt, exiting gracefully")
    sys.exit(0)
