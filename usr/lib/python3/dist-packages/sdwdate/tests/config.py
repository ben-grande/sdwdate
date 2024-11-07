#!/usr/bin/env python3
"""
Test the config module.
"""

from io import TextIOBase
import unittest
from unittest import mock
import subprocess
from sdwdate.sdwdate import TimeSourcePool
from sdwdate.config import (
    time_human_readable,
    time_replay_protection_file_read,
    randomize_time_config,
    allowed_failures_config,
    allowed_failures_calculate,
    get_comment,
    get_comment_pool_single,
    sort_pool,
    read_pools
)


class TestConfig(unittest.TestCase):
    """
    Test stripping HTML from message.
    """

    def test_time_human_readable(self):
        """
        Test a converting Unix time to human readable format.
        """
        # TODO: only works if comparing the same nodes on the same time zone.
        self.assertEqual(time_human_readable(1730192583),
                         "2024-10-29 09:03:03")
        self.assertEqual(time_human_readable(1730192594),
                         "2024-10-29 09:03:14")


    @mock.patch("subprocess.Popen")
    def test_time_replay_protection_file_read(self, mock_popen):
        """
        Relay check to avoid false-positives due to sdwdate inaccuracy.
        """
        mock_process = mock.Mock()
        unixtime, human_readable_time = 1730192998, "2024-10-29 09:09:58"
        mock_process.communicate.return_value = (unixtime, human_readable_time)
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process
        stdout, stderr = time_replay_protection_file_read()
        self.assertEqual(stdout, unixtime - 100)
        self.assertEqual(stderr, human_readable_time)
        self.assertIsInstance(stdout, int)
        self.assertIsInstance(stderr, str)
        mock_popen.assert_called_once_with(
            "/usr/bin/minimum-unixtime-show",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        #with subprocess.Popen(
        #    "/usr/bin/minimum-unixtime-show",
        #    stdout=subprocess.PIPE,
        #    stderr=subprocess.PIPE
        #) as proc:
        #    stdout, stderr = proc.communicate()
        #    # TODO: create a class variable that holds "100" to be reused.
        #    # TODO: deduct the same variable from human readable time
        #    minimum_unixtime = int(stdout.decode()) - 100
        #    minimum_time_human_readable = stderr.decode("utf-8").strip()
        #self.assertEqual(time_replay_protection_file_read(),
        #                 (minimum_unixtime, minimum_time_human_readable))


    @mock.patch("os.path.exists")
    def test_randomize_time_config_without_directory(self, mock_exists):
        """
        Test absent configuration directory.
        """
        mock_exists.return_value = False
        self.assertFalse(randomize_time_config())


    @mock.patch("os.path.exists")
    @mock.patch("glob.glob")
    def test_randomize_time_config_without_file(self, mock_glob, mock_exists):
        """
        Test absent configuration files.
        """
        mock_exists.return_value = True
        mock_glob.return_value = []
        self.assertFalse(randomize_time_config())


    @mock.patch("os.path.exists")
    @mock.patch("glob.glob")
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    def test_randomize_time_config_return_false(self, mock_open, mock_glob,
                                                mock_exists):
        """
        Test configurations that returns false.
        """
        mock_exists.return_value = True
        mock_glob.return_value = [
            "/etc/sdwdate/30_default.conf",
            "/etc/sdwdate/40_anon-apps-config.conf",
        ]
        mock_open_readlines = mock_open.return_value.readlines
        mock_open_readlines.return_value = ["RANDOMIZE_TIME="]
        self.assertFalse(randomize_time_config())
        mock_open_readlines.return_value = ["RANDOMIZE_TIME=false"]
        self.assertFalse(randomize_time_config())
        mock_open_readlines.return_value = ["#RANDOMIZE_TIME=true"]
        self.assertFalse(randomize_time_config())
        mock_open_readlines.return_value = [" RANDOMIZE_TIME=true"]
        self.assertFalse(randomize_time_config())
        mock_open_readlines.return_value = [
            "RANDOMIZE_TIME=true",
            "RANDOMIZE_TIME=false"
        ]
        self.assertFalse(randomize_time_config())


    @mock.patch("os.path.exists")
    @mock.patch("glob.glob")
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    def test_randomize_time_config_return_true(self, mock_open, mock_glob,
                                               mock_exists):
        """
        Test configurations that returns true.
        """
        mock_exists.return_value = True
        mock_glob.return_value = [
            "/etc/sdwdate/30_default.conf",
            "/etc/sdwdate/40_anon-apps-config.conf",
        ]
        mock_open_readlines = mock_open.return_value.readlines
        mock_open_readlines.return_value = [
            "RANDOMIZE_TIME=false",
            "RANDOMIZE_TIME=true"
        ]
        self.assertTrue(randomize_time_config())
        mock_open_readlines.return_value = ["RANDOMIZE_TIME=true"]
        self.assertTrue(randomize_time_config())


    @mock.patch("os.path.exists")
    @mock.patch("glob.glob")
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    def test_randomize_time_config_file_access(self, mock_open, mock_glob,
                                               mock_exists):
        """
        Test configuration files read against the intended ones.
        """
        mock_exists.return_value = True
        mock_glob.return_value = [
            "/etc/sdwdate/30_default.conf",
            "/etc/sdwdate/40_anon-apps-config.conf",
        ]
        mock_open_readlines = mock_open.return_value.readlines
        mock_open_readlines.return_value = []
        randomize_time_config()
        mock_exists.assert_called_with("/etc/sdwdate.d/")
        mock_glob.assert_called_with("/etc/sdwdate.d/*.conf")


    @mock.patch("os.path.exists")
    def test_allowed_failures_config_without_directory(self, mock_exists):
        """
        Test absent configuration directory.
        """
        mock_exists.return_value = False
        result = allowed_failures_config()
        self.assertEqual(result, 0.34)
        self.assertIsInstance(result, float)


    @mock.patch("os.path.exists")
    @mock.patch("glob.glob")
    def test_allowed_failures_config_without_file(self, mock_glob,
                                                  mock_exists):
        """
        Test absent configuration files.
        """
        mock_exists.return_value = True
        mock_glob.return_value = []
        result = allowed_failures_config()
        self.assertEqual(result, 0.34)
        self.assertIsInstance(result, float)


    @mock.patch("os.path.exists")
    @mock.patch("glob.glob")
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    def test_allowed_failures_config_empty(self, mock_open, mock_glob,
                                           mock_exists):
        """
        Test configuration files that do not set the ratio.
        """
        mock_exists.return_value = True
        mock_glob.return_value = [
            "/etc/sdwdate/30_default.conf",
            "/etc/sdwdate/40_anon-apps-config.conf",
        ]
        mock_open_readlines = mock_open.return_value.readlines
        mock_open_readlines.return_value = []
        # TODO: create class init variable to store 0.34
        self.assertEqual(allowed_failures_config(), 0.34)
        mock_open_readlines.return_value = ["#MAX_FAILURE_RATIO=0.1"]
        self.assertEqual(allowed_failures_config(), 0.34)
        mock_open_readlines.return_value = [" MAX_FAILURE_RATIO=0.1"]
        self.assertEqual(allowed_failures_config(), 0.34)


    @mock.patch("os.path.exists")
    @mock.patch("glob.glob")
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    # TODO: fix these cases
    def test_allowed_failures_config_to_fix(self, mock_open, mock_glob,
                                            mock_exists):
        """
        Test configurations that should not work and must be fixed.
        """
        mock_exists.return_value = True
        mock_glob.return_value = [
            "/etc/sdwdate/30_default.conf",
            "/etc/sdwdate/40_anon-apps-config.conf",
        ]
        mock_open_readlines = mock_open.return_value.readlines
        mock_open_readlines.return_value = ["MAX_FAILURE_RATIO="]
        self.assertEqual(allowed_failures_config(), "")
        mock_open_readlines.return_value = ["MAX_FAILURE_RATIO=foo"]
        self.assertEqual(allowed_failures_config(), "foo")
        mock_open_readlines.return_value = ["MAX_FAILURE_RATIO_FOO=bar"]
        self.assertEqual(allowed_failures_config(), "bar")
        # Gathering the value returns string instead of float.
        mock_open_readlines.return_value = ["MAX_FAILURE_RATIO_FOO=0.34"]
        result = allowed_failures_config()
        self.assertEqual(result, "0.34")
        self.assertIsInstance(result, str)


    @mock.patch("os.path.exists")
    @mock.patch("glob.glob")
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    def test_allowed_failures_config_set(self, mock_open, mock_glob,
                                         mock_exists):
        """
        Test configuration files that set the ratio
        """
        mock_exists.return_value = True
        mock_glob.return_value = [
            "/etc/sdwdate/30_default.conf",
            "/etc/sdwdate/40_anon-apps-config.conf",
        ]
        mock_open_readlines = mock_open.return_value.readlines
        mock_open_readlines.return_value = [
            "MAX_FAILURE_RATIO=0.6",
            "MAX_FAILURE_RATIO=0.5"
        ]
        # TODO: should return float but returns as string.
        result = allowed_failures_config()
        self.assertEqual(result, "0.5")
        self.assertIsInstance(result, str)


    @mock.patch("os.path.exists")
    @mock.patch("glob.glob")
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    def test_allowed_failures_config_file_access(self, mock_open, mock_glob,
                                                 mock_exists):
        """
        Test configuration files read against the intended ones.
        """
        mock_exists.return_value = True
        mock_glob.return_value = [
            "/etc/sdwdate/30_default.conf",
            "/etc/sdwdate/40_anon-apps-config.conf",
        ]
        mock_open_readlines = mock_open.return_value.readlines
        mock_open_readlines.return_value = []
        allowed_failures_config()
        mock_exists.assert_called_with("/etc/sdwdate.d/")
        mock_glob.assert_called_with("/etc/sdwdate.d/*.conf")


    def test_allowed_failures_calculate(self):
        """
        Test calculation of allowed failures.
        """
        self.assertEqual(allowed_failures_calculate(0.34, 1, 1), 0)
        self.assertEqual(allowed_failures_calculate(0.34, 1, 2), 0)
        self.assertEqual(allowed_failures_calculate(0.34, 1, 3), 1)
        self.assertEqual(allowed_failures_calculate(0.34, 1, 50), 17)
        self.assertEqual(allowed_failures_calculate(0.5, 1, 50), 25)
        self.assertEqual(allowed_failures_calculate(0.5, 10, 50), 2)
        self.assertEqual(allowed_failures_calculate(0.5, 10, 9), 0)
        self.assertEqual(allowed_failures_calculate(0.5, 10, 20), 1)
        self.assertIsInstance(allowed_failures_calculate(0.5, 10, 20), int)


class TestConfigPool(unittest.TestCase):
    """
    Test the functions that uses pool variables separate to initialize a
    distinct setUp().
    """

    def setUp(self):
        self.setup_mock_read_pools()  # pylint: disable=no-value-for-parameter


    @mock.patch("sdwdate.sdwdate.read_pools")
    def setup_mock_read_pools(self, mock_read_pools):
        """
        TODO
        """
        self.mock_read_pools = mock_read_pools
        self.remotes = {
            "black": {"url": "http://black.onion", "comment": "black sun"},
            "gray": {"url": "http://gray.onion", "comment": "gray sun"},
            "magenta": {"url": "http://magenta.onion", "comment": "magenta sun"},
            "blue": {"url": "http://blue.onion", "comment": "blue sun"},
            "green": {"url": "http://green.onion", "comment": "green sun"},
            "yellow": {"url": "http://yellow.onion", "comment": "yellow sun"},
            "orange": {"url": "http://orange.onion", "comment": "orange sun"},
            "red": {"url": "http://red.onion", "comment": "red sun"},
            "white": {"url": "http://white.onion", "comment": "white sun"},
            "purple": {"url": "http://purple.onion", "comment": "purple sun"},
            "pink": {"url": "http://pink.onion", "comment": "pink sun"},
            "cyan": {"url": "http://cyan.onion", "comment": "cyan sun"},
            "teal": {"url": "http://teal.onion", "comment": "teal sun"},
            "lavender": {"url": "http://lavender.onion", "comment": "lavender sun"},
            "maroon": {"url": "http://maroon.onion", "comment": "maroon sun"},
            "navy": {"url": "http://navy.onion", "comment": "navy sun"},
            "olive": {"url": "http://olive.onion", "comment": "olive sun"},
            "turquoise": {"url": "http://turquoise.onion", "comment": "turquoise sun"},
            "gold": {"url": "http://gold.onion", "comment": "gold sun"},
            "silver": {"url": "http://silver.onion", "comment": "silver sun"},
            "indigo": {"url": "http://indigo.onion", "comment": "indigo sun"},
            "violet": {"url": "http://violet.onion", "comment": "violet sun"},
            "crimson": {"url": "http://crimson.onion", "comment": "crimson sun"},
            "azure": {"url": "http://azure.onion", "comment": "azure sun"},
            "beige": {"url": "http://beige.onion", "comment": "beige sun"},
            "coral": {"url": "http://coral.onion", "comment": "coral sun"},
            "khaki": {"url": "http://khaki.onion", "comment": "khaki sun"},
            "mauve": {"url": "http://mauve.onion", "comment": "mauve sun"},
            "ochre": {"url": "http://ochre.onion", "comment": "ochre sun"},
            "periwinkle": {"url": "http://periwinkle.onion", "comment": "periwinkle sun"}
        }

        all_colors = list(self.remotes.keys())
        color_sets = [all_colors[i:i+10] for i in range(0, len(all_colors), 10)]
        self.sort_pool_set = [
            (
                [self.remotes[color]["url"] for color in colors],
                [self.remotes[color]["comment"] for color in colors]
            )
            for colors in color_sets
        ]
        mock_read_pools.side_effect = self.sort_pool_set

        self.pool_zero = [
            f'"{self.remotes[color]["url"]} # {self.remotes[color]["comment"]}"'
            for color in all_colors[0:10]
        ]
        self.pool_zero.insert(5, "[")
        self.pool_zero.append("]")

        self.pool_one = [
            f'"{self.remotes[color]["url"]} # {self.remotes[color]["comment"]}"'
            for color in all_colors[10:20]
        ]
        self.pool_one.insert(1, "[")
        self.pool_one.insert(4, "]")
        self.pool_one.insert(5, "[")
        self.pool_one.append("]")
        self.pool_one.append(")")
        self.pool_one.append("")

        self.pool_two = [
            f'"{self.remotes[color]["url"]} # {self.remotes[color]["comment"]}"'
            for color in all_colors[20:30]
        ]
        self.pool_two.append(")")
        self.pool_two.append("")
        self.pool_two.append("RANDOMIZE_TIME=true")

        self.pools = [
            TimeSourcePool(0),
            TimeSourcePool(1),
            TimeSourcePool(2)
        ]


    def test_get_comment_existent(self):
        """
        Query a URL.
        """
        color = list(self.remotes.keys())[0]
        self.assertEqual(get_comment(self.pools, self.remotes[color]["url"]),
                         self.remotes["black"]["comment"])


    def test_get_comment_from_second_pool(self):
        """
        Query URL from second pool.
        """
        color = list(self.remotes.keys())[15]
        self.assertEqual(get_comment(self.pools, self.remotes[color]["url"]),
                         self.remotes[color]["comment"])


    def test_get_comment_non_registered_url(self):
        """
        Query URL that is not registered.
        """
        remote = "http://url-not-registered.com"
        self.assertEqual(get_comment(self.pools, remote), "unknown-comment")


    def test_get_comment_empty_pools(self):
        """
        Query URL from empty pool.
        """
        color = list(self.remotes.keys())[0]
        self.assertEqual(get_comment([], self.remotes[color]["url"]),
                         "unknown-comment")


    def test_get_comment_pool_single(self):
        """
        Query URL from a single pool.
        """
        color = list(self.remotes.keys())[25]
        remote = self.remotes[color]["url"]
        comment = self.remotes[color]["comment"]
        self.assertEqual(get_comment_pool_single(self.pools[2], remote),
                         comment)
        self.assertNotEqual(get_comment_pool_single(self.pools[1], remote),
                            comment)


    def test_get_comment_pool_single_non_registered_url(self):
        """
        Query non registered URL from a single pool.
        """
        remote = "http://url-not-registered.com"
        self.assertEqual(get_comment_pool_single(self.pools[2], remote),
                         "unknown-comment")


    def test_get_comment_pool_single_empty_pool(self):
        """
        Query URL from empty pool.
        """
        color = list(self.remotes.keys())[0]
        remote = self.remotes[color]["url"]
        self.assertEqual(get_comment([], remote), "unknown-comment")


    def test_sort_pool(self):
        """
        Test pool sorting using different modes.
        Mode:
          test: must produce identical results as side effect.
          production: must produce random output if pool contains [URL groups].
        """
        pools = [self.pool_zero, self.pool_one, self.pool_two]
        for i, pool in enumerate(pools):
            result_test = sort_pool(pool, "test")
            self.assertIsInstance(result_test, tuple)
            self.assertEqual(result_test, self.sort_pool_set[i])
            if "[" not in pool:
                continue
            max_tries = 100
            first_sample = None
            for _ in range(max_tries):
                current_sample = sort_pool(pool, "production")
                result_production = sort_pool(pool, "production")
                self.assertIsInstance(result_production, tuple)
                ## TODO: testing assertEqual() with the production mode is more
                ## difficult as it has to iterate over all possibilities to find
                ## a matching one.
                #self.assertEqual(result_production, self.sort_pool_set[i])
                if first_sample is None:
                    first_sample = current_sample
                elif current_sample != first_sample:
                    break
            else:
                raise AssertionError(f"Pool {i} did not produce a random sample")


    def test_sort_pool_wrong_format(self):
        """
        Test sorting pools that have the wrong format.
        """
        self.assertEqual(sort_pool([], "test"), ([], []))
        self.assertEqual(sort_pool(['a # b'], "test"), ([], []))
        self.assertEqual(sort_pool(["a # b"], "test"), ([], []))
        self.assertEqual(sort_pool(['"a # b'], "test"), (["a"], []))
        self.assertEqual(sort_pool(['"a # b"'], "test"), (["a"], ["b"]))
        self.assertEqual(sort_pool(["'a # b'"], "test"), ([], []))
        self.assertEqual(sort_pool(['"a"'], "test"), ([], []))
        self.assertEqual(sort_pool(['"a"'], "test"), ([], []))
        self.assertEqual(sort_pool(['"a "'], "test"), ([], []))
        self.assertEqual(sort_pool(['"a #"'], "test"), (["a"], [""]))
        self.assertEqual(sort_pool(['"a # "'], "test"), (["a"], [""]))
        self.assertEqual(sort_pool(['"a # b"'], "test"), (["a"], ["b"]))
        self.assertEqual(sort_pool(['"a #  b"'], "test"), (["a"], ["b"]))
        self.assertEqual(sort_pool(['"a ## b"'], "test"), (["a #"], ["# b"]))
        self.assertEqual(sort_pool(['"# #"'], "test"), (["#"], ["#"]))


    @mock.patch("os.path.exists")
    @mock.patch("glob.glob")
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    def test_read_pools(self, mock_open, mock_glob, mock_exists):
        """
        Test configurations that returns true.
        """
        # TODO: test missing directory, missing configuration.
        mock_exists.return_value = True
        mock_glob.return_value = [
            "/etc/sdwdate/30_default.conf"
        ]
        pools = [self.pool_zero, self.pool_one, self.pool_two]
        mock_open_readlines = mock_open.return_value.readlines
        mock_open_readlines.return_value = [
            "SDWDATE_POOL_ZERO=(",
            *pools[0],
            "SDWDATE_POOL_ONE=(",
            *pools[1],
            "SDWDATE_POOL_TWO=(",
            *pools[2],
        ]

        for i in range(len(pools)):
            result_test = read_pools(i, "test")
            self.assertIsInstance(result_test, tuple)
            self.assertEqual(result_test, self.sort_pool_set[i])


if __name__ == "__main__":
    unittest.main()
