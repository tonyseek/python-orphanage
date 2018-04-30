from __future__ import absolute_import

import os
import signal
import time

from pytest import fixture, raises

from orphanage.poll import Context, ffi, lib, orphanage_poll_routine_callback


@fixture(autouse=True)
def gcov_flush():
    try:
        yield lib.__gcov_flush
    finally:
        lib.__gcov_flush()


def test_allocation():
    ctx = Context()
    assert ctx.ptr is not None
    assert ctx.ptr != ffi.NULL

    ctx.close()
    assert ctx.ptr is None


def test_allocation_memory_error(mocker):
    lib = mocker.patch('orphanage.poll.lib', autospec=True)
    lib.orphanage_poll_create.return_value = ffi.NULL
    with raises(RuntimeError) as error:
        Context()
    error.match('out of memory')


def test_polling_smoke():
    ctx = Context()
    assert ctx.start() == 0
    assert ctx.stop() == 0


def test_polling_closing_error():
    ctx = Context()
    ctx.close()

    with raises(RuntimeError) as error:
        ctx.start()
    error.match('has been closed')

    with raises(RuntimeError) as error:
        ctx.stop()
    error.match('has been closed')


def test_polling_callback_registry(mocker):
    stub = mocker.stub()
    stub2 = mocker.stub()
    ctx = Context([stub])
    ctx2 = Context([stub2])
    assert ctx.ptr != ctx2.ptr
    orphanage_poll_routine_callback(ctx.ptr)
    stub.assert_called_once_with(ctx)
    stub2.assert_not_called()


def test_polling_callback_registry_fault_tolerance(mocker):
    stub = mocker.stub()
    ctx = Context([stub])
    assert ctx.ptr != ffi.NULL
    orphanage_poll_routine_callback(ffi.NULL)
    stub.assert_not_called()


def test_polling_callback_unexploded(mocker):
    stub = mocker.stub()
    ctx = Context([stub])
    assert ctx.start() == 0
    stub.assert_not_called()
    assert ctx.stop() == 0


def test_polling_callback_exploded(gcov_flush):
    pipe_r, pipe_w = os.pipe()
    child_pid = os.fork()

    if child_pid == 0:
        # child process
        os.setsid()
        grandchild_pid = os.fork()
        if grandchild_pid == 0:
            # grandchild process
            os.close(pipe_r)
            ctx = Context([
                lambda ctx: os.write(pipe_w, b'called'),
                lambda ctx: gcov_flush(),
                lambda ctx: os.close(pipe_w),  # EOF to end the test
            ])
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
            os.kill(child_pid, signal.SIGTERM)
            os.waitpid(child_pid, 0)
            assert os.read(pipe_r, 1024) == b'called'
            assert os.read(pipe_r, 1024) == b''  # EOF
        finally:
            try:
                os.killpg(child_pid, signal.SIGTERM)
                os.waitpid(child_pid, 0)
            except OSError:
                pass
