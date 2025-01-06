from typing import Annotated, Callable

import pytest
import pytest_cases as pc

from omnipy.compute.flow import (DagFlow,
                                 DagFlowTemplateCore,
                                 FuncFlow,
                                 FuncFlowTemplate,
                                 FuncFlowTemplateCore,
                                 LinearFlow,
                                 LinearFlowTemplateCore)
from omnipy.compute.task import Task, TaskTemplate, TaskTemplateCore
from omnipy.shared.protocols.compute.job import (IsDagFlowTemplate,
                                                 IsFuncFlowTemplate,
                                                 IsLinearFlowTemplate,
                                                 IsTaskTemplate)

from .helpers.mocks import MockLocalRunner


@pc.parametrize_with_cases(
    'plus_one_template',
    cases='.cases.decorators',
    has_tag='task',
)
def test_task_template_as_decorator(
    mock_local_runner: Annotated[MockLocalRunner, pytest.fixture],
    plus_one_template: IsTaskTemplate,
) -> None:
    assert isinstance(plus_one_template,
                      TaskTemplateCore)  # noqa  # Pycharm static type checker bug
    assert plus_one_template.name == 'plus_one'  # noqa  # Pycharm static type checker bug

    plus_one = plus_one_template.apply()  # noqa  # Pycharm static type checker bug
    assert isinstance(plus_one, Task)

    assert plus_one(number=3) == 4


@pc.parametrize_with_cases(
    'plus_five_template',
    cases='.cases.decorators',
    has_tag='linear_flow',
)
def test_linear_flow_template_as_decorator(
    mock_local_runner: Annotated[MockLocalRunner, pytest.fixture],
    plus_five_template: IsLinearFlowTemplate,
) -> None:

    assert isinstance(plus_five_template, LinearFlowTemplateCore)
    assert plus_five_template.name == 'plus_five'

    plus_five = plus_five_template.apply()
    assert isinstance(plus_five, LinearFlow)

    assert plus_five(3) == 8


@pc.parametrize_with_cases(
    'plus_five_template',
    cases='.cases.decorators',
    has_tag='dag_flow',
)
def test_dag_flow_template_as_decorator(
    mock_local_runner: Annotated[MockLocalRunner, pytest.fixture],
    plus_five_template: IsDagFlowTemplate,
) -> None:

    assert isinstance(plus_five_template, DagFlowTemplateCore)
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
def test_func_flow_template_as_decorator(
    mock_local_runner: Annotated[MockLocalRunner, pytest.fixture],
    plus_y_template: IsFuncFlowTemplate,
) -> None:

    assert isinstance(plus_y_template, FuncFlowTemplateCore)
    assert plus_y_template.name == 'plus_y'

    plus_y = plus_y_template.apply()
    assert isinstance(plus_y, FuncFlow)

    assert plus_y(3, y=5) == 8


def test_fail_task_template_decorator_with_func_argument() -> None:
    with pytest.raises(TypeError):

        def myfunc(a: Callable) -> Callable:
            return a

        @TaskTemplate(myfunc)  # type: ignore[misc, arg-type]
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

        @FuncFlowTemplate(myfunc)  # type: ignore[misc, arg-type]
        def plus_one(number: int) -> int:
            return plus_one_template(number)
