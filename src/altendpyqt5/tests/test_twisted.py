from PyQt5 import QtCore
import pytest

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
