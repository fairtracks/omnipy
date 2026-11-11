"""Test compute task template and task behavior."""

import os
from typing import Annotated

import pytest
import pytest_cases as pc

from omnipy.compute.task import Task, TaskTemplate, TaskTemplateCore
from omnipy.data.model import Model
from omnipy.shared.exceptions import JobStateException
from omnipy.util.pydantic import ValidationError

from ..helpers.functions import assert_func_wrapper
from .cases.raw.functions import format_to_string_func, power_m1_func
from .cases.tasks import TaskCase
from .helpers.mocks import MockLocalRunner


@pytest.mark.usefixtures('mock_local_runner')
def test_init() -> None:
    task_template = TaskTemplate()(format_to_string_func)
    assert isinstance(task_template, TaskTemplateCore)
    assert_func_wrapper(task_template, format_to_string_func)

    with pytest.raises(TypeError):
        TaskTemplate(format_to_string_func)(format_to_string_func)  # pyright: ignore[reportCallIssue]

    with pytest.raises(JobStateException):
        Task(format_to_string_func)

    task = task_template.apply()
    assert isinstance(task, Task)
    assert_func_wrapper(task, format_to_string_func)


@pc.parametrize_with_cases('case', cases='.cases.tasks')
def test_task_run(
    mock_local_runner: Annotated[MockLocalRunner, pytest.fixture], case: TaskCase
) -> None:
    if hasattr(mock_local_runner, 'finished'):
        assert mock_local_runner.finished is False

    task_template = TaskTemplate()(case.task_func)
    assert_func_wrapper(task_template, case.task_func)

    with pytest.raises(TypeError):
        task_template(*case.args, **case.kwargs)

    task = task_template.apply()
    assert_func_wrapper(task, case.task_func)

    result = task(*case.args, **case.kwargs)

    case.assert_results_func(result)

    if hasattr(mock_local_runner, 'finished'):
        assert mock_local_runner.finished is True


def test_task_run_parameter_variants(
    mock_local_runner: Annotated[MockLocalRunner, pytest.fixture],
) -> None:
    """Test task runs accept positional and keyword variants."""

    if hasattr(mock_local_runner, 'finished'):
        assert mock_local_runner.finished is False

    power_m1 = TaskTemplate()(power_m1_func)

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
    power_m1 = TaskTemplate()(power_m1_func).apply()

    with pytest.raises(TypeError):
        power_m1()  # type: ignore[call-arg]

    with pytest.raises(TypeError):
        power_m1(5)  # type: ignore[call-arg]

    with pytest.raises(TypeError):
        power_m1(4, minus_one=False)  # type: ignore[call-arg]


# TODO: Remove the skip of test_job_boundaries_validate_parents_of_changed_nested_models_known_issue
#       when job boundary validation is implemented as a job modifier
@pytest.mark.skipif(
    os.getenv('OMNIPY_FORCE_SKIPPED_TEST') != '1',
    reason="""
Known issue: jobs do not yet validate their input and output data. Changing a nested Model in place
does not rerun the validators of its parents (see
test_parent_validators_rerun_only_on_validation_of_or_changes_through_the_parent in
tests/data/test_model.py). A job can thus receive or return data that breaks a rule of a parent.
Validation at job boundaries is planned as a job modifier, rerunning the validators of the parents.
""",
)
@pytest.mark.usefixtures('mock_local_runner')
def test_job_boundaries_validate_parents_of_changed_nested_models_known_issue() -> None:
    class ShortListsModel(Model[list[Model[list[int]]]]):
        @classmethod
        def _parse_data(cls, data: list[Model[list[int]]]) -> list[Model[list[int]]]:
            if any(len(inner) > 2 for inner in data):  # pyright: ignore[reportArgumentType]
                raise ValueError('Inner lists can have at most two elements')
            return data

    @TaskTemplate()
    def extend_first_list(model: ShortListsModel) -> ShortListsModel:
        model[0].append(3)  # pyright: ignore[reportIndexIssue]
        return model

    @TaskTemplate()
    def return_unchanged(model: ShortListsModel) -> ShortListsModel:
        return model

    with pytest.raises(ValidationError):
        extend_first_list.run(ShortListsModel([[1, 2]]))  # pyright: ignore[reportArgumentType]

    broken_input = ShortListsModel([[1, 2]])
    broken_input[0].append(3)  # pyright: ignore[reportAttributeAccessIssue]
    with pytest.raises(ValidationError):
        return_unchanged.run(broken_input)  # pyright: ignore[reportArgumentType]
