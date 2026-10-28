"""UniFi OS Network API client, authenticated with a local API key."""

import logging
from urllib.parse import quote, urlsplit

import requests

logger = logging.getLogger(__name__)


class UniFiAPIError(RuntimeError):
    """A request failed, or UniFi returned an unsuccessful API response."""


class UniFiAPI:
    def __init__(self, host, api_key, site="default", *, verify_ssl=True, timeout=30):
        host = host.strip()
        if "://" not in host:
            host = f"https://{host}"
        parsed = urlsplit(host)
        if (parsed.scheme != "https" or not parsed.hostname or parsed.path not in ("", "/")
                or parsed.query or parsed.fragment or parsed.username or parsed.password):
            raise ValueError("UL_UNIFI_HOST must be a console hostname or HTTPS origin (no UI/API path)")
        if not api_key.strip():
            raise ValueError("UL_UNIFI_API_KEY must not be empty")
        if not site.strip() or site in (".", ".."):
            raise ValueError("UL_UNIFI_SITE must be a Network site name, usually 'default'")

        self.host = host.rstrip("/")
        self.site = site
        self.base_path = f"/proxy/network/api/s/{quote(site, safe='')}"
        self.timeout = timeout
        self.session = requests.Session()
        self.session.verify = verify_ssl
        self.session.headers.update({"Accept": "application/json", "X-API-Key": api_key})

    def _apirequest(self, method, path, payload=None):
        try:
            response = self.session.request(
                method, f"{self.host}{path}", json=payload,
                timeout=self.timeout, allow_redirects=False,
            )
        except requests.exceptions.SSLError as exc:
            raise UniFiAPIError(
                "TLS certificate verification failed. Trust the console certificate "
                "(REQUESTS_CA_BUNDLE), or set UL_VERIFY_SSL=false for a self-signed console."
            ) from exc
        except requests.exceptions.RequestException as exc:
            raise UniFiAPIError(f"UniFi {method} request failed: {exc}") from exc

        if response.status_code in (401, 403):
            raise UniFiAPIError(
                f"UniFi returned HTTP {response.status_code}. Check that the local Network "
                "API key is valid and has permission to read and rename clients."
            )
        if not 200 <= response.status_code < 300:
            raise UniFiAPIError(
                f"UniFi {method} {path} returned HTTP {response.status_code}; "
                "check the console address, site name, and Network API support."
            )
        try:
            result = response.json()
        except ValueError as exc:
            raise UniFiAPIError("UniFi returned a non-JSON response; check the console address") from exc

        if not isinstance(result, dict) or not isinstance(result.get("meta"), dict):
            raise UniFiAPIError("UniFi returned an unexpected Network API response")
        if result["meta"].get("rc") != "ok":
            raise UniFiAPIError(f"UniFi API error: {result['meta'].get('msg', 'unknown error')}")
        return result

    def get_clients(self):
        """Return connected clients with their Network user IDs."""
        result = self._apirequest("GET", f"{self.base_path}/stat/sta")
        clients = result.get("data")
        if not isinstance(clients, list) or any(not isinstance(c, dict) for c in clients):
            raise UniFiAPIError("UniFi returned an invalid client list")
        logger.debug("Retrieved %s clients from UniFi", len(clients))
        return clients

    def set_client_alias(self, identifier, newname):
        """Update only the client name, using a Network user _id or MAC address."""
        if not isinstance(identifier, str) or not identifier or identifier in (".", ".."):
            raise ValueError("A client ID or MAC address is required")
        if not isinstance(newname, str) or not newname.strip():
            raise ValueError("A non-empty client name is required")
        if ":" in identifier:
            client = next((c for c in self.get_clients()
                           if c.get("mac", "").lower() == identifier.lower()), None)
            if not client or not client.get("_id"):
                raise UniFiAPIError(f"No connected client found for MAC {identifier}")
            identifier = client["_id"]
        self._apirequest(
            "PUT", f"{self.base_path}/rest/user/{quote(identifier, safe='')}",
            {"name": newname},
        )
        return True

    def close(self):
        # API keys need no login/logout request or browser session/CSRF token.
        self.session.close()
