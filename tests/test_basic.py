# -*- coding: utf-8 -*-
#!/usr/bin/env python3
#
# Copyright (C) 2019 Intel Corporation.  All rights reserved.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
#

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
