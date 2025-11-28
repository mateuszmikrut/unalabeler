"""
UniFi Network Application API client.
Provides interface for authentication and client management.
"""

import requests
import urllib3
import logging

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class UniFiAPI:
  """UniFi Network Application API client."""
  
  def __init__(self, host, username, password, site="default"):
    self.host = host.rstrip('/')
    self.username = username
    self.password = password
    self.site = site
    self.session = requests.Session()
    self.session.verify = False  # Skip SSL verification for self-signed certs

    
  def login(self):
    """Authenticate with UniFi controller."""
    url = f"{self.host}/api/login"
    payload = {
      "username": self.username,
      "password": self.password,
      "remember": False
    }
    
    try:
      response = self.session.post(url, json=payload)
      response.raise_for_status()
      logger.info("Successfully logged in to UniFi controller")
      return True
    except requests.exceptions.RequestException as e:
      logger.error(f"Login failed: {e}")
      return False
  
  def get_clients(self):
    """Get list of all clients from UniFi."""
    url = f"{self.host}/api/s/{self.site}/stat/sta"
    
    try:
      response = self.session.get(url)
      response.raise_for_status()
      data = response.json()
      
      if data.get("meta", {}).get("rc") == "ok":
        clients = data.get("data", [])
        logger.info(f"Retrieved {len(clients)} clients from UniFi")
        return clients
      else:
        logger.error("Failed to get clients from UniFi")
        return []
    except requests.exceptions.RequestException as e:
      logger.error(f"Error getting clients: {e}")
      return []
  
  def set_client_alias(self, mac, name):
    """Set alias/name for a client by MAC address."""
    url = f"{self.host}/api/s/{self.site}/rest/user"
    
    # Find client ID first
    clients = self.get_clients()
    client = next((c for c in clients if c.get("mac", "").lower() == mac.lower()), None)
    
    if not client:
      logger.debug(f"Client {mac} not found in UniFi (might be offline)")
      return False
    
    client_id = client.get("_id")
    if not client_id:
      logger.warning(f"No client ID found for {mac}")
      return False
    
    # Update client alias
    payload = {
      "name": name,
      "_id": client_id
    }
    
    try:
      response = self.session.put(f"{url}/{client_id}", json=payload)
      response.raise_for_status()
      logger.info(f"Updated {mac} -> {name}")
      return True
    except requests.exceptions.RequestException as e:
      logger.error(f"Error updating client {mac}: {e}")
      return False
  
  def logout(self):
    """Logout from UniFi controller."""
    url = f"{self.host}/api/logout"
    try:
      self.session.post(url)
      logger.info("Logged out from UniFi controller")
    except Exception as e:
      logger.debug(f"Logout error (non-critical): {e}")
