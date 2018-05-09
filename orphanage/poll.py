from __future__ import absolute_import

from logging import getLogger
from errno import errorcode
from weakref import WeakValueDictionary

from _orphanage_poll import ffi, lib


# Copied from "poll.c" only
ORPHANAGE_POLL_OK = 0x00000000
ORPHANAGE_POLL_PT_CREATE_ERROR = 0x00000001
ORPHANAGE_POLL_PT_DETACH_ERROR = 0x00000002
ORPHANAGE_POLL_PT_CANCEL_ERROR = 0x00000003


logger = getLogger(__name__)
callback_registry = WeakValueDictionary()


@ffi.def_extern()
def orphanage_poll_routine_callback(ptr):
    """The external callback function of CFFI.

    This function invokes the :meth:`Context.trigger_callbacks` method.

    :param ptr: The C pointer of context.
    :returns: ``0`` for nonerror calls.
    """
    ctx = callback_registry.get(ptr)
    if ctx is None:
        logger.debug('Context of %r is not found', ptr)
        return 1
    logger.debug('Prepare to trigger callbacks on %r', ctx)
    ctx.trigger_callbacks()
    logger.debug('Finished to trigger callbacks on %r', ctx)
    return 0


def perror(description):
    """Raises a runtime error from the specified description and ``errno``."""
    errno = ffi.errno
    errname = errorcode.get(errno, str(errno))
    return RuntimeError('{0}: errno = {1}'.format(description, errname))


def raise_for_return_value(return_value):
    """Checks the return value from C area.

    A runtime error will be raised if the return value is nonzero.
    """
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
    """The context of orphans polling which acts as the CFFI wrapper.

    .. caution:: It is dangerous to use this class directly except you are
                 familiar with the implementation of CPython and you know what
                 you are doing clearly. It is recommended to use the
                 :ref:`public_api` instead, for most users.

    The context must be closed via :meth:`~Context.close` or the memory will
    be leaked.

    :param callbacks: Optional. The list of callback functions. A callback
                      function will be passed one parameter, the instance of
                      this context. Be careful, never invoking any Python
                      built-in and C/C++ extended functions which use the
                      ``Py_BEGIN_ALLOW_THREADS``, such as ``os.close`` and all
                      methods on this context, to avoid from deadlock and other
                      undefined behaviors.
    """

    def __init__(self, callbacks=None, suicide_instead=False):
        self.callbacks = list(callbacks or [])
        self.suicide_instead = suicide_instead
        self.ptr = lib.orphanage_poll_create(int(suicide_instead))
        if self.ptr == ffi.NULL:
            raise RuntimeError('out of memory')
        callback_registry[self.ptr] = self

    def close(self):
        """Closes this context and release the memory from C area."""
        lib.orphanage_poll_close(self.ptr)
        callback_registry.pop(self.ptr, None)
        self.ptr = None

    def _started(self):
        if self.ptr:
            return
        raise RuntimeError('context has been closed')

    def start(self):
        """Starts the polling thread."""
        self._started()
        r = lib.orphanage_poll_start(self.ptr)
        raise_for_return_value(r)

    def stop(self):
        """Stops the polling thread.

        Don't forget to release allocated memory by calling
        :meth:`~Context.close` if you won't use it anymore.
        """
        self._started()
        r = lib.orphanage_poll_stop(self.ptr)
        raise_for_return_value(r)

    def trigger_callbacks(self):
        """Triggers the callback functions.

        This method is expected to be called from C area.
        """
        for callback in self.callbacks:
            logger.debug('triggering callback %r on %r', callback, self)
            try:
                callback(self)
            except Exception:
                logger.exception('triggering callback')
            else:
                logger.debug('triggered callback %r on %r', callback, self)
