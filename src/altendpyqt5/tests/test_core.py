import altendpy.tests.common
import PyQt5.QtCore

import altendpyqt5.core


def test_signal_independence():
    class C:
        a = altendpyqt5.core.Signal(int)
        b = altendpyqt5.core.Signal(int)

    value_checkers = {
        'a': altendpy.tests.common.Values(
            initial=None,
            input=[1, 2, 3],
            expected=[1, 2, 3],
        ),
        'b': altendpy.tests.common.Values(
            initial=None,
            input=[10, 20, 30],
            expected=[10, 20, 30],
        ),
    }

    c = C()
    for name, checker in value_checkers.items():
        getattr(c, name).connect(checker.collect)

    for name, checker in value_checkers.items():
        for value in checker.input:
            getattr(c, name).emit(value)

    for name, checker in value_checkers.items():
        assert tuple(checker.expected) == tuple(checker.collected)


def test_signal_chaining():
    class C:
        a = altendpyqt5.core.Signal(int)
        b = altendpyqt5.core.Signal(int)

    input = [1, 2, 3]

    value_checkers = {
        'a': altendpy.tests.common.Values(
            initial=None,
            input=input,
            expected=input,
        ),
        'b': altendpy.tests.common.Values(
            initial=None,
            input=None,
            expected=input,
        ),
    }

    c = C()
    c.a.connect(c.b)

    for name, checker in value_checkers.items():
        getattr(c, name).connect(checker.collect)

    for value in value_checkers['a'].input:
        c.a.emit(value)

    for name, checker in value_checkers.items():
        assert tuple(checker.expected) == tuple(checker.collected)


def test_signal_to_pyqtslot():
    class Signal:
        signal = altendpyqt5.core.Signal()

    class Slot(PyQt5.QtCore.QObject):
        @PyQt5.QtCore.pyqtSlot()
        def slot(self):
            pass

    s = Signal()
    q = Slot()

    s.signal.connect(q.slot)


# def test_signal_repr():
#     class C:
#         signal = altendpyqt5.core.Signal()
#
#     c = C()
#
#     expected = (
#         '<bound PYQT_SIGNAL signal of _SignalQObject object at 0x'
#         ' of C object at 0x'
#     )
#
#     actual = repr(c.signal)
#     print(actual)
#     actual = actual.split()
#
#     for index in (-1, -6):
#         actual[index] = actual[index][:2]
#
#     actual = ' '.join(actual)
#
#     assert actual == expected
