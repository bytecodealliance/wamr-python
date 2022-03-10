# -*- coding: utf-8 -*-
#!/usr/bin/env python3
#
# Copyright (C) 2019 Intel Corporation.  All rights reserved.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
#
"""
- Need to run *download_wamr.py* firstly.
- Parse *./wasm-micro-runtime/core/iwasm/include/wasm_c_api.h* and generate
  *wamr/binding.py*
"""
import pycparser


class Visitor(pycparser.c_ast.NodeVisitor):
    def visit_Struct(self, node):
        pass

    def visit_Union(self, node):
        pass

    def visit_TypeDef(self, node):
        pass

    def visit_FuncDecl(self, node):
        pass


def main():
    ast = pycparser.parse_file(...)
    v = Visitor()
    v.visit(ast)


if __name__ == "__main__":
    main()
