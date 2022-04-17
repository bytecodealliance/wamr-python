# -*- coding: utf-8 -*-
#!/usr/bin/env python3
#
# Copyright (C) 2019 Intel Corporation.  All rights reserved.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
#
import ctypes
from .binding import *


def dereference(p):
    """
    fetch the conents of a pointer
    """
    if not isinstance(p, ctypes._Pointer):
        raise RuntimeError("not a pointer")
    return p.contents


def create_null_pointer(struct_type):
    return ctypes.POINTER(struct_type)()


def wasm_vec_to_list(vec):
    """
    Converts a vector or a POINTER(vector) to a list
    vector of type pointers -> list of type pointers
    """
    known_vec_type = [wasm_valtype_vec_t, wasm_byte_vec_t]
    known_vec_pointer_type = [POINTER(type) for type in known_vec_type]

    if any([isinstance(vec, type) for type in known_vec_pointer_type]):
        vec = dereference(vec)
        return [vec.data[i] for i in range(vec.num_elems)]
    elif any([isinstance(vec, type) for type in known_vec_type]):
        return [vec.data[i] for i in range(vec.num_elems)]
    else:
        raise RuntimeError("not a known vector type")


# Built-in functions for Structure
def __repr_wasm_limits_t(self):
    return f"{self.min:#x} {self.max:#x}"


# overwrite
wasm_limits_t.__repr__ = __repr_wasm_limits_t


def __compare_wasm_valtype_t(self, other):
    if not isinstance(other, wasm_valtype_t):
        return False
    return wasm_valtype_kind(byref(self)) == wasm_valtype_kind(byref(other))


def __repr_wasm_valtype_t(self):
    kind = wasm_valtype_kind(byref(self))
    if WASM_I32 == kind:
        return "i32"
    elif WASM_I64 == kind:
        return "i64"
    elif WASM_F32 == kind:
        return "f32"
    elif WASM_F64 == kind:
        return "f64"
    elif WASM_FUNCREF == kind:
        return "funcref"
    else:
        return "anyref"


wasm_valtype_t.__eq__ = __compare_wasm_valtype_t
wasm_valtype_t.__repr__ = __repr_wasm_valtype_t


def __repr_wasm_valtype_vec_t(self):
    return (
        " ".join([str(dereference(self.data[i])) for i in range(self.size)])
        if self.size
        else "EMPTY"
    )


wasm_valtype_vec_t.__repr__ = __repr_wasm_valtype_vec_t


def __compare_wasm_functype_t(self, other):
    if not isinstance(other, wasm_functype_t):
        return False
    params1 = dereference(wasm_functype_params(byref(self)))
    params2 = dereference(wasm_functype_params(byref(other)))
    results1 = dereference(wasm_functype_results(byref(self)))
    results2 = dereference(wasm_functype_results(byref(other)))
    return params1 == params2 and results1 == results2


def __repr_wasm_functype_t(self):
    params = dereference(wasm_functype_params(byref(self)))
    results = dereference(wasm_functype_results(byref(self)))
    params = f" (params {params})" if params.size else ""
    results = f" (results {results})" if results.size else ""
    return f"(func{params}{results})"


wasm_functype_t.__eq__ = __compare_wasm_functype_t
wasm_functype_t.__repr__ = __repr_wasm_functype_t


def __compare_wasm_globaltype_t(self, other):
    if not isinstance(other, wasm_globaltype_t):
        return False
    content1 = dereference(wasm_globaltype_content(byref(self)))
    content2 = dereference(wasm_globaltype_content(byref(other)))
    mutability1 = wasm_globaltype_mutability(byref(self))
    mutability2 = wasm_globaltype_mutability(byref(other))
    return content1 == content2 and mutability1 == mutability2


def __repr_wasm_globaltype_t(self):
    mutability = f"{wasm_globaltype_mutability(byref(self))}"
    content = f"{dereference(wasm_globaltype_content(byref(self)))}"
    return f"(global{' mut ' if mutability else ' '}{content})"


wasm_globaltype_t.__eq__ = __compare_wasm_globaltype_t
wasm_globaltype_t.__repr__ = __repr_wasm_globaltype_t


def __compare_wasm_tabletype_t(self, other):
    if not isinstance(other, wasm_tabletype_t):
        return False
    element1 = dereference(wasm_tabletype_element(byref(self)))
    element2 = dereference(wasm_tabletype_element(byref(other)))
    limits1 = dereference(wasm_tabletype_limits(byref(self)))
    limits2 = dereference(wasm_tabletype_limits(byref(other)))
    return element1 == element2 and limits1 == limits2


def __repr_wasm_tabletype_t(self):
    element = dereference(wasm_tabletype_element(byref(self)))
    limit = dereference(wasm_tabletype_limits(byref(self)))
    return f"(table {limit} {element})"


wasm_tabletype_t.__eq__ = __compare_wasm_tabletype_t
wasm_tabletype_t.__repr__ = __repr_wasm_tabletype_t


def __compare_wasm_memorytype_t(self, other):
    if not isinstance(other, wasm_memorytype_t):
        return False
    limits1 = dereference(wasm_memorytype_limits(byref(self)))
    limits2 = dereference(wasm_memorytype_limits(byref(other)))
    return limits1 == limits2


def __repr_wasm_memorytype_t(self):
    limit = dereference(wasm_memorytype_limits(byref(self)))
    return f"(memory {limit})"


wasm_memorytype_t.__eq__ = __compare_wasm_memorytype_t
wasm_memorytype_t.__repr__ = __repr_wasm_memorytype_t

# Function Types construction short-hands
def __wasm_functype_new(param_list, result_list):
    def __list_to_wasm_valtype_vec(l):
        vec = wasm_valtype_vec_t()

        if not l:
            wasm_valtype_vec_new_empty(byref(vec))
        else:
            data_type = POINTER(wasm_valtype_t) * len(l)
            data = data_type()
            for i in range(len(l)):
                data[i] = l[i]
            wasm_valtype_vec_new(byref(vec), len(l), data)

        return vec

    params = __list_to_wasm_valtype_vec(param_list)
    results = __list_to_wasm_valtype_vec(result_list)
    return wasm_functype_new(byref(params), byref(results))


def wasm_functype_new_0_0():
    return __wasm_functype_new([], [])


def wasm_functype_new_1_0(p1):
    return __wasm_functype_new([p1], [])


def wasm_functype_new_2_0(p1, p2):
    return __wasm_functype_new([p1, p2], [])


def wasm_functype_new_3_0(p1, p2, p3):
    return __wasm_functype_new([p1, p2, p3], [])


def wasm_functype_new_0_1(r1):
    return __wasm_functype_new([], [r1])


def wasm_functype_new_1_1(p1, r1):
    return __wasm_functype_new([p1], [r1])


def wasm_functype_new_2_1(p1, p2, r1):
    return __wasm_functype_new([p1, p2], [r1])


def wasm_functype_new_3_1(p1, p2, p3, r1):
    return __wasm_functype_new([p1, p2, p3], [r1])
