#!/usr/bin/env python3
"""
Test the timesanitycheck module.
"""

import io
import subprocess
import time
import unittest
from unittest.mock import Mock, MagicMock, patch
import stem
import stem.connection
import stem.socket
from sdwdate.timesanitycheck import (
    time_consensus_sanity_check,
    static_time_sanity_check
)


class TestTimeSanityCheck(unittest.TestCase):
    """
    Test time sanity.
    """

    @patch('stem.connection.connect')
    def test_time_consensus_sanity_check(self, mock_connect):
        """
        TODO: AI generated
        """
        # Mock the Tor controller
        mock_controller = MagicMock()
        mock_controller.get_info.side_effect = [
            "2023-01-01 00:00:00",
            "2023-01-02 00:00:00"
        ]
        mock_connect.return_value = mock_controller
        status, error, valid_after, valid_until = time_consensus_sanity_check(int(time.time()))
        self.assertEqual(status, 'ok')
        self.assertEqual(error, '')
        self.assertEqual(valid_after, "2023-01-01 00:00:00")
        self.assertEqual(valid_until, "2023-01-02 00:00:00")


    @patch('stem.connection.connect')
    def test_time_consensus_sanity_check_connection_error(self, mock_connect):
        mock_connect.side_effect = Exception("Connection error")
        status, error, _, _ = time_consensus_sanity_check(int(time.time()))
        self.assertEqual(status, 'ok')
        self.assertIn('Could not request from Tor control connection', error)


    @patch('sys.stdout', new_callable = io.StringIO)
    @patch('stem.util.system.is_running')
    @patch('os.path.exists', Mock(return_value = True))
    @patch('stem.socket.ControlSocketFile', Mock(side_effect = stem.SocketError('failed')))
    @patch('stem.socket.ControlPort', Mock(side_effect = stem.SocketError('failed')))
    def test_time_consensus_sanity_check_connection_error_plssssssssss(self, mock_connect):
        mock_connect.side_effect = Exception("Connection error")
        status, error, _, _ = time_consensus_sanity_check(int(time.time()))
        self.assertEqual(status, 'ok')
        self.assertIn('Could not request from Tor control connection', error)
    #def test_failue_with_the_default_endpoint(self, is_running_mock, stdout_mock):
    #    is_running_mock.return_value = False
    #    self.assertRaises(AttributeError)


    def test_static_time_sanity_check_sane(self):
        """
        Test sane static time.
        """
        current_time = int(time.time())
        self.assertEqual(static_time_sanity_check(current_time),
                         ('sane', 'none'))


    def test_static_time_sanity_check_slow(self):
        """
        Test slow static time.
        """
        with subprocess.Popen(
            "/usr/bin/minimum-unixtime-show",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        ) as proc:
            stdout, _ = proc.communicate()
            minimum_unixtime = int(stdout.decode())
        current_time = minimum_unixtime - 1
        self.assertEqual(static_time_sanity_check(current_time),
                         ('slow', 'none'))


    def test_static_time_sanity_check_fast(self):
        """
        Test fast static time.
        """
        # TODO: create a class to import this variable instead of hard code.
        expiration_unixtime = 1999936800
        current_time = expiration_unixtime + 1
        self.assertEqual(static_time_sanity_check(current_time),
                         ('fast', 'none'))


if __name__ == "__main__":
    unittest.main()
