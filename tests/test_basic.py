# -*- coding: utf-8 -*-

from .context import wamr

import unittest


class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_wasm_engine_new_success(self):
        self.assertTrue(False)

    def test_wasm_engine_new_failure(self):
        self.assertTrue(False)


if __name__ == "__main__":
    unittest.main()
