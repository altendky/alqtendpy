import decorator
import pytest
import twisted

import alqtendpy.tests.utils
import alqtendpy.twisted


pytestmark = pytest.mark.twisted


# https://github.com/pytest-dev/pytest-twisted/issues/31
@decorator.decorator
def asyncCallbacks(fun, *args, **kw):
    return twisted.internet.defer.ensureDeferred(fun(*args, **kw))



@pytest.inlineCallbacks
def test_yield_for_signal(qtbot):
    timer = alqtendpy.tests.utils.singleshot_immediate_timer()

    yield alqtendpy.twisted.signal_as_deferred(timer.timeout)


@pytest.inlineCallbacks
def test_yield_for_signal_arguments(qtbot):
    source = alqtendpy.tests.utils.Source(args=('hi', 42))

    timer = alqtendpy.tests.utils.singleshot_immediate_timer()
    timer.timeout.connect(source.emit)

    result = yield alqtendpy.twisted.signal_as_deferred(source.signal)

    assert result == source.args


@asyncCallbacks
async def test_await_for_signal():
    timer = alqtendpy.tests.utils.singleshot_immediate_timer()

    await alqtendpy.twisted.signal_as_deferred(timer.timeout)


@asyncCallbacks
async def test_await_for_signal_result():
    source = alqtendpy.tests.utils.Source(args=('hi', 42))

    timer = alqtendpy.tests.utils.singleshot_immediate_timer()
    timer.timeout.connect(source.emit)

    result = await alqtendpy.twisted.signal_as_deferred(source.signal)

    assert result == source.args


@asyncCallbacks
async def test_await_immediate_signal_manual():
    source = alqtendpy.tests.utils.Source(args=('hi', 42))

    d = alqtendpy.twisted.signal_as_deferred(source.signal)
    source.emit()
    result = await d

    assert result == source.args


@asyncCallbacks
async def test_await_immediate_signal_integrated():
    source = alqtendpy.tests.utils.Source(args=('hi', 42))

    result = await alqtendpy.twisted.signal_as_deferred(
        signal=source.signal,
        f=source.emit,
    )

    assert result == source.args
