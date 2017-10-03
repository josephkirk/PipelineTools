# -*- coding: utf-8 -*-

from ..sample import core as sample

import unittest


class AdvancedTestSuite(unittest.TestCase):
    """Advanced test cases."""

    def test_thoughts(self):
        self.assertIsNone(sample.hmm())


if __name__ == '__main__':
    unittest.main()
