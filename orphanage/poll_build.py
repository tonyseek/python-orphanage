from __future__ import absolute_import

import os
from pkg_resources import resource_string

from cffi import FFI


def ensure_string(text):
    if isinstance(text, bytes):
        return text.decode('utf-8')
    return text


ffibuilder = FFI()
ffibuilder.set_source(
    '_orphanage_poll',
    ensure_string(resource_string('orphanage', 'poll.c')),
    libraries=['pthread'],
)
ffibuilder.cdef(
    ensure_string(resource_string('orphanage', 'poll.h')),
)

if '--coverage' in os.environ.get('CFLAGS', '').split():
    ffibuilder.cdef('void __gcov_flush(void);')


if __name__ == '__main__':
    ffibuilder.compile(verbose=True)
