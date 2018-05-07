from __future__ import absolute_import

import os
import signal
import time
import contextlib
import errno

from pytest import fixture, raises

from orphanage.poll import (
    Context, ffi, lib, orphanage_poll_routine_callback,
    ORPHANAGE_POLL_OK, ORPHANAGE_POLL_PT_CREATE_ERROR,
    ORPHANAGE_POLL_PT_DETACH_ERROR)


@fixture(autouse=True)
def gcov_flush():
    try:
        yield lib.__gcov_flush
    finally:
        lib.__gcov_flush()


@fixture
def mocked_lib(mocker):
    return mocker.patch('orphanage.poll.lib', autospec=True)


@fixture
def mocked_ffi(mocker):
    return mocker.patch('orphanage.poll.ffi', autospec=True)


def test_allocation():
    ctx = Context()
    assert ctx.ptr is not None
    assert ctx.ptr != ffi.NULL

    ctx.close()
    assert ctx.ptr is None


def test_allocation_memory_error(mocked_lib):
    mocked_lib.orphanage_poll_create.return_value = ffi.NULL
    with raises(RuntimeError) as error:
        Context()
    error.match('out of memory')


def test_polling_smoke():
    with contextlib.closing(Context()) as ctx:
        ctx.start()
        ctx.stop()
    with contextlib.closing(Context()) as ctx:
        ctx.stop()


def test_polling_starting_error(mocked_lib, mocked_ffi):
    mocked_lib.orphanage_poll_start.return_value = ORPHANAGE_POLL_OK
    with contextlib.closing(Context()) as ctx:
        ctx.start()

    mocked_lib.orphanage_poll_start.return_value = \
        ORPHANAGE_POLL_PT_CREATE_ERROR
    mocked_ffi.errno = errno.EPERM
    with raises(RuntimeError) as error, contextlib.closing(Context()) as ctx:
        ctx.start()
    error.match('pthread_create: errno = EPERM')


def test_polling_stopping_error(mocked_lib, mocked_ffi):
    mocked_lib.orphanage_poll_stop.return_value = ORPHANAGE_POLL_OK
    with contextlib.closing(Context()) as ctx:
        ctx.stop()

    mocked_lib.orphanage_poll_stop.return_value = \
        ORPHANAGE_POLL_PT_DETACH_ERROR
    mocked_ffi.errno = -65535
    with raises(RuntimeError) as error, contextlib.closing(Context()) as ctx:
        ctx.stop()
    error.match('pthread_detach: errno = -65535')

    mocked_lib.orphanage_poll_stop.return_value = -1
    mocked_ffi.errno = errno.EINVAL
    with raises(RuntimeError) as error, contextlib.closing(Context()) as ctx:
        ctx.stop()
    error.match('unknown: errno = EINVAL')


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
    with contextlib.closing(Context([stub])) as ctx, \
            contextlib.closing(Context([stub2])) as ctx2:
        assert ctx.ptr != ctx2.ptr
        orphanage_poll_routine_callback(ctx.ptr)
        stub.assert_called_once_with(ctx)
        stub2.assert_not_called()


def test_polling_callback_registry_fault_tolerance(mocker):
    stub = mocker.stub()
    with contextlib.closing(Context([stub])) as ctx:
        assert ctx.ptr != ffi.NULL
        orphanage_poll_routine_callback(ffi.NULL)
        stub.assert_not_called()


def test_polling_callback_unexploded(mocker):
    stub = mocker.stub()
    with contextlib.closing(Context([stub])) as ctx:
        ctx.start()
        stub.assert_not_called()
        ctx.stop()


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
                lambda ctx: ctx.stop(),
                lambda ctx: ctx.close(),
                lambda ctx: os._exit(0),  # EOF to end the test
            ])
            ctx.start()
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
