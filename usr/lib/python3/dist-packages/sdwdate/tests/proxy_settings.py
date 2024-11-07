#!/usr/bin/env python3
"""
Test the proxy_settings module.
"""

import unittest
from unittest import mock
from sdwdate.proxy_settings import proxy_settings


class TestProxySettings(unittest.TestCase):
    """
    Test retrieval of proxy settings.
    """

    @mock.patch("os.path.exists")
    def test_proxy_settings_default_settings_non_whonix(self, mock_exists):
        """
        Test absent Whonix marker.
        """
        mock_exists.side_effect = [False, False, False]
        self.assertEqual(proxy_settings(), ("127.0.0.1", "9050"))


    @mock.patch("os.path.exists")
    @mock.patch("os.access")
    @mock.patch("subprocess.Popen")
    def test_proxy_settings_default_settings(self, mock_popen, mock_access,
                                             mock_exists):
        """
        Test absent configuration files.
        """
        mock_ip = "10.0.0.1"
        mock_ip_option = 'GATEWAY_IP="' + mock_ip + '"'
        mock_exists.side_effect = [True, True, False]
        mock_access.return_value = True
        mock_process = mock.Mock()
        mock_process.communicate.return_value = (mock_ip_option, "")
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process
        result = proxy_settings()
        self.assertEqual(result, (mock_ip, "9108"))


    @mock.patch("os.path.exists")
    @mock.patch("glob.glob")
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    def test_randomize_time_config_file_access(self, mock_open, mock_glob,
                                               mock_exists):
        """
        Test configuration files read against the intended ones.
        """
        mock_exists.side_effect = [False, False, True]
        mock_glob.return_value = [
            "/etc/sdwdate/30_default.conf",
            "/etc/sdwdate/40_anon-apps-config.conf",
        ]
        mock_open_readlines = mock_open.return_value.readlines
        mock_open_readlines.return_value = []
        proxy_settings()
        mock_exists.assert_called_with("/etc/sdwdate.d/")
        mock_glob.assert_called_with("/etc/sdwdate.d/*.conf")


    @mock.patch("os.path.exists")
    @mock.patch("glob.glob")
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    def test_proxy_settings_config_empty(self, mock_open, mock_glob,
                                         mock_exists):
        """
        Test configuration files that do not set the proxy IP and port.
        """
        mock_exists.side_effect = lambda path: {
            "/usr/share/whonix": False,
            "/etc/sdwdate.d/": True
        }.get(path, False)
        mock_glob.return_value = [
            "/etc/sdwdate/30_default.conf",
            "/etc/sdwdate/40_anon-apps-config.conf",
        ]
        mock_open_readlines = mock_open.return_value.readlines
        mock_open_readlines.return_value = []
        self.assertEqual(proxy_settings(), ("127.0.0.1", "9050"))
        mock_open_readlines.return_value = [
            "#PROXY_IP=127.0.0.1",
            "#PROXY_PORT=9000"
        ]
        self.assertEqual(proxy_settings(), ("127.0.0.1", "9050"))
        mock_open_readlines.return_value = [
            " PROXY_IP=127.0.0.1",
            " PROXY_PORT=9000"
        ]
        self.assertEqual(proxy_settings(), ("127.0.0.1", "9050"))


    @mock.patch("os.path.exists")
    @mock.patch("glob.glob")
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    def test_proxy_settings_config_to_fix(self, mock_open, mock_glob,
                                          mock_exists):
        """
        Test configurations that should not work and must be fixed.
        """
        mock_exists.side_effect = lambda path: {
            "/usr/share/whonix": False,
            "/etc/sdwdate.d/": True
        }.get(path, False)
        mock_glob.return_value = [
            "/etc/sdwdate/30_default.conf",
            "/etc/sdwdate/40_anon-apps-config.conf",
        ]
        mock_open_readlines = mock_open.return_value.readlines
        mock_open_readlines.return_value = [
            " PROXY_IP=",
            " PROXY_PORT="
        ]
        self.assertEqual(proxy_settings(), ("127.0.0.1", "9050"))
        mock_open_readlines.return_value = [
            " PROXY_IP=foo",
            " PROXY_PORT=foo"
        ]
        self.assertEqual(proxy_settings(), ("127.0.0.1", "9050"))
        mock_open_readlines.return_value = [
            " PROXY_IP_FOO=bar",
            " PROXY_PORT_FOO=bar"
        ]
        self.assertEqual(proxy_settings(), ("127.0.0.1", "9050"))
        mock_open_readlines.return_value = [
            "PROXY_IP_FOO=0.39",
            "PROXY_PORT_FOO=0.39"
        ]
        self.assertEqual(proxy_settings(), ("0.39", "0.39"))


    @mock.patch("os.path.exists")
    @mock.patch("glob.glob")
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    def test_proxy_settings_set(self, mock_open, mock_glob, mock_exists):
        """
        Test configuration files that set the proxy settings.
        """
        mock_exists.side_effect = lambda path: {
            "/usr/share/whonix": False,
            "/etc/sdwdate.d/": True
        }.get(path, False)
        mock_exists.return_value = True
        mock_glob.return_value = [
            "/etc/sdwdate/30_default.conf",
            "/etc/sdwdate/40_anon-apps-config.conf",
        ]
        mock_open_readlines = mock_open.return_value.readlines
        mock_open_readlines.return_value = [
            "PROXY_IP=129.0.0.1",
            "PROXY_IP=130.0.0.1",
            "PROXY_PORT=9000",
            "PROXY_PORT=9004"
        ]
        result = proxy_settings()
        self.assertEqual(result, ("130.0.0.1", "9004"))
        self.assertIsInstance(result[0], str)
        self.assertIsInstance(result[1], str)


if __name__ == "__main__":
    unittest.main()
