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


def signal_as_deferred(signal, f=None, *args, **kwargs):
    dfs = DeferredForSignal(signal=signal)
    dfs.connect()

    if f is not None:
        f(*args, **kwargs)

    return dfs.deferred
