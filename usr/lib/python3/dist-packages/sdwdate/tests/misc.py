#!/usr/bin/env python3
"""
Test the misc module.
"""

import unittest
from sdwdate.misc import strip_html


class TestMisc(unittest.TestCase):
    """
    Test stripping HTML from message.
    """

    def test_html(self):
        """
        Test a simple HTML.
        """
        self.assertEqual(strip_html(
            """
            <h1>Header</h1>
            <p>Paragraph.</p>
                <li>Item 1</li>
                <li>Item 2</li>
                <li>Item 3</li>
            <a href="https://www.example.com">Visit Example.com</a>
            """),
            """
            Header
            Paragraph.
                Item 1
                Item 2
                Item 3
            Visit Example.com
            """)


if __name__ == "__main__":
    unittest.main()
