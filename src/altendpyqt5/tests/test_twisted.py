import attr
from PyQt5 import QtCore
import pytest
import twisted

import altendpyqt5.twisted


def singleshot_immediate_timer():
    timer = QtCore.QTimer()
    timer.setSingleShot(True)
    timer.setInterval(0)
    timer.start()

    return timer


@attr.s
class Source(QtCore.QObject):
    signal = QtCore.pyqtSignal(str, int)

    args = attr.ib()

    def __attrs_post_init__(self):
        super().__init__()

    def emit(self):
        self.signal.emit(*self.args)


@pytest.inlineCallbacks
def test_yield_for_signal(qtbot):
    timer = singleshot_immediate_timer()

    yield altendpyqt5.twisted.signal_as_deferred(timer.timeout)


@pytest.inlineCallbacks
def test_yield_for_signal_arguments(qtbot):
    source = Source(args=('hi', 42))

    timer = singleshot_immediate_timer()
    timer.timeout.connect(source.emit)

    result = yield altendpyqt5.twisted.signal_as_deferred(source.signal)

    assert result == source.args


async def async_await_for_signal():
    timer = singleshot_immediate_timer()

    f = altendpyqt5.twisted.signal_as_async(timer.timeout)
    print('f (before):', f, type(f))
    try:
        await f
    finally:
        print('f  (after):', f, type(f))


@pytest.inlineCallbacks
def test_await_for_signal():
    yield twisted.internet.defer.ensureDeferred(async_await_for_signal())


async def async_await_for_signal_result():
    source = Source(args=('hi', 42))

    timer = singleshot_immediate_timer()
    timer.timeout.connect(source.emit)

    f = altendpyqt5.twisted.signal_as_async(source.signal)
    print('f (before):', f, type(f))
    try:
        result = await f
    finally:
        print('f  (after):', f, type(f))

    print('result:', result)

    assert result == source.args


@pytest.inlineCallbacks
def test_await_for_signal_result():
    yield twisted.internet.defer.ensureDeferred(
        async_await_for_signal_result(),
    )
