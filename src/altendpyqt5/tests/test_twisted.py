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


@pytest.inlineCallbacks
def test_yield_for_signal(qtbot):
    timer = singleshot_immediate_timer()

    yield altendpyqt5.twisted.signal_as_deferred(timer.timeout)


@pytest.inlineCallbacks
def test_yield_for_signal_arguments(qtbot):
    class Source(QtCore.QObject):
        signal = QtCore.pyqtSignal(str, int)

        def emit(self):
            self.signal.emit(*arguments)

    arguments = ('hi', 42)

    source = Source()

    timer = singleshot_immediate_timer()
    timer.timeout.connect(source.emit)

    result = yield altendpyqt5.twisted.signal_as_deferred(source.signal)

    assert result == arguments


async def test_async_await_for_signal():
    timer = singleshot_immediate_timer()

    await altendpyqt5.twisted.signal_as_async(timer.timeout)


@pytest.inlineCallbacks
def test_await_for_signal():
    yield twisted.internet.defer.ensureDeferred(test_async_await_for_signal())
