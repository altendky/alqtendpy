import altendpyqt5.tests.utils
import altendpyqt5.asyncio


async def test_async_await_for_signal():
    timer = altendpyqt5.tests.utils.singleshot_immediate_timer()

    await altendpyqt5.asyncio.signal_as_deferred(timer.timeout)


async def test_async_await_for_signal_result():
    source = altendpyqt5.tests.utils.Source(args=('hi', 42))

    timer = altendpyqt5.tests.utils.singleshot_immediate_timer()
    timer.timeout.connect(source.emit)

    result = await altendpyqt5.asyncio.signal_as_deferred(source.signal)

    print('result:', result)

    assert result == source.args
