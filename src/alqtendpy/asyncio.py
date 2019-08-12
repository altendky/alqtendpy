import asyncio

import attr


@attr.s
class AsyncForSignal:
    signal = attr.ib()
    future = attr.ib(factory=asyncio.Future)

    def connect(self):
        self.future.add_done_callback(self.cancelled)
        self.signal.connect(self.slot)

    def disconnect(self):
        self.signal.disconnect(self.slot)
        self.future.remove_done_callback(self.cancelled)

    def cancelled(self, future):
        self.disconnect()

    def slot(self, *args):
        self.disconnect()
        self.future.set_result(args)


def signal_as_future(signal, f=None, *args, **kwargs):
    afs = AsyncForSignal(signal=signal)
    afs.connect()

    if f is not None:
        f(*args, **kwargs)

    return afs.future
