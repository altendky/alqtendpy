import attr
from PyQt5 import QtCore


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
