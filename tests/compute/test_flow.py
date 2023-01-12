from typing import Annotated, Dict, Iterable, Tuple, Union

import pytest
import pytest_cases as pc

from omnipy.compute.flow import (DagFlow,
                                 DagFlowTemplate,
                                 Flow,
                                 FlowTemplate,
                                 FuncFlow,
                                 FuncFlowTemplate,
                                 LinearFlowTemplate)
from omnipy.compute.task import TaskTemplate

from .cases.flows import FlowCase
from .cases.raw.functions import format_to_string_func
from .helpers.functions import assert_updated_wrapper
from .helpers.mocks import MockLocalRunner


def test_init(mock_local_runner: Annotated[MockLocalRunner, pytest.fixture]) -> None:
    for class_info in [{
            'template_cls': DagFlowTemplate, 'flow_cls': DagFlow
    }, {
            'template_cls': FuncFlowTemplate, 'flow_cls': FuncFlow
    }]:
        template_cls = class_info['template_cls']
        flow_cls = class_info['flow_cls']

        flow_template = template_cls(format_to_string_func)
        assert isinstance(flow_template, FlowTemplate)
        assert isinstance(flow_template, template_cls)
        assert_updated_wrapper(flow_template, format_to_string_func)

        with pytest.raises(RuntimeError):
            flow_cls(format_to_string_func)

        flow = flow_template.apply()  # noqa  # Pycharm static type checker bug
        assert isinstance(flow, flow_cls)
        assert_updated_wrapper(flow, format_to_string_func)


def test_fail_init(mock_local_runner: Annotated[MockLocalRunner, pytest.fixture]) -> None:
    with pytest.raises(TypeError):
        FlowTemplate()

    with pytest.raises(TypeError):
        Flow()

    with pytest.raises(TypeError):
        FuncFlowTemplate('extra_positional_argument')(lambda x: x)


@pc.parametrize_with_cases('case', cases='.cases.flows')
def test_flow_run(mock_local_runner: Annotated[MockLocalRunner, pytest.fixture],
                  case: FlowCase) -> None:
    if hasattr(mock_local_runner, 'finished'):
        assert mock_local_runner.finished is False

    assert_updated_wrapper(case.flow_template, case.flow_func)

    with pytest.raises(TypeError):
        case.flow_template(*case.args, **case.kwargs)  # noqa

    flow = case.flow_template.apply()
    assert_updated_wrapper(flow, case.flow_func)

    results = flow(*case.args, **case.kwargs)

    case.assert_results_func(results)

    if hasattr(mock_local_runner, 'finished'):
        assert mock_local_runner.finished is True


# TODO: Tests to add:
#       - engine not supporting dag_flow_decorator
#       - engine not supporting func_flow_decorator
#       - dag_flow.tasks (should be a tuple, not a list, for immutability)
#       - linear flow peculiarities


def test_linear_flow_only_first_positional(
        mock_local_runner: Annotated[MockLocalRunner, pytest.fixture]) -> None:
    @TaskTemplate
    def task_tmpl() -> Tuple[int]:
        return 42, 42

    @TaskTemplate
    def my_formula_tmpl(number: Union[int, Tuple[int, ...]], plus_number: int = 0) -> int:
        number = sum(number) if isinstance(number, Iterable) else number
        return number * 2 + plus_number

    @LinearFlowTemplate(task_tmpl, my_formula_tmpl)
    def linear_flow_tmpl() -> int:
        ...

    linear_flow = linear_flow_tmpl.apply()
    assert linear_flow() == 168


def test_dag_flow_ignore_args_and_non_matched_kwarg_returns(
        mock_local_runner: Annotated[MockLocalRunner, pytest.fixture]) -> None:
    @TaskTemplate
    def task_tmpl() -> int:
        return 42

    @TaskTemplate
    def double_tmpl(number: int) -> int:
        return number * 2

    @DagFlowTemplate(
        task_tmpl.refine(result_key='number'),
        task_tmpl.refine(result_key='bumber'),
        task_tmpl,
        double_tmpl)
    def dag_flow_tmpl() -> int:
        ...

    dag_flow = dag_flow_tmpl.apply()
    assert dag_flow() == 84


def test_dynamic_dag_flow_by_returned_dict(
        mock_local_runner: Annotated[MockLocalRunner, pytest.fixture]) -> None:
    @TaskTemplate
    def task_tmpl() -> Dict[str, int]:
        return {'number': 42}

    @TaskTemplate
    def double_tmpl(number: int) -> int:
        return number * 2

    @DagFlowTemplate(task_tmpl, double_tmpl)
    def dag_flow_tmpl() -> int:
        ...

    dag_flow = dag_flow_tmpl.apply()
    assert dag_flow() == 84


def test_func_flow_context(mock_local_runner: Annotated[MockLocalRunner, pytest.fixture]) -> None:
    @TaskTemplate
    def task_tmpl() -> int:
        return 42

    with pytest.raises(TypeError):
        task_tmpl()

    @TaskTemplate
    def double_tmpl(number: int) -> int:
        return number * 2

    @DagFlowTemplate(task_tmpl.refine(result_key='number'), double_tmpl)
    def dag_flow_tmpl() -> int:
        ...

    with pytest.raises(TypeError):
        dag_flow_tmpl()

    dag_flow = dag_flow_tmpl.apply()
    assert dag_flow() == 84

    @FuncFlowTemplate
    def func_flow_tmpl(number: int) -> int:
        return dag_flow_tmpl() + number

    with pytest.raises(TypeError):
        func_flow_tmpl(16)

    func_flow = func_flow_tmpl.apply()
    assert func_flow(16) == 100

    @FuncFlowTemplate
    def func_flow_2_tmpl() -> int:
        return int(func_flow_tmpl(16) / 2)

    with pytest.raises(TypeError):
        func_flow_2_tmpl()

    func_flow_2 = func_flow_2_tmpl.apply()
    assert func_flow_2() == 50
