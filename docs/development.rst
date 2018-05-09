Development Guide
-----------------

There is a ``Makefile`` for development in local environment.
See available commands via invoking ``make help``.

You will need to install pyenv_ and tox_ globally in your local environment::

    brew install pyenv tox
    pyenv install 2.7.14  # and also


Requirement
~~~~~~~~~~~

The requirement changes of testing and document building environment need to be
included in ``requirements-test.in`` and ``docs/requirements.in``. You will
need to invoke ``make deps`` to compile them into ``requirements*.txt``.


Test
~~~~

For running test in all supported Python versions, you will need pyenv_::

    # Enter the multi-version Python environment (2.7, 3.6, pypy2, pypy3)
    pyenv shell 2.7.14:3.6.5:pypy2.7-5.10.0:pypy3.5-5.10.1

    make test

For debugging, you may want to test in a specific Python version, such as 2.7::

    tox -e py27                               # Default pytest options
    tox -e py27 -- -vxs --log-cli-level=DEBUG # Custom pytest options


Package
~~~~~~~

For packaging a new distribution, ``make dist`` will be helpful. It assumes you
are using macOS and the Docker for Mac has been installed and started also. The
binary wheel packages for macOS (with your current ABI) and Linux (with
manylinux API) will be present. Using pyenv_ and bumpversion_ is a good idea::

    # Enter the multi-version Python environment (2.7, 3.6, pypy2, pypy3)
    pyenv shell 2.7.14:3.6.5:pypy2.7-5.10.0:pypy3.5-5.10.1

    bumpversion minor           # Commit and tag a new major/minor/patch release
    make dist                   # Build release packages
    make dist options="-b dev0" # Build pre-release packages


Clean up
~~~~~~~~

You could clean up the workspace with ``make clean``. It removes files which
was ignored in the version control except the ``.tox``.


Debugg C Extension
~~~~~~~~~~~~~~~~~~

Debugging the C extension of Python needs different toolchains and skills. The
``lldb`` or ``gdb`` will be useful in that::

    tox -e py27                  # Run test until it hangs
    vim tests/_orphanage_poll.c  # Inspect the CFFI generated code
    lldb --attach-pid=100001     # Attach to the target process
    lldb> breakpoint set -f _orphanage_poll.c -l 434
    lldb> continue
    lldb> bt all

For unexpected crashing, the coredump will include useful information::

    ulimit -c unlimited         # Turn on coredump in current shell
    tox -e py27                 # Run test until it crashes
    lldb --core /cores/cores.10 # Open the coredump named with its pid
    lldb> bt all                # Print the backtrace


.. _pyenv: https://github.com/pyenv/pyenv
.. _bumpversion: https://github.com/peritus/bumpversion
