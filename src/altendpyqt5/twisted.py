import attr
import twisted.internet.defer


def get_reactor():
    import twisted.internet.reactor
    return twisted.internet.reactor


@attr.s
class DeferredForSignal:
    signal = attr.ib()
    timeout = attr.ib(default=None)
    deferred = attr.ib(
        default=attr.Factory(
            factory=lambda self: twisted.internet.defer.Deferred(
                canceller=self.cancelled,
            ),
            takes_self=True,
        ),
    )
    reactor = attr.ib(factory=get_reactor)

    def connect(self):
        self.signal.connect(self.slot)

        if self.timeout is not None:
            self.deferred.addTimeout(
                timeout=self.timeout,
                clock=self.reactor,
            )

    def disconnect(self):
        self.signal.disconnect(self.slot)

    def cancelled(self, deferred):
        self.disconnect()

    def slot(self, *args):
        self.disconnect()
        self.deferred.callback(args)


def signal_as_deferred(signal, timeout=None, f=None, *args, **kwargs):
    dfs = DeferredForSignal(signal=signal, timeout=timeout)
    dfs.connect()

    if f is not None:
        f(*args, **kwargs)

    return dfs.deferred
