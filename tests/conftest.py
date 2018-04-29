from __future__ import absolute_import

from pytest import fixture
from cffi import FFI


@fixture(autouse=True)
def gcov():
    ffi = FFI()
    ffi.cdef('void __gcov_flush();')
    lib = ffi.dlopen(None)
    yield ffi, lib
    lib.__gcov_flush()
