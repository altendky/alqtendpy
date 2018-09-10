import asyncio

import attr
import twisted.internet.defer


@attr.s
class DeferredForSignal:
    signal = attr.ib()
    deferred = attr.ib(
        default=attr.Factory(
            factory=lambda self: twisted.internet.defer.Deferred(
                canceller=self.cancelled,
            ),
            takes_self=True,
        ),
    )

    def connect(self):
        self.signal.connect(self.slot)

    def disconnect(self):
        self.signal.disconnect(self.slot)

    def cancelled(self, deferred):
        self.disconnect()

    def slot(self, *args):
        self.disconnect()
        self.deferred.callback(args)


def signal_as_deferred(signal):
    dfs = DeferredForSignal(signal=signal)
    dfs.connect()

    return dfs.deferred


@attr.s
class AsyncForSignal:
    signal = attr.ib()
    future = attr.ib(factory=asyncio.Future)

    def connect(self):
        print('AsyncForSignal.connect()')
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
