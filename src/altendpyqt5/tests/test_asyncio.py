import pytest
import quamash

import altendpyqt5.tests.utils
import altendpyqt5.asyncio


@pytest.yield_fixture()
def event_loop(qapp):
    loop = quamash.QEventLoop(qapp)
    yield loop
    loop.close()


@pytest.mark.asyncio
async def test_await_for_signal(qapp):
    timer = altendpyqt5.tests.utils.singleshot_immediate_timer()

    await altendpyqt5.asyncio.signal_as_future(timer.timeout)


@pytest.mark.asyncio
async def test_await_for_signal_result(qapp):
    source = altendpyqt5.tests.utils.Source(args=('hi', 42))

    timer = altendpyqt5.tests.utils.singleshot_immediate_timer()
    timer.timeout.connect(source.emit)

    result = await altendpyqt5.asyncio.signal_as_future(source.signal)

    assert result == source.args


@pytest.mark.asyncio
async def test_await_immediate_signal_manual():
    source = altendpyqt5.tests.utils.Source(args=('hi', 42))

    d = altendpyqt5.asyncio.signal_as_future(source.signal)
    source.emit()
    result = await d

    assert result == source.args


@pytest.mark.asyncio
async def test_await_immediate_signal_integrated():
    source = altendpyqt5.tests.utils.Source(args=('hi', 42))

    result = await altendpyqt5.asyncio.signal_as_future(
        signal=source.signal,
        f=source.emit,
    )

    assert result == source.args
