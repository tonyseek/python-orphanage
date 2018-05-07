from __future__ import absolute_import

from pytest import fixture

from orphanage.poll import lib


@fixture(autouse=True)
def gcov_flush():
    try:
        yield lib.__gcov_flush
    finally:
        lib.__gcov_flush()
