from __future__ import absolute_import

import os
import signal
import time

from pytest import fixture

from orphanage.poll import Context, ffi, lib


@fixture(autouse=True)
def gcov_flush():
    yield
    lib.__gcov_flush()


def test_allocation():
    ctx = Context()
    assert ctx.ptr is not None
    assert ctx.ptr != ffi.NULL

    ctx.close()
    assert ctx.ptr is None


def test_polling_smoke():
    ctx = Context()
    assert ctx.start() == 0
    assert ctx.stop() == 0


def test_polling_callback_unexploded(mocker):
    stub = mocker.stub()
    ctx = Context([stub])
    assert ctx.start() == 0
    stub.assert_not_called()
    assert ctx.stop() == 0


def test_polling_callback_exploded():
    pipe_r, pipe_w = os.pipe()
    child_pid = os.fork()

    if child_pid == 0:
        # child process
        os.setsid()
        grandchild_pid = os.fork()
        if grandchild_pid == 0:
            # grandchild process
            os.close(pipe_r)
            ctx = Context([lambda ctx: os.write(pipe_w, b'called')])
            assert ctx.start() == 0
            os.write(pipe_w, b'did_not_call_yet')
            signal.pause()
        else:
            # still child process
            os.close(pipe_r)
            os.close(pipe_w)
            signal.pause()
    else:
        # main process
        try:
            os.close(pipe_w)
            assert os.read(pipe_r, 1024) == b'did_not_call_yet'

            time.sleep(1)  # suspend for waiting the pthread
            os.kill(child_pid, signal.SIGQUIT)
            os.waitpid(child_pid, 0)
            assert os.read(pipe_r, 1024) == b'called'
        finally:
            try:
                os.killpg(child_pid, signal.SIGQUIT)
                os.waitpid(child_pid, 0)
            except OSError:
                pass
