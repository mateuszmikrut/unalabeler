import unittest
from unittest.mock import Mock, call, patch

import config
import main


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch("main.logger"))
        self.api = Mock()
        self.api.get_clients.return_value = [
            {"_id": "a", "ip": "192.0.2.10", "name": "old"},
            {"_id": "b", "ip": "192.0.2.11", "name": "matching"},
            {"_id": "c", "ip": "192.0.2.12", "name": "keep-without-ptr"},
            {"_id": "d", "name": "keep-without-ip"},
            {"_id": "e", "ip": "not-an-ip"},
        ]
        self.lookup = self.enterContext(patch("main.reverse_lookup", side_effect=[
            "printer.example.test.", "matching.example.test", None,
        ]))

    def test_dry_run_resolves_only_valid_ips_and_never_writes(self):
        counts = main.sync_clients(self.api, dry_run=True)
        self.assertEqual(counts, dict(total=5, good=1, updated=1, missing=3, errors=0))
        self.api.set_client_alias.assert_not_called()
        self.assertEqual(self.lookup.call_args_list, [call("192.0.2.10"), call("192.0.2.11"), call("192.0.2.12")])

    def test_live_sync_updates_only_mismatches_and_is_idempotent(self):
        counts = main.sync_clients(self.api)
        self.assertEqual(counts["updated"], 1)
        self.api.set_client_alias.assert_called_once_with("a", "printer")
        self.api.get_clients.return_value[0]["name"] = "printer"
        self.api.set_client_alias.reset_mock()
        self.lookup.side_effect = ["printer.example.test.", "matching.example.test", None]
        self.assertEqual(main.sync_clients(self.api)["updated"], 0)
        self.api.set_client_alias.assert_not_called()

    def test_fqdn_mode_strips_only_trailing_dot(self):
        self.api.get_clients.return_value = self.api.get_clients.return_value[:1]
        main.sync_clients(self.api, short_names=False)
        self.api.set_client_alias.assert_called_once_with("a", "printer.example.test")

    def test_missing_id_is_an_error_even_in_dry_run(self):
        self.api.get_clients.return_value = [{"ip": "192.0.2.10"}]
        self.assertEqual(main.sync_clients(self.api, dry_run=True)["errors"], 1)
        self.api.set_client_alias.assert_not_called()

    def test_empty_and_numeric_dns_answers_never_become_labels(self):
        for hostname in (".", "192.0.2.10", "2001:db8::1"):
            with self.subTest(hostname=hostname):
                self.api.get_clients.return_value = [{"_id": "a", "ip": "192.0.2.10"}]
                self.lookup.side_effect = [hostname]
                self.assertEqual(main.sync_clients(self.api)["missing"], 1)
        self.api.set_client_alias.assert_not_called()

    def test_failed_update_does_not_stop_other_clients(self):
        self.api.set_client_alias.side_effect = [RuntimeError("denied"), True]
        counts = main.sync_clients(self.api, short_names=False)
        self.assertEqual(counts["errors"], 1)
        self.assertEqual(counts["updated"], 1)

    def test_failed_client_fetch_propagates(self):
        self.api.get_clients.side_effect = RuntimeError("offline")
        with self.assertRaisesRegex(RuntimeError, "offline"):
            main.sync_clients(self.api)
        self.api.set_client_alias.assert_not_called()


class EntryPointTests(unittest.TestCase):
    def test_main_uses_api_key_and_closes_connection_on_failure(self):
        with patch("main.validate_config"), patch("main.UniFiAPI") as api_class:
            api_class.return_value.get_clients.side_effect = RuntimeError("offline")
            with self.assertRaises(RuntimeError):
                main.main()
            api_class.assert_called_once_with(main.UL_UNIFI_HOST, main.UL_UNIFI_API_KEY,
                                               main.UL_UNIFI_SITE, verify_ssl=main.UL_VERIFY_SSL)
            api_class.return_value.close.assert_called_once()

    def test_once_skips_sleep_and_propagates_failure_status(self):
        with patch("main.validate_config"), patch("main.main", return_value=1), patch("main.sleep") as sleep:
            self.assertEqual(main.cli(["--once"]), 1)
            sleep.assert_not_called()

    def test_invalid_boolean_fails_instead_of_accidentally_writing(self):
        with patch.object(config, "UL_UNIFI_HOST", "console.example"), \
                patch.object(config, "UL_UNIFI_API_KEY", "key"), \
                patch.dict("os.environ", {"UL_DRYRUN": "treu"}):
            with self.assertRaisesRegex(ValueError, "UL_DRYRUN"):
                config.validate_config()
