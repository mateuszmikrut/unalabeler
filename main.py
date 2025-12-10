#!/usr/bin/env python3
"""
Sync DNS entries with UNIFI device labels
"""
import logging
import sys
from pathlib import Path
from time import sleep

from unifiapi import UniFiAPI
from config import UL_UNIFI_HOST, UL_UNIFI_USER, UL_UNIFI_PASS, UL_UNIFI_SITE, UL_LOGLEVEL, UL_DRYRUN, UL_REFRESH_MIN, UL_SHORTNAMES, UL_FIRSTSYNCDELAY_MIN, validate_config
from dnsquery import lookup

## Logging
logging.basicConfig(
    level = getattr(logging, UL_LOGLEVEL, logging.INFO),
    format = '%(asctime)s - %(levelname)s - %(message)s'
)  
logger = logging.getLogger(__name__)
logger.debug(f"Log level set to: {UL_LOGLEVEL}")

def main():
  logger.debug("Validating configuration")
  validate_config()

  # Connect to UniFi
  logger.debug("Logging in to UniFi controller")
  unifi = UniFiAPI(UL_UNIFI_HOST, UL_UNIFI_USER, UL_UNIFI_PASS, UL_UNIFI_SITE)
  logger.info("Connecting to UniFi controller")
  if not unifi.login():
    logger.error("Failed to login to UniFi controller, skipping this run")
    return
  
  try:
    logger.debug("Fetching clients from UniFi controller")
    clients = unifi.get_clients()

    # Counters for reporting
    total = len(clients)
    updated = 0
    missing = 0 
    good = 0
    errors = 0

    for client in clients:
      name = client.get('name', 'N/A')
      ip = client.get('ip', 'N/A')
      mac = client.get('mac', 'N/A')
      client_id = client.get('_id', 'N/A')
      logger.debug(f"Processing client: {name} <{ip}> ({client_id})")

      dnsname = lookup(ip)
      if dnsname is None:
        missing += 1
        logger.warning(f"No DNS name found for IP {ip}, ingnoring client")
        continue

      if UL_SHORTNAMES:
        logger.debug(f"Using shortname for DNS name '{dnsname}'")
        dnsname = dnsname.split('.')[0]
        logger.debug(f"Shortened DNS name to: {dnsname}")

      if dnsname != name:
        if not UL_DRYRUN:
          # Attempt to set the name in UniFi
          try:
            ok = unifi.set_client_alias(client_id, dnsname)
            if ok:
              updated += 1
              logger.info(f"Updated client {ip} ({mac}) label to '{dnsname}'")
            else:
              errors += 1
              logger.error(f"Failed to update client {ip} ({mac}) label to '{dnsname}'")
          except Exception as e:
            errors += 1
            logger.error(f"Error updating client {ip} ({mac}) label to '{dnsname}': {e}")
        else:
          updated += 1
          logger.info(f"[DRY RUN] Would update client {ip} ({mac}) label to '{dnsname}'")
      else:
        good += 1
        logger.debug(f"Client name '{name}' already matches DNS name '{dnsname}', no update needed")

  finally:
    logger.debug("Logging out from UniFi controller")
    unifi.logout()

  # Log a concise summary. Show `would_update` only for dry-run runs.
  if UL_DRYRUN:
    logger.info(f"Sync completed ({total} devices): ok={good}, would update={updated}, missing dns={missing}, errors={errors}")
  else:
    logger.info(f"Sync completed ({total} devices): ok={good}, updated={updated},  missing dns={missing},  errors={errors}")


if __name__ == "__main__":
  logger.info("Starting UniFi devices names sync")
  try:
    if UL_DRYRUN:
      logger.debug("DRY RUN only - single execution")
      main()
    else:
      logger.debug(f"Waiting {UL_FIRSTSYNCDELAY_MIN} minutes before first sync")
      sleep(int(UL_FIRSTSYNCDELAY_MIN) * 60)
      while True:
        try:
          main()
        except Exception as e:
          logger.error(f"Unexpected error during sync: {e}")
        logger.info(f"Sleeping for {UL_REFRESH_MIN} minutes before next sync")
        sleep(int(UL_REFRESH_MIN) * 60)
  except KeyboardInterrupt:
    logger.debug("Received keyboard interrupt, exiting gracefully")
    logger.info("Exiting sync")
    sys.exit(0)
