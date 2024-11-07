#!/usr/bin/env python3
import unittest
from sdwdate.remote_times import (
    run_command,
    check_remote,
    get_time_from_servers,
    remote_times_signal_handler
)


class TestRemoteTimes(unittest.TestCase):
    """
    TODO
    """

    def test_run_command(self):
        """
        TODO
        """


    def check_remote(self):
        """
        TODO
        """


    def get_time_from_servers(self):
        """
        TODO
        """


    def test_remote_times_signal_handler(self):
        """
        Test exit code.
        """
        with self.assertRaises(SystemExit) as exit_context:
            remote_times_signal_handler(-1, "")
        self.assertEqual(exit_context.exception.code, 127)
        with self.assertRaises(SystemExit) as exit_context:
            remote_times_signal_handler(0, "")
        self.assertEqual(exit_context.exception.code, 128)
        with self.assertRaises(SystemExit) as exit_context:
            remote_times_signal_handler(1, "")
        self.assertEqual(exit_context.exception.code, 129)


if __name__ == "__main__":
    unittest.main()
