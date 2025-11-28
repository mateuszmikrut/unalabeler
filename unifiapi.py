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
      logger.debug("Successfully logged in to UniFi controller")
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
        logger.debug(f"Retrieved {len(clients)} clients from UniFi")
        return clients
      else:
        logger.error("Failed to get clients from UniFi")
        return []
    except requests.exceptions.RequestException as e:
      logger.error(f"Error getting clients: {e}")
      return []
  
  def set_client_alias(self, identifier, newname):
    """
    Set alias/name for a client.
    
    Args:
      identifier (str): Client ID or MAC address
      newname (str): New name/alias to set
      
    Returns:
      bool: True if successful, False otherwise
    """
    url = f"{self.host}/api/s/{self.site}/rest/user"
    
    # Check if identifier looks like a MAC address (contains colons)
    if ':' in identifier:
      # It's a MAC, need to find the client ID
      logger.debug(f"Identifier '{identifier}' is a MAC address, looking up client ID")
      clients = self.get_clients()
      client = next((c for c in clients if c.get("mac", "").lower() == identifier.lower()), None)
      
      if not client:
        logger.warning(f"Client with MAC {identifier} not found in UniFi")
        return False
      
      client_id = client.get("_id")
      if not client_id:
        logger.error(f"No client ID found for MAC {identifier}")
        return False
      logger.debug(f"Found client ID: {client_id}")
    else:
      # Assume it's already a client ID
      logger.debug(f"Using identifier '{identifier}' as client ID directly")
      client_id = identifier
    
    # Update client alias
    payload = {
      "name": newname
    }
    
    try:
      response = self.session.put(f"{url}/{client_id}", json=payload)
      response.raise_for_status()
      logger.debug(f"Updated client {identifier} name to '{newname}'")
      return True
    except requests.exceptions.RequestException as e:
      logger.error(f"Error updating client {identifier}: {e}")
      return False
  
  def logout(self):
    """Logout from UniFi controller."""
    url = f"{self.host}/api/logout"
    try:
      self.session.post(url)
      logger.debug("Logged out from UniFi controller")
    except Exception as e:
      logger.debug(f"Logout error (non-critical): {e}")
