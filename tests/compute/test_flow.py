from collections.abc import Iterable
from datetime import datetime
from typing import Annotated, Callable, cast, Type

import pytest
import pytest_cases as pc

from omnipy.api.exceptions import JobStateException
from omnipy.api.protocols.private.compute.job import IsFuncArgJobTemplate
from omnipy.api.protocols.public.compute import (IsDagFlowTemplate,
                                                 IsFuncFlowTemplate,
                                                 IsLinearFlowTemplate)
from omnipy.compute.flow import DagFlowTemplate, FuncFlowTemplate, LinearFlowTemplate
from omnipy.compute.job import JobBase, JobMixin, JobTemplateMixin
from omnipy.compute.task import TaskTemplate

from .cases.flows import FlowCase
from .cases.raw.functions import data_import_func, empty_dict_func, format_to_string_func
from .helpers.classes import AnyFlowClsTuple, FuncArgFlowClsTuple, TaskTemplateArgFlowClsTuple
from .helpers.functions import assert_flow_or_flow_template, assert_updated_wrapper
from .helpers.mocks import (IsMockTaskTemplateAssertSameTimeOfCurFlowRun,
                            MockFlowTemplateSubclass,
                            MockJobTemplateSubclass,
                            MockLocalRunner,
                            MockTaskTemplateAssertSameTimeOfCurFlowRun,
                            MockTaskTemplateAssertSameTimeOfCurFlowRunCore)

MockJobClasses = tuple[Type[JobBase], Type[JobTemplateMixin], Type[JobMixin]]


def test_flow_context_mock() -> None:
    flow_tmpl: MockFlowTemplateSubclass = MockFlowTemplateSubclass()
    flow = flow_tmpl.apply()
    job_tmpl: MockJobTemplateSubclass = MockJobTemplateSubclass()
    job = job_tmpl.apply()

    for job_obj in flow, flow_tmpl, job, job_tmpl:
        assert job_obj.in_flow_context is False

    for job_obj in flow_tmpl, job, job_tmpl:
        assert not hasattr(job_obj, 'flow_context')

    with flow.flow_context:
        job_tmpl_inside: MockJobTemplateSubclass = MockJobTemplateSubclass()
        job_inside = job_tmpl_inside.apply()

        for job_obj in flow, flow_tmpl, job, job_tmpl, job_inside, job_tmpl_inside:
            assert job_obj.in_flow_context is True

    job_tmpl_outside: MockJobTemplateSubclass = MockJobTemplateSubclass()
    job_outside = job_tmpl_outside.apply()

    for job_obj in (flow,
                    flow_tmpl,
                    job,
                    job_tmpl,
                    job_inside,
                    job_tmpl_inside,
                    job_outside,
                    job_tmpl_outside):
        assert job_obj.in_flow_context is False


def test_time_of_flow_run_mock() -> None:
    flow_tmpl: MockFlowTemplateSubclass = MockFlowTemplateSubclass()
    flow = flow_tmpl.apply()
    job_tmpl: MockJobTemplateSubclass = MockJobTemplateSubclass()
    job = job_tmpl.apply()

    assert flow.time_of_cur_toplevel_flow_run is None
    assert job.time_of_cur_toplevel_flow_run is None

    assert not hasattr(flow_tmpl, 'time_of_cur_toplevel_flow_run')
    assert not hasattr(job_tmpl, 'time_of_cur_toplevel_flow_run')

    for job_obj in flow_tmpl, job, job_tmpl:
        assert not hasattr(job_obj, 'time_of_last_run')

    assert flow.time_of_last_run is None
    with flow.flow_context:
        assert isinstance(flow.time_of_last_run, datetime)
        assert flow.time_of_last_run is not None
        prev_time_of_last_run = flow.time_of_last_run
        assert flow.time_of_cur_toplevel_flow_run == prev_time_of_last_run

        job_inside = MockJobTemplateSubclass().apply()

        assert job.time_of_cur_toplevel_flow_run == prev_time_of_last_run
        assert job_inside.time_of_cur_toplevel_flow_run == prev_time_of_last_run

    job_outside = MockJobTemplateSubclass().apply()

    assert flow.time_of_cur_toplevel_flow_run is None
    assert job.time_of_cur_toplevel_flow_run is None
    assert job_inside.time_of_cur_toplevel_flow_run is None
    assert job_outside.time_of_cur_toplevel_flow_run is None

    assert flow.time_of_last_run == prev_time_of_last_run


def test_fail_init_flow_cls_tuple(
    mock_local_runner: Annotated[MockLocalRunner, pytest.fixture],
    flow_cls_tuple: Annotated[AnyFlowClsTuple, pytest.fixture],
) -> None:
    flow_cls = flow_cls_tuple.flow_cls

    with pytest.raises(JobStateException):
        flow_cls(format_to_string_func)


def test_fail_init_func_arg_flow_classes(
    mock_local_runner: Annotated[MockLocalRunner, pytest.fixture],
    func_arg_flow_cls_tuple: Annotated[FuncArgFlowClsTuple, pytest.fixture],
) -> None:
    flow_cls, flow_tmpl_cls, _ = func_arg_flow_cls_tuple
    with pytest.raises(TypeError):
        flow_cls()

    with pytest.raises(TypeError):
        flow_tmpl_cls(lambda x: x)(lambda y: y)  # type: ignore[misc, call-arg]


def test_init_task_template_args_flow_templates(
    mock_local_runner: Annotated[MockLocalRunner, pytest.fixture],
    task_tmpl_arg_flow_cls_tuple: Annotated[TaskTemplateArgFlowClsTuple, pytest.fixture],
) -> None:
    _, flow_tmpl_cls, assert_flow_tmpl_cls = task_tmpl_arg_flow_cls_tuple

    task_tmpl = TaskTemplate()(format_to_string_func)
    flow_template = flow_tmpl_cls(task_tmpl)(format_to_string_func)

    assert_flow_or_flow_template(
        flow_template,
        assert_flow_cls=assert_flow_tmpl_cls,
        assert_func=format_to_string_func,
        assert_name='format_to_string_func')


def test_init_func_arg_flow_templates(
    mock_local_runner: Annotated[MockLocalRunner, pytest.fixture],
    func_arg_flow_cls_tuple: Annotated[FuncArgFlowClsTuple, pytest.fixture],
) -> None:
    _, flow_tmpl_cls, assert_flow_tmpl_cls = func_arg_flow_cls_tuple

    flow_template = flow_tmpl_cls()(format_to_string_func)

    assert_flow_or_flow_template(
        flow_template,
        assert_flow_cls=assert_flow_tmpl_cls,
        assert_func=format_to_string_func,
        assert_name='format_to_string_func')


def _run_and_assert_flow_template(flow_template: IsFuncArgJobTemplate,
                                  assert_flow_cls: type,
                                  assert_func: Callable,
                                  assert_name: str) -> None:
    flow = flow_template.apply()
    assert_flow_or_flow_template(
        flow, assert_flow_cls=assert_flow_cls, assert_func=assert_func, assert_name=assert_name)

    assert flow_template.run('text', number=1) == 'text: 1'
    assert flow('text', number=1) == 'text: 1'

    with pytest.raises(TypeError):
        flow_template.run('text')
        flow('text')


def test_apply_run_task_tmpl_arg_flow_cls_tuple(
    mock_local_runner: Annotated[MockLocalRunner, pytest.fixture],
    task_tmpl_arg_flow_cls_tuple: Annotated[TaskTemplateArgFlowClsTuple, pytest.fixture],
) -> None:
    flow_cls, flow_tmpl_cls, _ = task_tmpl_arg_flow_cls_tuple

    task_tmpl = TaskTemplate()(format_to_string_func)
    flow_template = flow_tmpl_cls(task_tmpl)(format_to_string_func)

    _run_and_assert_flow_template(flow_template,
                                  flow_cls,
                                  format_to_string_func,
                                  'format_to_string_func')


def test_apply_run_func_arg_flow_cls_tuple(
    mock_local_runner: Annotated[MockLocalRunner, pytest.fixture],
    func_arg_flow_cls_tuple: Annotated[FuncArgFlowClsTuple, pytest.fixture],
) -> None:
    flow_cls, flow_tmpl_cls, _ = func_arg_flow_cls_tuple

    flow_template = flow_tmpl_cls()(format_to_string_func)

    _run_and_assert_flow_template(flow_template,
                                  flow_cls,
                                  format_to_string_func,
                                  'format_to_string_func')


def test_refine_task_tmpl_arg_flow_cls_tuple(
    mock_local_runner: Annotated[MockLocalRunner, pytest.fixture],
    task_tmpl_arg_flow_cls_tuple: Annotated[TaskTemplateArgFlowClsTuple, pytest.fixture],
) -> None:
    _, flow_tmpl_cls, assert_flow_tmpl_cls = task_tmpl_arg_flow_cls_tuple

    flow_template = flow_tmpl_cls(TaskTemplate()(format_to_string_func))(empty_dict_func)
    flow_template_2 = flow_template.refine(TaskTemplate()(data_import_func), name='data_import')

    assert_flow_or_flow_template(
        flow_template_2,
        assert_flow_cls=assert_flow_tmpl_cls,
        assert_func=empty_dict_func,
        assert_name='data_import')
    assert flow_template_2.run() == '{"my_data": [123,234,345,456]}'


def test_refine_func_arg_flow_cls_tuple(
    mock_local_runner: Annotated[MockLocalRunner, pytest.fixture],
    func_arg_flow_cls_tuple: Annotated[FuncArgFlowClsTuple, pytest.fixture],
) -> None:
    _, flow_tmpl_cls, assert_flow_tmpl_cls = func_arg_flow_cls_tuple

    flow_template = flow_tmpl_cls()(empty_dict_func)
    flow_template_2 = flow_template.refine(name='not_data_import')

    assert_flow_or_flow_template(
        flow_template_2,
        assert_flow_cls=assert_flow_tmpl_cls,
        assert_func=empty_dict_func,
        assert_name='not_data_import')
    assert flow_template_2.run() == {}


def _apply_revise_and_run_and_assert_flow_template(flow_template: IsFuncArgJobTemplate,
                                                   assert_flow_tmpl_cls: type,
                                                   assert_func: Callable,
                                                   assert_name: str) -> None:
    flow = flow_template.apply()
    flow_template_2 = flow.revise()

    assert_flow_or_flow_template(
        flow_template_2,
        assert_flow_cls=assert_flow_tmpl_cls,
        assert_func=format_to_string_func,
        assert_name='format_to_string_func')
    assert flow_template_2.run('text', 1) == 'text: 1'


def test_revise_task_tmpl_arg_flow_cls_tuple(
    mock_local_runner: Annotated[MockLocalRunner, pytest.fixture],
    task_tmpl_arg_flow_cls_tuple: Annotated[TaskTemplateArgFlowClsTuple, pytest.fixture],
) -> None:
    _, flow_tmpl_cls, assert_flow_tmpl_cls = task_tmpl_arg_flow_cls_tuple

    flow_template = flow_tmpl_cls(TaskTemplate()(format_to_string_func))(format_to_string_func)

    _apply_revise_and_run_and_assert_flow_template(flow_template,
                                                   assert_flow_tmpl_cls,
                                                   format_to_string_func,
                                                   'format_to_string_func')


def test_revise_func_arg_flow_cls_tuple(
    mock_local_runner: Annotated[MockLocalRunner, pytest.fixture],
    func_arg_flow_cls_tuple: Annotated[FuncArgFlowClsTuple, pytest.fixture],
) -> None:
    _, flow_tmpl_cls, assert_flow_tmpl_cls = func_arg_flow_cls_tuple

    flow_template = flow_tmpl_cls()(format_to_string_func)

    _apply_revise_and_run_and_assert_flow_template(flow_template,
                                                   assert_flow_tmpl_cls,
                                                   format_to_string_func,
                                                   'format_to_string_func')


@pc.parametrize_with_cases('case', cases='.cases.flows')
def test_flow_run_flow_cls_tuple(mock_local_runner: Annotated[MockLocalRunner, pytest.fixture],
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
    @TaskTemplate()
    def task_tmpl() -> tuple[int, int]:
        return 42, 42

    @TaskTemplate()
    def my_formula_tmpl(number: int | tuple[int, ...], plus_number: int = 0) -> int:
        number = sum(number) if isinstance(number, Iterable) else number
        return number * 2 + plus_number

    @LinearFlowTemplate(task_tmpl, my_formula_tmpl)
    def linear_flow_tmpl() -> int:
        ...

    linear_flow = linear_flow_tmpl.apply()
    assert linear_flow() == 168


def test_dag_flow_ignore_args_and_non_matched_kwarg_returns(
        mock_local_runner: Annotated[MockLocalRunner, pytest.fixture]) -> None:
    @TaskTemplate()
    def task_tmpl() -> int:
        return 42

    @TaskTemplate()
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
    @TaskTemplate()
    def task_tmpl() -> dict[str, int]:
        return {'number': 42}

    @TaskTemplate()
    def double_tmpl(number: int) -> int:
        return number * 2

    @DagFlowTemplate(task_tmpl, double_tmpl)
    def dag_flow_tmpl() -> int:
        ...

    dag_flow = dag_flow_tmpl.apply()
    assert dag_flow() == 84


def mypy_fix_mock_task_template_assert_same_time(
        mock_task_template_assert_same_time: object
) -> MockTaskTemplateAssertSameTimeOfCurFlowRunCore:
    return cast(MockTaskTemplateAssertSameTimeOfCurFlowRunCore, mock_task_template_assert_same_time)


def test_time_of_multi_level_flow_run_flow_cls_tuple(
        mock_local_runner: Annotated[MockLocalRunner, pytest.fixture]) -> None:

    # TaskTemplate
    @MockTaskTemplateAssertSameTimeOfCurFlowRun()
    def task_tmpl() -> int:
        return 42

    task = task_tmpl.apply()
    assert task() == 42
    assert task_tmpl.persisted_time_of_cur_toplevel_flow_run is None
    task_tmpl.reset_persisted_time_of_cur_toplevel_flow_run()

    # LinearFlowTemplate
    @MockTaskTemplateAssertSameTimeOfCurFlowRun()
    def plus_one_tmpl(number: int) -> int:
        return number + 1

    @LinearFlowTemplate(task_tmpl, plus_one_tmpl)
    def linear_flow_tmpl() -> int:
        ...

    _assert_diff_time_of_two_flow_runs(
        linear_flow_tmpl, assert_result=43, assert_task_tmpl=task_tmpl)

    # DagFlowTemplate
    @MockTaskTemplateAssertSameTimeOfCurFlowRun()
    def double_tmpl(number: int) -> int:
        return number * 2

    @DagFlowTemplate(linear_flow_tmpl.refine(result_key='number'), double_tmpl)
    def dag_flow_tmpl() -> int:
        ...

    _assert_diff_time_of_two_flow_runs(dag_flow_tmpl, assert_result=86, assert_task_tmpl=task_tmpl)

    @FuncFlowTemplate()
    def func_flow_tmpl(number: int) -> int:
        return dag_flow_tmpl() + number

    _assert_diff_time_of_two_flow_runs(
        func_flow_tmpl, 14, assert_result=100, assert_task_tmpl=task_tmpl)

    # FuncFlowTemplate again
    @FuncFlowTemplate()
    def func_flow_2_tmpl() -> int:
        return int(func_flow_tmpl(14) / 2)

    with pytest.raises(TypeError):
        func_flow_2_tmpl()

    _assert_diff_time_of_two_flow_runs(
        func_flow_2_tmpl, assert_result=50, assert_task_tmpl=task_tmpl)


def _assert_diff_time_of_two_flow_runs(
        flow_tmpl: IsLinearFlowTemplate | IsDagFlowTemplate | IsFuncFlowTemplate,
        *args: object,
        assert_result: object,
        assert_task_tmpl: IsMockTaskTemplateAssertSameTimeOfCurFlowRun):
    flow = flow_tmpl.apply()
    assert flow(*args) == assert_result

    assert flow.time_of_cur_toplevel_flow_run is None
    assert isinstance(flow.time_of_last_run, datetime)
    time_of_prev_flow_run = flow.time_of_last_run

    assert assert_task_tmpl.persisted_time_of_cur_toplevel_flow_run == time_of_prev_flow_run
    assert_task_tmpl.reset_persisted_time_of_cur_toplevel_flow_run()

    flow_2 = flow_tmpl.apply()
    assert flow_2(*args) == assert_result

    assert flow_2.time_of_cur_toplevel_flow_run is None
    assert isinstance(flow_2.time_of_last_run, datetime)
    assert flow_2.time_of_last_run != time_of_prev_flow_run

    assert assert_task_tmpl.persisted_time_of_cur_toplevel_flow_run == flow_2.time_of_last_run
    assert_task_tmpl.reset_persisted_time_of_cur_toplevel_flow_run()
