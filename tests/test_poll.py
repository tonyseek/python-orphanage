from __future__ import absolute_import

from orphanage.poll import Context, ffi


def test_allocation():
    ctx = Context()
    assert ctx.ptr is not None
    assert ctx.ptr != ffi.NULL

    ctx.close()
    assert ctx.ptr is None


def test_not_implemented():
    ctx = Context()
    assert ctx.start() == 0
    assert ctx.stop() == 0
