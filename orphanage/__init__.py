from __future__ import absolute_import


__version__ = '0.0.0'
__all__ = ['exit_when_orphaned']


_suicide_ctx = None


def exit_when_orphaned():
    """Let the current process exit when it was orphaned."""
    from orphanage.poll import Context

    global _suicide_ctx
    if _suicide_ctx is not None:
        return
    _suicide_ctx = Context(suicide_instead=True)
    _suicide_ctx.start()
