import asyncio

import attr
import twisted.internet.defer


@attr.s
class DeferredForSignal:
    signal = attr.ib()
    deferred = attr.ib(
        default=attr.Factory(
            factory=lambda self: twisted.internet.defer.Deferred(
                canceller=self.cancel,
            ),
            takes_self=True,
        ),
    )

    def connect(self):
        self.signal.connect(self.slot)

    def disconnect(self):
        self.signal.disconnect(self.slot)

    def cancel(self, deferred):
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
        self.future.add_done_callback(self.cancel)
        self.signal.connect(self.slot)

    def disconnect(self):
        self.signal.disconnect(self.slot)
        self.future.remove_done_callback(self.cancel)

    def cancel(self, future):
        self.disconnect()

    def slot(self, *args):
        self.disconnect()
        self.future.set_result(args)


async def signal_as_async(signal):
    afs = AsyncForSignal(signal=signal)
    afs.connect()

    return afs.future
