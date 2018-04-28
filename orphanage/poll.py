from __future__ import absolute_import

from _orphanage_poll import ffi, lib


class Context(object):
    def __init__(self):
        self.ptr = lib.orphanage_poll_create()
        if self.ptr == ffi.NULL:
            raise RuntimeError('out of memory')

    def close(self):
        lib.orphanage_poll_close(self.ptr)
        self.ptr = None

    def _started(self):
        if self.ptr:
            return
        raise RuntimeError('context has been closed')

    def start(self):
        self._started()
        return lib.orphanage_poll_start(self.ptr)

    def stop(self):
        self._started()
        return lib.orphanage_poll_stop(self.ptr)
