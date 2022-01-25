# -*- coding: utf-8 -*-
#!/usr/bin/env python3
#
# Copyright (C) 2019 Intel Corporation.  All rights reserved.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
#
import ctypes
from wamr.ffi import *


def hello_callback(args, results):
    print("Calling back...")
    print("> Hello World!")
    return 0


def wasm_functype_new_0_0():
    params = wasm_valtype_vec_t()
    results = wasm_valtype_vec_t()

    wasm_valtype_vec_new_empty(byref(params))
    wasm_valtype_vec_new_empty(byref(results))
    return wasm_functype_new(byref(params), byref(results))


def main():
    print("Initializing...")
    engine = wasm_engine_new()
    store = wasm_store_new(engine)

    print("Loading binary...")
    with open("hello.wasm", "rb") as f:
        wasm = f.read()
        binary = wasm_byte_vec_t()
        wasm_byte_vec_new_uninitialized(byref(binary), len(wasm))
        # underlying buffer is not writable
        binary.data = (ctypes.c_ubyte * len(wasm)).from_buffer_copy(wasm)

    print("Compiling module...")
    module = wasm_module_new(store, byref(binary))
    binary.data = None
    wasm_byte_vec_delete(byref(binary))

    print("Creating callback...")
    hello_type = wasm_functype_new_0_0()
    hello_func = wasm_func_new(store, hello_type, wasm_func_callback_t(hello_callback))

    wasm_functype_delete(hello_type)

    print("Instantiating module...")

    imports = wasm_extern_vec_t()
    wasm_extern_vec_new(byref(imports), 1, wasm_func_as_extern(hello_func))
    instance = wasm_instance_new(store, module, imports, None)

    wasm_func_delete(hello_func)

    print("Extracting export...")
    exports = wasm_extern_vec_t()
    wasm_instance_exports(instance, exports)

    run_func = wasm_extern_as_func(exports.data[0])

    wasm_instance_delete(instance)
    wasm_module_delete(module)

    print("Calling export...")
    args = wasm_val_vec_t()
    results = wasm_val_vec_t()

    wasm_val_vec_new_empty(byref(args))
    wasm_val_vec_new_empty(byref(results))

    wasm_func_call(run_func, byref(args), byref(results))

    print("Shutting down...")
    wasm_store_delete(store)
    wasm_engine_delete(engine)

    print("Done.")


if __name__ == "__main__":
    main()
