# -*- coding: utf-8 -*-
#!/usr/bin/env python3
#
# Copyright (C) 2019 Intel Corporation.  All rights reserved.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
#
import ctypes
import os
from pathlib import Path
import sys

# how to open the library file of WAMR

if sys.platform == "linux":
    building_dir = "product-mini/platforms/linux/build"
    libname = "libiwasm.so"
elif sys.platform == "win32":
    building_dir = "product-mini/platforms/windows/build"
    libname = "iwasm.dll"
elif sys.platform == "darwin":
    building_dir = "product-mini/platforms/darwin/build"
    libname = "libiwasm.dylib"
else:
    raise RuntimeError(f"unsupported platform `{sys.platform}`")

current_file = Path(__file__)
if current_file.is_symlink():
    current_file = Path(os.readlink(current_file))
current_dir = current_file.parent.resolve()
root_dir = current_dir.joinpath("..").resolve()
wamr_dir = root_dir.joinpath("wasm-micro-runtime").resolve()
if not wamr_dir.exists():
    raise RuntimeError(f"not found the repo of wasm-micro-runtime under {root_dir}")

libpath = wamr_dir.joinpath(building_dir).joinpath(libname).resolve()
if not libpath.exists():
    raise RuntimeError(f"not found precompiled wamr library at {libpath}")

libiwasm = ctypes.cdll.LoadLibrary(libpath)


class wasm_ref_t(ctypes.Structure):
    pass


class wasm_val_union(ctypes.Union):
    _fields_ = [
        ("i32", ctypes.c_int32),
        ("i64", ctypes.c_int64),
        ("f32", ctypes.c_float),
        ("f64", ctypes.c_double),
        ("ref", ctypes.POINTER(wasm_ref_t)),
    ]


class wasm_val_t(ctypes.Structure):
    _fields_ = [
        ("kind", ctypes.c_uint8),
        ("of", wasm_val_union),
    ]
