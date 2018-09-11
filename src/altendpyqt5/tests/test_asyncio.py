import asyncio

import pytest

import altendpyqt5.tests.utils
import altendpyqt5.asyncio


pytestmark = pytest.mark.asyncio


async def test_async_await_for_signal(qapp):
    timer = altendpyqt5.tests.utils.singleshot_immediate_timer()

    await altendpyqt5.asyncio.signal_as_async(timer.timeout)


async def test_async_await_for_signal_result(qapp):
    source = altendpyqt5.tests.utils.Source(args=('hi', 42))

    timer = altendpyqt5.tests.utils.singleshot_immediate_timer()
    timer.timeout.connect(source.emit)

    result = await altendpyqt5.asyncio.signal_as_async(source.signal)

    assert result == source.args
