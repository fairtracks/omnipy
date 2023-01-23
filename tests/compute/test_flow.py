from datetime import datetime
from typing import Annotated, Dict, Iterable, Tuple, Type, Union

import pytest
import pytest_cases as pc

from omnipy.compute.flow import (DagFlowTemplate, FuncFlowTemplate, LinearFlowTemplate, FuncFlow)
from omnipy.compute.job import Job, JobBase, JobTemplate, JobStateException
from omnipy.compute.task import TaskTemplate
from omnipy.engine.protocols import IsFlowTemplate

from .cases.flows import FlowCase
from .cases.raw.functions import data_import_func, empty_dict_func, format_to_string_func
from .helpers.classes import FlowClsTuple
from .helpers.functions import assert_flow_or_flow_template, assert_updated_wrapper
from .helpers.mocks import (MockFlowTemplateSubclass,
                            MockJobTemplateSubclass,
                            MockLocalRunner,
                            MockTaskTemplateAssertSameTimeOfCurFlowRun)

MockJobClasses = Tuple[Type[JobBase], Type[JobTemplate], Type[Job]]


def test_flow_context_mock() -> None:
    flow_tmpl = MockFlowTemplateSubclass()
    flow = flow_tmpl.apply()
    job_tmpl = MockJobTemplateSubclass()
    job = job_tmpl.apply()

    for job_obj in flow, flow_tmpl, job, job_tmpl:
        assert job_obj.in_flow_context is False

    for job_obj in flow_tmpl, job, job_tmpl:
        assert not hasattr(job_obj, 'flow_context')

    with flow.flow_context:
        job_tmpl_inside = MockJobTemplateSubclass()
        job_inside = job_tmpl_inside.apply()

        for job_obj in flow, flow_tmpl, job, job_tmpl, job_inside, job_tmpl_inside:
            assert job_obj.in_flow_context is True

    job_tmpl_outside = MockJobTemplateSubclass()
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
    flow_tmpl = MockFlowTemplateSubclass()
    flow = flow_tmpl.apply()
    job_tmpl = MockJobTemplateSubclass()
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
        prev_time_of_last_tun = flow.time_of_last_run
        assert flow.time_of_cur_toplevel_flow_run == prev_time_of_last_tun

        job_inside = MockJobTemplateSubclass().apply()

        assert job.time_of_cur_toplevel_flow_run == prev_time_of_last_tun
        assert job_inside.time_of_cur_toplevel_flow_run == prev_time_of_last_tun

    job_outside = MockJobTemplateSubclass().apply()

    assert flow.time_of_cur_toplevel_flow_run is None
    assert job.time_of_cur_toplevel_flow_run is None
    assert job_inside.time_of_cur_toplevel_flow_run is None
    assert job_outside.time_of_cur_toplevel_flow_run is None

    assert flow.time_of_last_run == prev_time_of_last_tun


def test_init_all_flow_classes(
        mock_local_runner: Annotated[MockLocalRunner, pytest.fixture],
        all_flow_classes: Annotated[Tuple[FlowClsTuple, ...], pytest.fixture]) -> None:
    for class_info in all_flow_classes:
        template_cls = class_info.template_cls
        flow_cls = class_info.flow_cls

        flow_template = template_cls(format_to_string_func)
        assert_flow_or_flow_template(
            flow_template,
            assert_flow_cls=template_cls,
            assert_func=format_to_string_func,
            assert_name='format_to_string_func')

        with pytest.raises(JobStateException):
            flow_cls(format_to_string_func)


def test_init_linear_and_dag_flow_templates(
        mock_local_runner: Annotated[MockLocalRunner, pytest.fixture],
        all_flow_classes: Annotated[Tuple[FlowClsTuple, ...], pytest.fixture]) -> None:
    for class_info in all_flow_classes:
        template_cls = class_info.template_cls

        if any(issubclass(template_cls, cls) for cls in (LinearFlowTemplate, DagFlowTemplate)):
            flow_template = template_cls(TaskTemplate(format_to_string_func))(format_to_string_func)
            assert_flow_or_flow_template(
                flow_template,
                assert_flow_cls=template_cls,
                assert_func=format_to_string_func,
                assert_name='format_to_string_func')


def test_fail_init(mock_local_runner: Annotated[MockLocalRunner, pytest.fixture]) -> None:
    with pytest.raises(TypeError):
        FuncFlow()

    with pytest.raises(TypeError):
        FuncFlowTemplate(lambda x: x)(lambda y: y)


def test_apply_run_all_flow_classes(
        mock_local_runner: Annotated[MockLocalRunner, pytest.fixture],
        all_flow_classes: Annotated[Tuple[FlowClsTuple, ...], pytest.fixture]) -> None:
    for class_info in all_flow_classes:
        template_cls = class_info.template_cls
        flow_cls = class_info.flow_cls

        if any(issubclass(template_cls, cls) for cls in (LinearFlowTemplate, DagFlowTemplate)):
            flow_template = template_cls(TaskTemplate(format_to_string_func))(format_to_string_func)
        else:
            flow_template = template_cls(format_to_string_func)

        flow = flow_template.apply()
        assert_flow_or_flow_template(
            flow,
            assert_flow_cls=flow_cls,
            assert_func=format_to_string_func,
            assert_name='format_to_string_func')

        assert flow_template.run('text', number=1) == 'text: 1'
        assert flow('text', number=1) == 'text: 1'

        with pytest.raises(TypeError):
            flow_template.run('text')
            flow('text')


def test_refine_all_flow_classes(
        mock_local_runner: Annotated[MockLocalRunner, pytest.fixture],
        all_flow_classes: Annotated[Tuple[FlowClsTuple, ...], pytest.fixture]) -> None:
    for class_info in all_flow_classes:
        template_cls = class_info.template_cls

        if any(issubclass(template_cls, cls) for cls in (LinearFlowTemplate, DagFlowTemplate)):
            flow_template = template_cls(TaskTemplate(format_to_string_func))(empty_dict_func)
            flow_template_2 = flow_template.refine(
                TaskTemplate(data_import_func), name='data_import')

            assert_flow_or_flow_template(
                flow_template_2,
                assert_flow_cls=template_cls,
                assert_func=empty_dict_func,
                assert_name='data_import')
            assert flow_template_2.run() == '{"my_data": [123,234,345,456]}'
        else:
            flow_template = template_cls(empty_dict_func)
            flow_template_2 = flow_template.refine(name='not_data_import')

            assert_flow_or_flow_template(
                flow_template_2,
                assert_flow_cls=template_cls,
                assert_func=empty_dict_func,
                assert_name='not_data_import')
            assert flow_template_2.run() == {}


def test_revise_all_flow_classes(
        mock_local_runner: Annotated[MockLocalRunner, pytest.fixture],
        all_flow_classes: Annotated[Tuple[FlowClsTuple, ...], pytest.fixture]) -> None:
    for class_info in all_flow_classes:
        template_cls = class_info.template_cls

        if any(issubclass(template_cls, cls) for cls in (LinearFlowTemplate, DagFlowTemplate)):
            flow_template = template_cls(TaskTemplate(format_to_string_func))(format_to_string_func)
        else:
            flow_template = template_cls(format_to_string_func)

        flow = flow_template.apply()
        flow_template_2 = flow.revise()

        assert_flow_or_flow_template(
            flow_template_2,
            assert_flow_cls=template_cls,
            assert_func=format_to_string_func,
            assert_name='format_to_string_func')
        assert flow_template_2.run('text', 1) == 'text: 1'


@pc.parametrize_with_cases('case', cases='.cases.flows')
def test_flow_run_all_flow_classes(mock_local_runner: Annotated[MockLocalRunner, pytest.fixture],
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


def test_time_of_multi_level_flow_run_all_flow_classes(
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

    # FuncFlowTemplate
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
        flow_tmpl: IsFlowTemplate,
        *args: object,
        assert_result: object,
        assert_task_tmpl: MockTaskTemplateAssertSameTimeOfCurFlowRun):
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
