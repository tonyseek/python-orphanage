from __future__ import absolute_import

import os
from pkg_resources import resource_string

from cffi import FFI


DEBUG = '--coverage' in os.environ.get('CFLAGS', '').split()


def ensure_string(text):
    if isinstance(text, bytes):
        return text.decode('utf-8')
    return text


def yield_macros():
    if DEBUG:
        yield ('DEBUG', '')


ffibuilder = FFI()
ffibuilder.set_source(
    '_orphanage_poll',
    ensure_string(resource_string('orphanage', 'poll.c')),
    libraries=['pthread'],
    define_macros=list(yield_macros()),
)
ffibuilder.cdef(
    ensure_string(resource_string('orphanage', 'poll.h')),
)

if DEBUG:
    ffibuilder.cdef('void __gcov_flush(void);')


if __name__ == '__main__':  # pragma: no cover
    ffibuilder.compile(verbose=True, debug=DEBUG)
