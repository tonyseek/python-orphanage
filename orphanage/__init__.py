from __future__ import absolute_import

import os


__version__ = '0.1.0'
__all__ = ['exit_when_orphaned']


_suicide_ctx = None
_suicide_pid = None


def exit_when_orphaned():
    """Let the current process exit when it was orphaned.

    Calling multiple times and calling-and-forking are both safe. But this is
    not a thread safe function. Never call it concurrently.
    """
    from orphanage.poll import Context

    global _suicide_ctx, _suicide_pid
    if _suicide_ctx is not None:
        if _suicide_pid == os.getpid():
            return
        else:
            _suicide_ctx.stop()
            _suicide_ctx.close()
    _suicide_pid = os.getpid()
    _suicide_ctx = Context(suicide_instead=True)
    _suicide_ctx.start()
