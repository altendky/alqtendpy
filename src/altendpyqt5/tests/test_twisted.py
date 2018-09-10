import pytest
import twisted

import altendpyqt5.tests.utils
import altendpyqt5.twisted


@pytest.inlineCallbacks
def test_yield_for_signal(qtbot):
    timer = altendpyqt5.tests.utils.singleshot_immediate_timer()

    yield altendpyqt5.twisted.signal_as_deferred(timer.timeout)


@pytest.inlineCallbacks
def test_yield_for_signal_arguments(qtbot):
    source = altendpyqt5.tests.utils.Source(args=('hi', 42))

    timer = altendpyqt5.tests.utils.singleshot_immediate_timer()
    timer.timeout.connect(source.emit)

    result = yield altendpyqt5.twisted.signal_as_deferred(source.signal)

    assert result == source.args


async def async_await_for_signal():
    timer = altendpyqt5.tests.utils.singleshot_immediate_timer()

    await altendpyqt5.twisted.signal_as_deferred(timer.timeout)


@pytest.inlineCallbacks
def test_await_for_signal():
    yield twisted.internet.defer.ensureDeferred(async_await_for_signal())


async def async_await_for_signal_result():
    source = altendpyqt5.tests.utils.Source(args=('hi', 42))

    timer = altendpyqt5.tests.utils.singleshot_immediate_timer()
    timer.timeout.connect(source.emit)

    result = await altendpyqt5.twisted.signal_as_deferred(source.signal)

    print('result:', result)

    assert result == source.args


@pytest.inlineCallbacks
def test_await_for_signal_result():
    yield twisted.internet.defer.ensureDeferred(
        async_await_for_signal_result(),
    )
