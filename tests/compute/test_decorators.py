from typing import Annotated, Callable

import pytest
import pytest_cases as pc

from compute.helpers.mocks import MockLocalRunner
from unifair.compute.flow import DagFlow, DagFlowTemplate, FuncFlow, FuncFlowTemplate
from unifair.compute.task import Task, TaskTemplate


@pc.parametrize_with_cases(
    'plus_one_template',
    cases='.cases.decorators',
    has_tag='task',
)
def test_task_template_as_decorator(mock_local_runner: Annotated[MockLocalRunner, pytest.fixture],
                                    plus_one_template: TaskTemplate) -> None:
    assert isinstance(plus_one_template, TaskTemplate)  # noqa  # Pycharm static type checker bug
    assert plus_one_template.name == 'plus_one'  # noqa  # Pycharm static type checker bug

    plus_one = plus_one_template.apply()  # noqa  # Pycharm static type checker bug
    assert isinstance(plus_one, Task)

    assert plus_one(number=3) == 4


@pc.parametrize_with_cases(
    'plus_five_template',
    cases='.cases.decorators',
    has_tag='dag_flow',
)
def test_dag_flow_template_as_decorator(mock_local_runner: Annotated[MockLocalRunner,
                                                                     pytest.fixture],
                                        plus_five_template: DagFlowTemplate) -> None:

    assert (plus_five_template, DagFlowTemplate)
    assert plus_five_template.name == 'plus_five'

    plus_five = plus_five_template.apply()
    assert isinstance(plus_five, DagFlow)

    result = plus_five(3)
    assert isinstance(result, dict)
    assert len(result) == 1
    key, val = result.popitem()
    assert key in ('number', 'x')
    assert val == 8


@pc.parametrize_with_cases(
    'plus_y_template',
    cases='.cases.decorators',
    has_tag='func_flow',
)
def test_func_flow_template_as_decorator(mock_local_runner: Annotated[MockLocalRunner,
                                                                      pytest.fixture],
                                         plus_y_template: FuncFlowTemplate) -> None:

    assert (plus_y_template, FuncFlowTemplate)
    assert plus_y_template.name == 'plus_y'

    plus_y = plus_y_template.apply()
    assert isinstance(plus_y, FuncFlow)

    assert plus_y(3, y=5) == 8


def test_fail_task_template_decorator_with_func_argument() -> None:
    with pytest.raises(TypeError):

        def myfunc(a: Callable) -> Callable:
            return a

        @TaskTemplate(myfunc)
        def plus_one(number: int) -> int:
            return number + 1


@pc.parametrize_with_cases(
    'plus_one_template',
    cases='.cases.decorators',
    prefix='case_task_',
    has_tag='plain',
)
def test_fail_func_flow_template_decorator_with_func_argument(
    mock_local_runner: Annotated[MockLocalRunner, pytest.fixture],
    plus_one_template,
) -> None:
    with pytest.raises(TypeError):

        def myfunc(a: Callable) -> Callable:
            return a

        @FuncFlowTemplate(myfunc)
        def plus_one(number: int) -> int:
            return plus_one_template(number)
