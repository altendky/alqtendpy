import threading

import outcome
import PyQt5.QtCore
import pytest
import trio

import alqtendpy.core
import alqtendpy.trio


def test_reenter_event_triggers_in_main_thread(qapp):
    result = []

    reenter = alqtendpy.trio.Reenter()

    def post():
        event = alqtendpy.trio.ReenterEvent(alqtendpy.trio.REENTER_EVENT)
        event.fn = handler
        qapp.postEvent(reenter, event)

    def handler():
        result.append(threading.get_ident())

    thread = threading.Thread(target=post)
    thread.start()
    thread.join()

    qapp.processEvents()

    assert result == [threading.get_ident()]


def test_runner_runs_in_main_thread(qapp, qtbot):
    result = {}

    async def main():
        await trio.sleep(0)
        result['thread_id'] = threading.get_ident()

        return 37

    def done_callback(main_outcome):
        result['outcome'] = main_outcome

    runner = alqtendpy.trio.Runner(
        async_fn=main,
        application=qapp,
        done_callback=done_callback,
        manage_application_lifetime=False,
    )

    runner.run()

    qtbot.wait_until(lambda: result.get('outcome') is not None)

    assert result == {
        'outcome': outcome.Value(37),
        'thread_id': threading.get_ident(),
    }


@alqtendpy.trio.welcomes_qt
async def test_get_integer_gets_value(request, qtbot):
    dialog = alqtendpy.trio.IntegerDialog.build()
    dialog.shown.connect(qtbot.addWidget)

    async def user(task_status):
        async with alqtendpy.trio.signal_event_manager(dialog.shown):
            task_status.started()

        qtbot.keyClicks(dialog.edit_widget, str(test_value))
        qtbot.mouseClick(dialog.ok_button, PyQt5.QtCore.Qt.LeftButton)

    test_value = 928

    async with trio.open_nursery() as nursery:
        await nursery.start(user)
        integer = await dialog.wait()

    assert integer == test_value


@alqtendpy.trio.welcomes_qt
async def test_get_integer_raises_cancel_when_canceled(request, qtbot):
    dialog = alqtendpy.trio.IntegerDialog.build()
    dialog.shown.connect(qtbot.addWidget)

    async def user(task_status):
        async with alqtendpy.trio.signal_event_manager(dialog.shown):
            task_status.started()

        qtbot.keyClicks(dialog.edit_widget, 'abc')
        qtbot.mouseClick(dialog.cancel_button, PyQt5.QtCore.Qt.LeftButton)

    async with trio.open_nursery() as nursery:
        await nursery.start(user)
        with pytest.raises(alqtendpy.core.UserCancelledError):
            await dialog.wait()


@alqtendpy.trio.welcomes_qt
async def test_get_integer_gets_value_after_retry(request, qtbot):
    dialog = alqtendpy.trio.IntegerDialog.build()
    dialog.shown.connect(qtbot.addWidget)

    test_value = 928

    async def user(task_status):
        async with alqtendpy.trio.signal_event_manager(dialog.shown):
            task_status.started()

        qtbot.keyClicks(dialog.edit_widget, 'abc')

        async with alqtendpy.trio.signal_event_manager(dialog.shown):
            qtbot.mouseClick(dialog.ok_button, PyQt5.QtCore.Qt.LeftButton)

        qtbot.keyClicks(dialog.edit_widget, str(test_value))
        qtbot.mouseClick(dialog.ok_button, PyQt5.QtCore.Qt.LeftButton)

    async with trio.open_nursery() as nursery:
        await nursery.start(user)
        integer = await dialog.wait()

    assert integer == test_value


@pytest.mark.xfail(reason='this is supposed to fail', strict=True)
@alqtendpy.trio.welcomes_qt
async def test_times_out(request):
    await trio.sleep(10)
