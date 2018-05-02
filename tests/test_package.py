from __future__ import absolute_import

import os
import signal
import select

from pkg_resources import get_distribution

from orphanage import __version__ as orphanage_version, exit_when_orphaned


def test_distribution():
    distribution = get_distribution('orphanage')
    assert distribution.version == orphanage_version


def test_suicide():
    pipe_r, pipe_w = os.pipe()
    spawner_pid = os.fork()
    if spawner_pid == 0:
        # spawner process
        os.setsid()
        spawnee_pid = os.fork()
        if spawnee_pid == 0:
            # spawnee process
            os.close(pipe_r)
            exit_when_orphaned()
            os.write(pipe_w, b'ready')
            signal.pause()
        else:
            # still spawner process
            os.close(pipe_r)
            os.close(pipe_w)
            signal.pause()
    else:
        # main process
        try:
            os.close(pipe_w)

            assert os.read(pipe_r, 5) == b'ready'
            assert select.select([pipe_r], [], [], 1)[0] == []

            os.kill(spawner_pid, signal.SIGTERM)
            os.waitpid(spawner_pid, 0)
            assert os.read(pipe_r, 6) == b''  # EOF: spawnee is dead
        finally:
            try:
                os.killpg(spawner_pid, signal.SIGTERM)
                os.waitpid(spawner_pid, 0)
            except OSError:
                pass
