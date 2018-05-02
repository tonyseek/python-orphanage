from __future__ import absolute_import

import sys
import logging


__version__ = '0.0.0'
__all__ = ['exit_when_orphaned']


_logger = logging.getLogger(__name__)
_suicide_ctx = None


def exit_when_orphaned(exit_func=sys.exit, exit_args=()):
    """Let the current process exit when it was orphaned.

    By default, the :func:`sys.exit` will be used to terminate the process.

    :param exit_func: The function which will terminate current process.
    :param exit_args: The arguments of the ``exit_func``.
    """
    from orphanage.poll import Context

    def terminate(ctx):
        try:
            ctx.stop()
            ctx.close()
        except Exception:
            _logger.exception('Closing context of orphanage')
        exit_func(*exit_args)

    global _suicide_ctx
    _suicide_ctx = Context([terminate])
    _suicide_ctx.start()
