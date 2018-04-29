from __future__ import absolute_import

from weakref import WeakValueDictionary

from _orphanage_poll import ffi, lib


callback_registry = WeakValueDictionary()


@ffi.def_extern()
def orphanage_poll_routine_callback(ptr):
    ctx = callback_registry.get(ptr)
    if ctx is None:
        return
    ctx.trigger_callbacks()


class Context(object):
    def __init__(self, callbacks=None):
        self.callbacks = list(callbacks or [])
        self.ptr = lib.orphanage_poll_create()
        if self.ptr == ffi.NULL:
            raise RuntimeError('out of memory')
        callback_registry[self.ptr] = self

    def close(self):
        lib.orphanage_poll_close(self.ptr)
        callback_registry.pop(self.ptr, None)
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

    def trigger_callbacks(self):
        for callback in self.callbacks:
            callback(self)
