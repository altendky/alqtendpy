import decorator
from PyQt5 import QtCore
import pytest
import twisted

import altendpyqt5.tests.utils
import altendpyqt5.twisted


pytestmark = pytest.mark.twisted


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

    assert result == source.args


@pytest.inlineCallbacks
def test_await_for_signal_result():
    yield twisted.internet.defer.ensureDeferred(
        async_await_for_signal_result(),
    )


async def async_await_immediate_signal_manual():
    source = altendpyqt5.tests.utils.Source(args=('hi', 42))

    d = altendpyqt5.twisted.signal_as_deferred(source.signal)
    source.emit()
    result = await d

    assert result == source.args


@pytest.inlineCallbacks
def test_async_await_immediate_signal_manual():
    yield twisted.internet.defer.ensureDeferred(
        async_await_immediate_signal_manual(),
    )


async def async_await_immediate_signal_integrated():
    source = altendpyqt5.tests.utils.Source(args=('hi', 42))

    result = await altendpyqt5.twisted.signal_as_deferred(
        signal=source.signal,
        f=source.emit,
    )

    assert result == source.args


@pytest.inlineCallbacks
def test_async_await_immediate_signal_integrated():
    yield twisted.internet.defer.ensureDeferred(
        async_await_immediate_signal_integrated(),
    )
