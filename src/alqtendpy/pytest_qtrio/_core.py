import functools

import outcome
import pytest
from alqtendpy import qtrio


def host(test_function):
    timeout = 3000

    @pytest.mark.usefixtures('qapp', 'qtbot')
    @functools.wraps(test_function)
    def wrapper(*args, **kwargs):
        request = kwargs['request']

        qapp = request.getfixturevalue('qapp')
        qtbot = request.getfixturevalue('qtbot')

        test_outcomes_sentinel = qtrio.Outcomes(
            qt=outcome.Value(0),
            trio=outcome.Value(29),
        )
        test_outcomes = test_outcomes_sentinel

        def done_callback(outcomes):
            nonlocal test_outcomes
            test_outcomes = outcomes

        runner = qtrio.Runner(
            application=qapp,
            done_callback=done_callback,
            quit_application=False,
        )

        runner.run(
            functools.partial(test_function, **kwargs),
            *args,
            execute_application=False,
        )

        def result_ready():
            message = f'test not finished within {timeout/1000} seconds'
            assert test_outcomes is not test_outcomes_sentinel, message

        # TODO: probably increases runtime of fast tests a lot due to polling
        qtbot.wait_until(result_ready, timeout=timeout)

        test_outcomes.unwrap()

    return wrapper


