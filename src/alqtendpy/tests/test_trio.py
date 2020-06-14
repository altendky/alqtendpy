import threading

import outcome
import PyQt5.QtCore
import pytest
import trio

import alqtendpy.core
import alqtendpy.qtrio


pytestmark = pytest.mark.twisted


def test_reenter_event_triggers_in_main_thread(qapp):
    result = []

    reenter = alqtendpy.qtrio.Reenter()

    def post():
        event = alqtendpy.qtrio.ReenterEvent(alqtendpy.qtrio.REENTER_EVENT)
        event.fn = handler
        qapp.postEvent(reenter, event)

    def handler():
        result.append(threading.get_ident())

    thread = threading.Thread(target=post)
    thread.start()
    thread.join()

    qapp.processEvents()

    assert result == [threading.get_ident()]


timeout = 3


def test_run_returns_value(testdir):
    test_file = r"""
    import outcome
    from alqtendpy import qtrio

    def test():
        async def main():
            return 29

        result = qtrio.run(main)

        assert result == qtrio.Outcomes(
            qt=outcome.Value(0),
            trio=outcome.Value(29),
        )
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


def test_qt_quit_cancels_trio(testdir):
    test_file = r"""
    import outcome
    import PyQt5.QtCore
    from alqtendpy import qtrio
    import trio


    def test():
        async def main():
            PyQt5.QtCore.QTimer.singleShot(
                100,
                PyQt5.QtCore.QCoreApplication.instance().lastWindowClosed.emit,
            )

            while True:
                await trio.sleep(1)

        outcomes = qtrio.run(async_fn=main)

        assert outcomes.trio.value == None
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


def test_run_runs_in_main_thread(testdir):
    test_file = r"""
    import threading

    from alqtendpy import qtrio

    def test():
        async def main():
            return threading.get_ident()

        outcomes = qtrio.run(main)

        assert outcomes.trio.value == threading.get_ident()
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


def test_runner_runs_in_main_thread(testdir):
    test_file = r"""
    import threading

    from alqtendpy import qtrio


    def test():
        async def main():
            return threading.get_ident()

        runner = qtrio.Runner(async_fn=main)
        outcomes = runner.run()

        assert outcomes.trio.value == threading.get_ident()
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


def test_done_callback_runs_in_main_thread(testdir):
    test_file = r"""
    import threading

    from alqtendpy import qtrio

    def test():
        result = {}

        async def main():
            pass

        def done_callback(outcomes):
            result['thread_id'] = threading.get_ident()

        qtrio.run(async_fn=main, done_callback=done_callback)

        assert result['thread_id'] == threading.get_ident()
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


def test_done_callback_gets_outcomes(testdir):
    test_file = r"""
    import outcome
    from alqtendpy import qtrio

    def test():
        result = {}

        async def main():
            return 93

        def done_callback(outcomes):
            result['outcomes'] = outcomes

        qtrio.run(async_fn=main, done_callback=done_callback)

        assert result['outcomes'] == qtrio.Outcomes(
            qt=None,
            trio=outcome.Value(93),
        )
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


@alqtendpy.qtrio.welcomes_qt
async def test_get_integer_gets_value(request, qtbot):
    dialog = alqtendpy.qtrio.IntegerDialog.build()
    dialog.shown.connect(qtbot.addWidget)

    async def user(task_status):
        async with alqtendpy.qtrio.signal_event_manager(dialog.shown):
            task_status.started()

        qtbot.keyClicks(dialog.edit_widget, str(test_value))
        qtbot.mouseClick(dialog.ok_button, PyQt5.QtCore.Qt.LeftButton)

    test_value = 928

    async with trio.open_nursery() as nursery:
        await nursery.start(user)
        integer = await dialog.wait()

    assert integer == test_value


@alqtendpy.qtrio.welcomes_qt
async def test_get_integer_raises_cancel_when_canceled(request, qtbot):
    dialog = alqtendpy.qtrio.IntegerDialog.build()
    dialog.shown.connect(qtbot.addWidget)

    async def user(task_status):
        async with alqtendpy.qtrio.signal_event_manager(dialog.shown):
            task_status.started()

        qtbot.keyClicks(dialog.edit_widget, 'abc')
        qtbot.mouseClick(dialog.cancel_button, PyQt5.QtCore.Qt.LeftButton)

    async with trio.open_nursery() as nursery:
        await nursery.start(user)
        with pytest.raises(alqtendpy.core.UserCancelledError):
            await dialog.wait()


@alqtendpy.qtrio.welcomes_qt
async def test_get_integer_gets_value_after_retry(request, qtbot):
    dialog = alqtendpy.qtrio.IntegerDialog.build()
    dialog.shown.connect(qtbot.addWidget)

    test_value = 928

    async def user(task_status):
        async with alqtendpy.qtrio.signal_event_manager(dialog.shown):
            task_status.started()

        qtbot.keyClicks(dialog.edit_widget, 'abc')

        async with alqtendpy.qtrio.signal_event_manager(dialog.shown):
            qtbot.mouseClick(dialog.ok_button, PyQt5.QtCore.Qt.LeftButton)

        qtbot.keyClicks(dialog.edit_widget, str(test_value))
        qtbot.mouseClick(dialog.ok_button, PyQt5.QtCore.Qt.LeftButton)

    async with trio.open_nursery() as nursery:
        await nursery.start(user)
        integer = await dialog.wait()

    assert integer == test_value


@pytest.mark.xfail(reason='this is supposed to fail', strict=True)
@alqtendpy.qtrio.welcomes_qt
async def test_times_out(request):
    await trio.sleep(10)
