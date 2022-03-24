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
import os
import pathlib
import pycparser
import shutil
import sys

WASM_C_API_HEADER = "core/iwasm/include/wasm_c_api.h"
BINDING_PY = "wamr/binding.py"
# 4 spaces as default indent
INDENT = "    "


class Visitor(pycparser.c_ast.NodeVisitor):
    def __init__(self):
        self.type_map = {
            "byte_t": "ctypes.c_ubyte",
            "size_t": "ctypes.c_size_t",
            "uint32_t": "ctypes.c_uint32",
            "uint8_t": "ctypes.c_uint8",
        }
        self.ret = (
            "# -*- coding: utf-8 -*-\n"
            "#!/usr/bin/env python3\n"
            "#\n"
            "# Copyright (C) 2019 Intel Corporation.  All rights reserved.\n"
            "# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception\n"
            "#\n"
            "# DO NOT EDIT IT. IT IS CREATED BY A SCRIPT\n"
            "#\n"
            "import ctypes\n"
            "\n"
        )
        # WORKAROUNDS:
        # predefined types
        self.ret += (
            "class _OF(ctypes.Union):\n"
            "  _fields_ = [\n"
            '    ("i32", ctypes.c_int32),\n'
            '    ("i64", ctypes.c_int64),\n'
            '    ("f32", ctypes.c_float),\n'
            '    ("f64", ctypes.c_double),\n'
            "  ]\n"
            "\n"
            "class wasm_val_t(ctypes.Structure):\n"
            '  _anonymous_ = ("of",)\n'
            "  _fields_ = [\n"
            '    ("kind", ctypes.c_uint8)\n'
            '    ("of", _OF)\n'
            "  ]\n"
            "\n"
        )

    def get_type_name(self, type):
        if isinstance(type, pycparser.c_ast.TypeDecl):
            type = type.type
        elif isinstance(type, pycparser.c_ast.PtrDecl):
            return f"ctypes.POINTER({self.get_type_name(type.type)})"
        elif isinstance(type, pycparser.c_ast.FuncDecl):
            print(type)
        else:
            raise Exception(f"unexpected type: {type}")

        if isinstance(type, pycparser.c_ast.IdentifierType):
            if len(type.names) > 1:
                raise Exception(f"unexpected type with a long names: {type}")

            type = type.names[0]

            if type.startswith("wasm_"):
                return type

            if not type in self.type_map.keys():
                raise Exception(f"a new type should be in type_map: {type}")

            return self.type_map.get(type)
        elif isinstance(type, pycparser.c_ast.Union):
            if not type.name:
                raise Exception(f"found an anonymous union {type}")

            return type.name
        elif isinstance(type, pycparser.c_ast.Struct):
            if not type.name:
                raise Exception(f"found an anonymous union {type}")

            return type.name
        else:
            return "unknown"

    def visit_Struct(self, node):
        def gen_fields(info, indent):
            content = ""
            for k, v in info.items():
                content += f'{indent}("{k}", {v}),\n'
            return content[:-1]

        def gen_equal(info, indent):
            content = f"{indent}return "
            for k, v in info.items():
                # not compare pointer value in __eq__
                if v.startswith("ctypes.POINTER"):
                    continue

                content += f" self.{k} == other.{k} and"
            return content[:-4]

        if not node.name or node.name in ["__locale_struct", "wasm_val_t"]:
            return

        name = node.name
        info = {}
        if node.decls:
            for decl in node.decls:
                info[decl.name] = self.get_type_name(decl.type)

        print(f"Struct: {name}, {info}")

        if info:
            self.ret += (
                f"class {name}(ctypes.Structure):\n"
                f"{INDENT}__field__ = [\n"
                f"{gen_fields(info, INDENT*2)}\n"
                f"{INDENT}]\n"
                f"\n"
                f"{INDENT}def __eq__(self, other):\n"
                f"{INDENT*2}if not isinstance(other, {name}):\n"
                f"{INDENT*3}return False\n"
                f"{gen_equal(info, INDENT*2)}\n"
            )
        else:
            self.ret += f"class {name}(ctypes.Structure):\n{INDENT}pass\n"

        self.ret += "\n"

    def visit_Union(self, node):
        print(f"Union: {node.name}")

    def visit_Typedef(self, node):
        # system defined
        if not node.name or not node.name.startswith("wasm_"):
            return

        self.visit(node.type)

        if node.name == self.get_type_name(node.type):
            return
        else:
            self.ret += f"{node.name} = {self.get_type_name(node.type)}\n"
            self.ret += "\n"

    def visit_FuncDecl(self, node):
        # print(f"FuncDecl: {node.type}")
        pass


def preflight_check(workspace):
    wamr_repo = workspace.joinpath("wasm-micro-runtime")
    file_check_list = [
        wamr_repo.exists(),
        wamr_repo.joinpath(WASM_C_API_HEADER).exists(),
    ]

    if not all(file_check_list):
        print(
            "please run utils/download_wamr.py to download the repo, or re-download the repo"
        )
        return False

    if not shutil.which("gcc"):
        print("please install gcc")
        return False

    return True


def do_parse(workspace):
    filename = workspace.joinpath(WASM_C_API_HEADER)
    filename = str(filename)

    ast = pycparser.parse_file(
        filename,
        use_cpp=True,
        cpp_path="gcc",
        cpp_args=[
            "-E",
            "-D__attribute__(x)=",
            "-D__asm__(x)=",
            "-D__asm(x)=",
            "-D__builtin_va_list=int",
            "-D__extension__=",
            "-D__inline__=",
            "-D__restrict=",
            "-D__restrict__=",
            "-D_Static_assert(x, y)=",
            "-D__signed=",
            "-D__volatile__(x)=",
            "-Dstatic_assert(x, y)=",
        ],
    )

    v = Visitor()
    v.visit(ast)
    return v.ret


def main():
    current_file = pathlib.Path(__file__)
    if current_file.is_symlink():
        current_file = pathlib.Path(os.readlink(current_file))

    current_dir = current_file.parent.resolve()
    root_dir = current_dir.joinpath("..").resolve()

    if not preflight_check(root_dir):
        return False

    wamr_repo = root_dir.joinpath("wasm-micro-runtime")
    binding_py = root_dir.joinpath(BINDING_PY)
    with open(binding_py, "w") as f:
        f.write(do_parse(wamr_repo))

    return True


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
