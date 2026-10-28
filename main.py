#!/usr/bin/env python3
"""Sync reverse DNS hostnames to UniFi OS client names."""

import argparse
import logging
import sys
from time import sleep

from config import (
    UL_UNIFI_HOST, UL_UNIFI_API_KEY, UL_UNIFI_SITE, UL_VERIFY_SSL,
    UL_LOGLEVEL, UL_DRYRUN, UL_REFRESH_MIN, UL_SHORTNAMES,
    UL_FIRSTSYNCDELAY_MIN, validate_config,
)
from dnsquery import is_valid_ip, reverse_lookup
from unifiapi import UniFiAPI

logger = logging.getLogger(__name__)


def sync_clients(unifi, *, dry_run=False, short_names=True):
    clients = unifi.get_clients()
    counts = dict(total=len(clients), good=0, updated=0, missing=0, errors=0)
    for client in clients:
        name = client.get("name") or ""
        ip = client.get("ip")
        mac = client.get("mac", "N/A")
        client_id = client.get("_id")

        # Never forward-resolve a missing/invalid IP and use its address as a name.
        if not isinstance(ip, str) or not is_valid_ip(ip):
            counts["missing"] += 1
            logger.warning("Client %s has no valid IP address, skipping", mac)
            continue
        dnsname = reverse_lookup(ip)
        if not dnsname:
            counts["missing"] += 1
            logger.warning("No DNS name found for IP %s, ignoring client", ip)
            continue
        dnsname = dnsname.rstrip(".")
        if not dnsname or is_valid_ip(dnsname):
            counts["missing"] += 1
            logger.warning("No usable DNS hostname for IP %s, ignoring client", ip)
            continue
        if short_names:
            dnsname = dnsname.split(".")[0]
        if not dnsname:
            counts["missing"] += 1
            continue
        if dnsname == name:
            counts["good"] += 1
            logger.debug("Client %s already matches DNS name '%s'", ip, dnsname)
            continue
        if not isinstance(client_id, str) or not client_id:
            counts["errors"] += 1
            logger.error("Client %s (%s) has no client ID, skipping", ip, mac)
            continue
        if dry_run:
            counts["updated"] += 1
            logger.info("[DRY RUN] Would update client %s (%s) label from '%s' to '%s'",
                        ip, mac, name, dnsname)
            continue
        try:
            if unifi.set_client_alias(client_id, dnsname):
                counts["updated"] += 1
                logger.info("Updated client %s (%s) label from '%s' to '%s'", ip, mac, name, dnsname)
            else:
                counts["errors"] += 1
                logger.error("Failed to update client %s (%s) label to '%s'", ip, mac, dnsname)
        except Exception as exc:
            counts["errors"] += 1
            logger.error("Error updating client %s (%s): %s", ip, mac, exc)

    logger.info("Sync completed (%s devices): ok=%s, %s=%s, missing dns=%s, errors=%s",
                counts["total"], counts["good"], "would update" if dry_run else "updated",
                counts["updated"], counts["missing"], counts["errors"])
    return counts


def main():
    validate_config()
    logger.info("Connecting to UniFi OS Network with an API key")
    unifi = UniFiAPI(UL_UNIFI_HOST, UL_UNIFI_API_KEY, UL_UNIFI_SITE, verify_ssl=UL_VERIFY_SSL)
    try:
        counts = sync_clients(unifi, dry_run=UL_DRYRUN, short_names=UL_SHORTNAMES)
        return 1 if counts["errors"] else 0
    finally:
        unifi.close()


def cli(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--once", action="store_true", help="Run once immediately, then exit (respects UL_DRYRUN)")
    args = parser.parse_args(argv)
    logging.basicConfig(level=getattr(logging, UL_LOGLEVEL, logging.INFO),
                        format="%(asctime)s - %(levelname)s - %(message)s")
    try:
        validate_config()
        if args.once or UL_DRYRUN:
            return main()
        logger.info("Waiting %s minutes before first sync", UL_FIRSTSYNCDELAY_MIN)
        sleep(float(UL_FIRSTSYNCDELAY_MIN) * 60)
        while True:
            try:
                main()
            except Exception as exc:
                logger.error("Sync failed: %s", exc)
            logger.info("Sleeping for %s minutes before next sync", UL_REFRESH_MIN)
            sleep(float(UL_REFRESH_MIN) * 60)
    except KeyboardInterrupt:
        logger.info("Exiting sync")
        return 0
    except Exception as exc:
        logger.error("Sync failed: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(cli())
