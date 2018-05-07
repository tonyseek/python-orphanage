orphanage
=========

Let child processes in Python suicide if they became orphans.

Installation
------------

.. code-block:: bash

    pip install orphanage

Don't forget to put it in ``setup.py`` / ``requirements.txt``.


Usage
-----

.. code-block:: python

    from orphanage import exit_when_orphaned

    exit_when_orphaned()


Motivation
----------

Some application server softwares (e.g. Gunicorn_) work on a multiple-process
architect which we call the master-worker model. They must clean up the worker
processes if the master process is stopped, to prevent them from becoming
orphan processes.

In the gevent-integration scene, the worker processes of Gunicorn poll their
``ppid`` in an user thread (a.k.a greenlet) to be orphan-aware. But the user
thread may be hanged once the master process crashed because of the blocked
writing on a pipe, the communicating channel between master process and
worker processes.

We want to perform this ``ppid`` polling in a real kernel thread. That is the
intent of this library.


Principle
---------

This library spawns an internal thread to poll the ``ppid`` at regular
intervals (for now it is one second). Once the ``ppid`` changed, the original
parent process should be dead and the current process should be orphaned. The
internal thread will send ``SIGTERM`` to the current process.

In the plan, the ``prctl`` & ``SIGHUP`` pattern may be introduced in Linux
platforms to avoid from creating threads. For now, the only supported strategy
is the ``ppid`` polling, for being portable.


Alternatives
------------

CaoE_ is an alternative to this library which developed by the Douban Inc. It
uses ``prctl`` and a twice-forking pattern. It has a pure Python implementation
without any C extension compiling requirement. If you don't mind to twist the
process tree, that will be a good choice too.


Contributing
------------

If you want to report bugs or request features, please feel free to open
issues on GitHub_.

Of course, pull requests are always welcome.

.. _Gunicorn: https://github.com/benoitc/gunicorn
.. _CaoE: https://github.com/douban/CaoE
.. _GitHub: https://github.com/tonyseek/python-orphanage/issues
