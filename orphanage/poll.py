from __future__ import absolute_import

from errno import errorcode
from weakref import WeakValueDictionary

from _orphanage_poll import ffi, lib


# Copied from "poll.c" only
ORPHANAGE_POLL_OK = 0x00000000
ORPHANAGE_POLL_PT_CREATE_ERROR = 0x00000001
ORPHANAGE_POLL_PT_DETACH_ERROR = 0x00000002
ORPHANAGE_POLL_PT_CANCEL_ERROR = 0x00000003


callback_registry = WeakValueDictionary()


@ffi.def_extern()
def orphanage_poll_routine_callback(ptr):
    ctx = callback_registry.get(ptr)
    if ctx is None:
        return 1
    ctx.trigger_callbacks()
    return 0


def perror(description):
    errno = ffi.errno
    errname = errorcode.get(errno, str(errno))
    return RuntimeError('{0}: errno = {1}'.format(description, errname))


def raise_for_return_value(return_value):
    if return_value == ORPHANAGE_POLL_OK:
        return
    elif return_value == ORPHANAGE_POLL_PT_CREATE_ERROR:
        raise perror('pthread_create')
    elif return_value == ORPHANAGE_POLL_PT_DETACH_ERROR:
        raise perror('pthread_detach')
    elif return_value == ORPHANAGE_POLL_PT_CANCEL_ERROR:
        raise perror('pthread_cancel')
    else:
        raise perror('unknown')


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
        r = lib.orphanage_poll_start(self.ptr)
        raise_for_return_value(r)

    def stop(self):
        self._started()
        r = lib.orphanage_poll_stop(self.ptr)
        raise_for_return_value(r)

    def trigger_callbacks(self):
        for callback in self.callbacks:
            callback(self)
