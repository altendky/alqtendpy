import pytest
import quamash

import alqtendpy.tests.utils
import alqtendpy.asyncio


@pytest.yield_fixture()
def event_loop(qapp):
    loop = quamash.QEventLoop(qapp)
    yield loop
    loop.close()


@pytest.mark.asyncio
async def test_await_for_signal(qapp):
    timer = alqtendpy.tests.utils.singleshot_immediate_timer()

    await alqtendpy.asyncio.signal_as_future(timer.timeout)


@pytest.mark.asyncio
async def test_await_for_signal_result(qapp):
    source = alqtendpy.tests.utils.Source(args=('hi', 42))

    timer = alqtendpy.tests.utils.singleshot_immediate_timer()
    timer.timeout.connect(source.emit)

    result = await alqtendpy.asyncio.signal_as_future(source.signal)

    assert result == source.args


@pytest.mark.asyncio
async def test_await_immediate_signal_manual():
    source = alqtendpy.tests.utils.Source(args=('hi', 42))

    d = alqtendpy.asyncio.signal_as_future(source.signal)
    source.emit()
    result = await d

    assert result == source.args


@pytest.mark.asyncio
async def test_await_immediate_signal_integrated():
    source = alqtendpy.tests.utils.Source(args=('hi', 42))

    result = await alqtendpy.asyncio.signal_as_future(
        signal=source.signal,
        f=source.emit,
    )

    assert result == source.args
