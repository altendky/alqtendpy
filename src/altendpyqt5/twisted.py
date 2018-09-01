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
        )
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

