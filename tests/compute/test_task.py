from inspect import Parameter
from typing import Annotated

import pytest
import pytest_cases as pc

from omnipy.compute.job_types import JobStateException
from omnipy.compute.task import Task, TaskTemplate

from .cases.raw.functions import format_to_string_func, power_m1_func
from .cases.tasks import TaskCase
from .helpers.functions import assert_updated_wrapper
from .helpers.mocks import MockLocalRunner


def test_init() -> None:
    task_template = TaskTemplate(format_to_string_func)
    assert isinstance(task_template, TaskTemplate)  # noqa
    assert_updated_wrapper(task_template, format_to_string_func)

    with pytest.raises(TypeError):
        TaskTemplate(format_to_string_func)(format_to_string_func)

    with pytest.raises(JobStateException):
        Task(format_to_string_func)

    task = task_template.apply()  # noqa
    assert isinstance(task, Task)
    assert_updated_wrapper(task, format_to_string_func)


@pc.parametrize_with_cases('case', cases='.cases.tasks')
def test_task_run(mock_local_runner: Annotated[MockLocalRunner, pytest.fixture],
                  case: TaskCase) -> None:
    if hasattr(mock_local_runner, 'finished'):
        assert mock_local_runner.finished is False

    task_template = TaskTemplate(case.task_func)
    assert_updated_wrapper(task_template, case.task_func)

    with pytest.raises(TypeError):
        task_template(*case.args, **case.kwargs)

    task = task_template.apply()
    assert_updated_wrapper(task, case.task_func)

    result = task(*case.args, **case.kwargs)

    case.assert_results_func(result)

    if hasattr(mock_local_runner, 'finished'):
        assert mock_local_runner.finished is True


def test_task_run_parameter_variants(
        mock_local_runner: Annotated[MockLocalRunner, pytest.fixture]) -> None:

    if hasattr(mock_local_runner, 'finished'):
        assert mock_local_runner.finished is False

    power_m1 = TaskTemplate(power_m1_func)

    assert power_m1.run(4, 3) == 63
    assert power_m1.run(4, exponent=3) == 63
    assert power_m1.run(number=4, exponent=3) == 63
    assert power_m1.run(4, 3, False) == 64
    assert power_m1.run(4, 3, minus_one=False) == 64
    assert power_m1.run(4, exponent=3, minus_one=False) == 64
    assert power_m1.run(number=4, exponent=3, minus_one=False) == 64

    if hasattr(mock_local_runner, 'finished'):
        assert mock_local_runner.finished is True


def test_error_missing_task_run_parameters() -> None:
    power_m1 = TaskTemplate(power_m1_func).apply()

    with pytest.raises(TypeError):
        power_m1()

    with pytest.raises(TypeError):
        power_m1(5)

    with pytest.raises(TypeError):
        power_m1(4, minus_one=False)
