import unittest
from unittest.mock import Mock, patch

import requests

from unifiapi import UniFiAPI, UniFiAPIError


def response(body, status=200):
    result = Mock(status_code=status)
    result.json.return_value = body
    return result


class UniFiAPITests(unittest.TestCase):
    def setUp(self):
        self.api = UniFiAPI("console.example:443", "test-key")
        self.addCleanup(self.api.close)
        self.request = self.enterContext(patch.object(self.api.session, "request"))

    def test_connected_clients_unwraps_network_envelope(self):
        clients = [{"_id": "client-id", "ip": "192.0.2.10"}]
        self.request.return_value = response({"meta": {"rc": "ok"}, "data": clients})
        self.assertEqual(self.api.get_clients(), clients)
        self.request.assert_called_once_with(
            "GET", "https://console.example:443/proxy/network/api/s/default/stat/sta",
            json=None, timeout=30, allow_redirects=False,
        )
        self.assertEqual(self.api.session.headers["X-API-Key"], "test-key")
        self.assertTrue(self.api.session.verify)

    def test_update_only_sends_name_to_persistent_user_route(self):
        self.request.return_value = response({"meta": {"rc": "ok"}, "data": []})
        self.assertTrue(self.api.set_client_alias("client-id", "printer"))
        self.request.assert_called_once_with(
            "PUT", "https://console.example:443/proxy/network/api/s/default/rest/user/client-id",
            json={"name": "printer"}, timeout=30, allow_redirects=False,
        )

    def test_mac_lookup_uses_matching_client_id(self):
        self.request.side_effect = [
            response({"meta": {"rc": "ok"}, "data": [{"_id": "saved-id", "mac": "aa:bb:cc:dd:ee:ff"}]}),
            response({"meta": {"rc": "ok"}, "data": []}),
        ]
        self.api.set_client_alias("AA:BB:CC:DD:EE:FF", "printer")
        self.assertTrue(self.request.call_args.args[1].endswith("/rest/user/saved-id"))

    def test_http_success_with_api_error_is_not_reported_as_update(self):
        self.request.return_value = response({"meta": {"rc": "error", "msg": "api.err.NoPermission"}})
        with self.assertRaisesRegex(UniFiAPIError, "NoPermission"):
            self.api.set_client_alias("client-id", "printer")

    def test_http_failures_and_redirects_are_not_empty_client_lists(self):
        for status in (302, 401, 403, 404, 500):
            with self.subTest(status=status):
                self.request.return_value = response({}, status)
                with self.assertRaisesRegex(UniFiAPIError, str(status)):
                    self.api.get_clients()

    def test_bad_responses_are_not_empty_client_lists(self):
        for body in ({}, [], {"meta": None}, {"meta": {"rc": "ok"}},
                     {"meta": {"rc": "ok"}, "data": ["not a client"]}):
            with self.subTest(body=body):
                self.request.return_value = response(body)
                with self.assertRaises(UniFiAPIError):
                    self.api.get_clients()
        self.request.return_value.json.side_effect = ValueError("HTML login page")
        with self.assertRaisesRegex(UniFiAPIError, "non-JSON"):
            self.api.get_clients()

    def test_tls_and_timeout_errors_are_actionable(self):
        for error, message in ((requests.exceptions.SSLError(), "certificate"),
                               (requests.exceptions.Timeout(), "request failed")):
            with self.subTest(error=error):
                self.request.side_effect = error
                with self.assertRaisesRegex(UniFiAPIError, message):
                    self.api.get_clients()

    def test_https_origin_and_self_signed_override(self):
        api = UniFiAPI("https://console.example/", "key", "other", verify_ssl=False)
        self.addCleanup(api.close)
        self.assertEqual(api.host, "https://console.example")
        self.assertEqual(api.base_path, "/proxy/network/api/s/other")
        self.assertFalse(api.session.verify)

    def test_invalid_host_or_empty_update_never_sends_request(self):
        for host in ("", "https://", "http://console.example", "https://console.example/network",
                     "https://user:password@console.example"):
            with self.subTest(host=host), self.assertRaises(ValueError):
                UniFiAPI(host, "key")
        for identifier, name in ((None, "printer"), ("", "printer"), ("id", ""), ("id", " ")):
            with self.subTest(identifier=identifier, name=name), self.assertRaises(ValueError):
                self.api.set_client_alias(identifier, name)
        self.request.assert_not_called()
