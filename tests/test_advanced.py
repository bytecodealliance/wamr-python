# -*- coding: utf-8 -*-
#!/usr/bin/env python3
#
# Copyright (C) 2019 Intel Corporation.  All rights reserved.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
#

from .context import wamr

import unittest


class AdvancedTestSuite(unittest.TestCase):
    """Advanced test cases."""

    def test_thoughts(self):
        assert True


if __name__ == "__main__":
    unittest.main()
