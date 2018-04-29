from __future__ import absolute_import

from orphanage.poll_build import ffibuilder, ensure_string


def test_compile(tmpdir):
    with tmpdir.as_cwd():
        ffibuilder.compile(verbose=True, debug=True)
        assert tmpdir.join('_orphanage_poll.c').exists()
        assert tmpdir.join('_orphanage_poll.o').exists()


def test_ensure_string():
    assert ensure_string(u'\u6d4b\u8bd5') == u'\u6d4b\u8bd5'
    assert ensure_string(b'\xe6\xb5\x8b\xe8\xaf\x95') == u'\u6d4b\u8bd5'
