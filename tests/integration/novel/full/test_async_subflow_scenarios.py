import asyncio
from inspect import isawaitable, Parameter
from typing import Annotated, cast

import pytest
import pytest_cases as pc

from omnipy.shared.enums.job import RunState
from omnipy.shared.protocols.compute.job import IsAnyFlowTemplate, IsDagFlow, IsDagFlowTemplate
from omnipy.util.callable_types import CallableType
from omnipy.util.helpers import resolve

from ....engine.helpers.functions import assert_job_state
from .cases.flows import FlowCase


def _as_flow_template(flow_template: object) -> IsAnyFlowTemplate:
    return cast(IsAnyFlowTemplate, flow_template)


def _resolve_sync_or_async(result: object) -> object:
    if isawaitable(result):
        return asyncio.run(resolve(result))
    return result


def _normalized_scenario_result(result: object, result_key: str) -> dict[str, object]:
    resolved_result = _resolve_sync_or_async(result)
    if isinstance(resolved_result, dict):
        return cast(dict[str, object], resolved_result)
    return {result_key: resolved_result}


@pc.parametrize_with_cases('case', cases='.cases.flows', has_tag='async_subflow_scenario')
def test_async_subflow_scenario_signatures_and_callable_types(
    runtime_all_engines: Annotated[None, pytest.fixture],  # noqa
    case: FlowCase,
) -> None:
    flow_template = _as_flow_template(case.flow_template)
    for flow_obj in flow_template, flow_template.apply():
        if case.name == 'async_io_pipeline':
            assert flow_obj.param_signatures == {
                'seed': Parameter('seed', Parameter.POSITIONAL_OR_KEYWORD, annotation=int),
            }
            assert flow_obj.return_type == str
            assert flow_obj.callable_type is CallableType.ASYNC_COROUTINE
        elif case.name == 'nested_subflow_composition':
            assert flow_obj.param_signatures == {
                'text': Parameter('text', Parameter.POSITIONAL_OR_KEYWORD, annotation=str),
                'left': Parameter('left', Parameter.POSITIONAL_OR_KEYWORD, annotation=str),
                'right': Parameter('right', Parameter.POSITIONAL_OR_KEYWORD, annotation=str),
            }
            assert flow_obj.return_type == str
            assert flow_obj.callable_type is CallableType.SYNC_FUNCTION
        elif case.name == 'subflow_replacement':
            assert flow_obj.param_signatures == {
                'text': Parameter('text', Parameter.POSITIONAL_OR_KEYWORD, annotation=str),
                'left': Parameter('left', Parameter.POSITIONAL_OR_KEYWORD, annotation=str),
                'right': Parameter('right', Parameter.POSITIONAL_OR_KEYWORD, annotation=str),
            }
            assert flow_obj.return_type == str
            assert flow_obj.callable_type is CallableType.SYNC_FUNCTION
        else:
            raise AssertionError(f'Unexpected scenario case: {case.name}')


@pc.parametrize_with_cases(
    'case',
    cases='.cases.flows',
    has_tag='async_subflow_scenario',
    prefix='case_async_io_pipeline_',
)
def test_async_io_pipeline_run_and_apply(
    runtime_all_engines: Annotated[None, pytest.fixture],  # noqa
    case: FlowCase,
) -> None:
    async_io_pipeline = _as_flow_template(case.flow_template)

    assert _normalized_scenario_result(async_io_pipeline.run(4), 'async_io_pipeline') == {
        'async_io_pipeline': 'remote:18'
    }

    async_io_pipeline_job = async_io_pipeline.apply()

    assert _normalized_scenario_result(async_io_pipeline_job(5), 'async_io_pipeline') == {
        'async_io_pipeline': 'remote:20'
    }
    assert async_io_pipeline.name == async_io_pipeline_job.name == 'async_io_pipeline'
    assert_job_state(async_io_pipeline_job, [RunState.FINISHED])


@pc.parametrize_with_cases(
    'case',
    cases='.cases.flows',
    has_tag='async_subflow_scenario',
    prefix='case_nested_subflow_composition_',
)
def test_nested_subflow_composition_template_refine(
    runtime_all_engines: Annotated[None, pytest.fixture],  # noqa
    case: FlowCase,
) -> None:
    nested_subflow = cast(IsDagFlowTemplate, case.flow_template)

    refined_child = nested_subflow.child_job_templates[0].refine(
        fixed_params=dict(label='vip-'),
        result_key='formatted',
    )

    refined_nested_subflow = nested_subflow.refine(
        refined_child,
        nested_subflow.child_job_templates[1],
        update=False,
        name='nested_subflow_composition',
        result_key='nested_subflow_composition',
    )

    assert refined_nested_subflow.run('  Hi  ', '[', ']') == {
        'nested_subflow_composition': '[vip-hi]'
    }

    refined_nested_subflow_job = refined_nested_subflow.apply()

    assert refined_nested_subflow_job('  OmniPy  ', '<', '>') == {
        'nested_subflow_composition': '<vip-omnipy>'
    }


@pc.parametrize_with_cases(
    'case',
    cases='.cases.flows',
    has_tag='async_subflow_scenario',
    prefix='case_subflow_replacement_',
)
def test_subflow_replacement_via_revise_refine(
    runtime_all_engines: Annotated[None, pytest.fixture],  # noqa
    case: FlowCase,
) -> None:
    subflow_replacement = cast(IsDagFlowTemplate, case.flow_template)

    initial_result = subflow_replacement.run('  hi  ', '[', ']')
    assert initial_result == {'subflow_replacement': '[base-hi]'}

    dag_job = cast(IsDagFlow, subflow_replacement.apply())
    revised_child_templates = list(dag_job.child_job_templates)
    revised_child_templates[0] = revised_child_templates[0].refine(
        fixed_params=dict(label='vip-'),
        result_key='formatted',
    )

    replaced_subflow_job = dag_job.revise().refine(*revised_child_templates, update=False).apply()

    replaced_result = replaced_subflow_job('  hi  ', '[', ']')

    assert replaced_result == '[vip-hi]'
    assert replaced_result != initial_result['subflow_replacement']
