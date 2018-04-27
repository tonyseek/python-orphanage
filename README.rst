orphanage
=========

Let child processes in Python suicide if they became orphans.

Installation
------------

.. code-block:: bash

    pip install orphanage

Don't forget to put it in ``setup.py`` / ``requirements.txt``.

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

Contributing
------------

If you want to report bugs or request features, please feel free to open
issues on GitHub_.

Of course, pull requests are always welcome.

.. _Gunicorn: https://github.com/benoitc/gunicorn
.. _GitHub: https://github.com/tonyseek/python-orphanage/issues
