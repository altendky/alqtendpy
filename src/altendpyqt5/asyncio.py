import asyncio

import attr
import pytest


pytestmark = pytest.mark.skip(
    "Need new test setup to handle both Twisted and asyncio",
)


@attr.s
class AsyncForSignal:
    signal = attr.ib()
    future = attr.ib(factory=asyncio.Future)

    def connect(self):
        print('AsyncForSignal.connect()', self.future.get_loop())
        self.future.add_done_callback(self.cancelled)
        self.signal.connect(self.slot)

    def disconnect(self):
        print('AsyncForSignal.disconnect()')
        self.signal.disconnect(self.slot)
        self.future.remove_done_callback(self.cancelled)

    def cancelled(self, future):
        print('AsyncForSignal.cancel()')
        self.disconnect()

    def slot(self, *args):
        print('AsyncForSignal.slot()')
        self.disconnect()
        self.future.set_result(args)


def signal_as_async(signal):
    afs = AsyncForSignal(signal=signal)
    afs.connect()

    return afs.future
