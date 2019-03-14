import attr
import decorator
import pytest
import twisted
import twisted.internet.task

import altendpyqt5.tests.utils
import altendpyqt5.twisted


pytestmark = pytest.mark.twisted


# https://github.com/pytest-dev/pytest-twisted/issues/31
@decorator.decorator
def asyncCallbacks(fun, *args, **kw):
    return twisted.internet.defer.ensureDeferred(fun(*args, **kw))


@pytest.fixture
def clock():
    return twisted.internet.task.Clock()


@pytest.fixture
def source():
    return altendpyqt5.tests.utils.Source(args=('hi', 42))


@pytest.inlineCallbacks
def test_yield_for_signal(qtbot):
    timer = altendpyqt5.tests.utils.singleshot_immediate_timer()

    yield altendpyqt5.twisted.signal_as_deferred(timer.timeout)


@pytest.inlineCallbacks
def test_yield_for_signal_arguments(qtbot):
    source = altendpyqt5.tests.utils.Source(args=('hi', 42))

    timer = altendpyqt5.tests.utils.singleshot_immediate_timer()
    timer.timeout.connect(source.emit)

    result = yield altendpyqt5.twisted.signal_as_deferred(source.signal)

    assert result == source.args


@asyncCallbacks
async def test_await_for_signal():
    timer = altendpyqt5.tests.utils.singleshot_immediate_timer()

    await altendpyqt5.twisted.signal_as_deferred(timer.timeout)


@asyncCallbacks
async def test_await_for_signal_result():
    source = altendpyqt5.tests.utils.Source(args=('hi', 42))

    timer = altendpyqt5.tests.utils.singleshot_immediate_timer()
    timer.timeout.connect(source.emit)

    result = await altendpyqt5.twisted.signal_as_deferred(source.signal)

    assert result == source.args


@asyncCallbacks
async def test_await_immediate_signal_manual():
    source = altendpyqt5.tests.utils.Source(args=('hi', 42))

    d = altendpyqt5.twisted.signal_as_deferred(source.signal)
    source.emit()
    result = await d

    assert result == source.args


@asyncCallbacks
async def test_await_immediate_signal_integrated():
    source = altendpyqt5.tests.utils.Source(args=('hi', 42))

    result = await altendpyqt5.twisted.signal_as_deferred(
        signal=source.signal,
        f=source.emit,
    )

    assert result == source.args


@pytest.fixture
def deferred_for_signal(clock, source):
    deferred_for_signal = altendpyqt5.twisted.DeferredForSignal(
        signal=source.signal,
        timeout=1,
        reactor=clock,
    )
    deferred_for_signal.connect()

    return deferred_for_signal


@asyncCallbacks
async def test_signal_not_timed_out_yet(clock, deferred_for_signal):
    clock.advance(deferred_for_signal.timeout * 0.9)

    assert not deferred_for_signal.deferred.called


@asyncCallbacks
async def test_signal_does_not_time_out(clock, source, deferred_for_signal):
    clock.advance(deferred_for_signal.timeout * 0.9)
    source.emit()

    await deferred_for_signal.deferred


@asyncCallbacks
async def test_signal_timed_out(clock, deferred_for_signal):
    clock.advance(deferred_for_signal.timeout)

    with pytest.raises(twisted.internet.defer.TimeoutError):
        await deferred_for_signal.deferred
