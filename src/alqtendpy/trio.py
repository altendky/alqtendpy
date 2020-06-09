import contextlib
import functools
import traceback
import typing

import attr
import outcome
import PyQt5.QtCore
import PyQt5.QtWidgets
import trio

import alqtendpy.core


REENTER_EVENT = PyQt5.QtCore.QEvent.Type(
    PyQt5.QtCore.QEvent.registerEventType(),
)


class ReenterEvent(PyQt5.QtCore.QEvent):
    pass


class Reenter(PyQt5.QtCore.QObject):
    def event(self, event: PyQt5.QtCore.QEvent) -> bool:
        event.fn()
        return False


async def wait_signal(signal: PyQt5.QtCore.pyqtBoundSignal) -> typing.Any:
    event = trio.Event()
    result = None

    def slot(*args):
        nonlocal result
        result = args
        event.set()

    connection = signal.connect(slot)

    try:
        await event.wait()
    finally:
        signal.disconnect(connection)

    return result


@attr.s(auto_attribs=True)
class Runner:
    async_fn: typing.Callable[
        [PyQt5.QtWidgets.QApplication],
        typing.Awaitable[None],
    ]
    done_callback: typing.Optional[
        typing.Callable[[outcome.Error], None]
    ] = attr.ib(default=None)
    application: PyQt5.QtWidgets.QApplication = attr.ib(
        factory=PyQt5.QtWidgets.QApplication,
    )
    reenter: Reenter = attr.ib(factory=Reenter)
    manage_application_lifetime: bool = True

    def run(self, *args, **kwargs):
        done_callback = (
            self.trio_done
            if self.done_callback is None
            else self.done_callback
        )

        trio.lowlevel.start_guest_run(
            self.trio_main,
            args,
            kwargs,
            run_sync_soon_threadsafe=self.run_sync_soon_threadsafe,
            done_callback=done_callback,
        )

        if self.manage_application_lifetime:
            return self.application.exec()

        return None

    def run_sync_soon_threadsafe(self, fn):
        event = ReenterEvent(REENTER_EVENT)
        event.fn = fn
        self.application.postEvent(self.reenter, event)

    async def trio_main(self, args, kwargs):
        with trio.CancelScope() as cancel_scope:
            with alqtendpy.core.connection(
                    signal=self.application.lastWindowClosed,
                    slot=cancel_scope.cancel,
            ):
                return await self.async_fn(*args, **kwargs)

    def trio_done(self, main_outcome):
        print('---', repr(main_outcome))
        if isinstance(main_outcome, outcome.Error):
            exc = main_outcome.error
            traceback.print_exception(type(exc), exc, exc.__traceback__)

        if self.manage_application_lifetime:
            self.application.quit()


@attr.s(auto_attribs=True)
class IntegerDialog:
    parent: PyQt5.QtWidgets.QWidget
    dialog: typing.Optional[PyQt5.QtWidgets.QInputDialog] = None
    edit_widget: typing.Optional[PyQt5.QtWidgets.QWidget] = None
    ok_button: typing.Optional[PyQt5.QtWidgets.QPushButton] = None
    cancel_button: typing.Optional[PyQt5.QtWidgets.QPushButton] = None
    attempt: typing.Optional[int] = None
    result: typing.Optional[int] = None

    shown = alqtendpy.core.Signal(PyQt5.QtWidgets.QInputDialog)
    hidden = alqtendpy.core.Signal()

    @classmethod
    def build(
            cls,
            parent: PyQt5.QtCore.QObject = None,
    ) -> 'IntegerDialog':
        return cls(parent=parent)

    def setup(self):
        self.dialog = PyQt5.QtWidgets.QInputDialog(self.parent)

        # TODO: find a better way to trigger population of widgets
        self.dialog.show()

        for widget in self.dialog.findChildren(PyQt5.QtWidgets.QWidget):
            if isinstance(widget, PyQt5.QtWidgets.QLineEdit):
                self.edit_widget = widget
            elif isinstance(widget, PyQt5.QtWidgets.QPushButton):
                if widget.text() == self.dialog.okButtonText():
                    self.ok_button = widget
                elif widget.text() == self.dialog.cancelButtonText():
                    self.cancel_button = widget

            widgets = {self.edit_widget, self.ok_button, self.cancel_button}
            if None not in widgets:
                break
        else:
            raise alqtendpy.core.AlqtendpyException('not all widgets found')

        if self.attempt is None:
            self.attempt = 0
        else:
            self.attempt += 1

        self.shown.emit(self.dialog)

    def teardown(self):
        self.edit_widget = None
        self.ok_button = None
        self.cancel_button = None

        if self.dialog is not None:
            self.dialog.hide()
            self.dialog = None
            self.hidden.emit()

    @contextlib.contextmanager
    def manager(self):
        try:
            self.setup()
            yield
        finally:
            self.teardown()

    async def wait(self) -> int:
        while True:
            with self.manager():
                [result] = await wait_signal(self.dialog.finished)

                if result == PyQt5.QtWidgets.QDialog.Rejected:
                    raise alqtendpy.core.UserCancelledError()

                try:
                    self.result = int(self.dialog.textValue())
                except ValueError:
                    continue

            return self.result


def welcomes_qt(test_function):
    timeout = 3000

    @functools.wraps(test_function)
    def wrapper(*args, **kwargs):
        request = kwargs['request']

        qapp = request.getfixturevalue('qapp')
        qtbot = request.getfixturevalue('qtbot')

        result_sentinel = outcome.Value(29)
        result = result_sentinel

        def done_callback(main_outcome):
            nonlocal result
            result = main_outcome

        runner = alqtendpy.trio.Runner(
            async_fn=test_function,
            application=qapp,
            done_callback=done_callback,
            manage_application_lifetime=False,
        )

        runner.run(*args, **kwargs)

        def result_ready():
            message = f'test not finished within {timeout/1000} seconds'
            assert result is not result_sentinel, message

        qtbot.wait_until(result_ready, timeout=timeout)

        result.unwrap()

    return wrapper


def signal_event(signal: PyQt5.QtCore.pyqtBoundSignal) -> trio.Event:
    # TODO: does this leave these pairs laying around uncollectable?
    event = trio.Event()

    def event_set(*args, **kwargs):
        event.set()

    signal.connect(event_set)
    return event


@contextlib.asynccontextmanager
async def signal_event_manager(signal: PyQt5.QtCore.pyqtBoundSignal):
    event = signal_event(signal)
    yield event
    await event.wait()
