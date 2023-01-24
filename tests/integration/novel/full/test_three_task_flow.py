from inspect import Parameter
from typing import Annotated

import pytest
import pytest_cases as pc

from omnipy.abstract.enums import RunState

from ....engine.helpers.functions import assert_job_state
from .cases.flows import FlowCase


@pc.parametrize_with_cases('case', cases='.cases.flows', has_tag='pos_square_root')
def test_specialize_record_models_signature_and_return_type_func(
        runtime_all_engines: Annotated[None, pytest.fixture],  # noqa
        case: FlowCase):
    for flow_obj in case.flow_template, case.flow_template.apply():
        assert flow_obj.param_signatures == {
            'number': Parameter('number', Parameter.POSITIONAL_OR_KEYWORD, annotation=int),
            'text': Parameter('text', Parameter.POSITIONAL_OR_KEYWORD, annotation=str),
        }
        assert flow_obj.return_type == str


@pc.parametrize_with_cases('case', cases='.cases.flows', has_tag='pos_square_root')
def test_run_three_task_flow(
        runtime_all_engines: Annotated[None, pytest.fixture],  # noqa
        case: FlowCase):
    pos_square_root_tmpl = case.flow_template
    assert pos_square_root_tmpl.run(4, 'result') == {'pos_square_root': 'RESULT: 2.0'}

    pos_square_root = pos_square_root_tmpl.apply()

    assert pos_square_root(number=9, text='answer') == {'pos_square_root': 'ANSWER: 3.0'}
    assert pos_square_root_tmpl.name == pos_square_root.name == 'pos_square_root'
    assert_job_state(pos_square_root, [RunState.FINISHED])


@pc.parametrize_with_cases('case', cases='.cases.flows', has_tag='pos_square_root')
def test_refine_three_task_flow(
        runtime_all_engines: Annotated[None, pytest.fixture],  # noqa
        case: FlowCase):

    pos_square_root_tmpl = case.flow_template.refine(
        name='pos_sqrt',
        fixed_params=dict(text='='),
        result_key='+√',
    )

    assert pos_square_root_tmpl.run(4) == {'+√': '=: 2.0'}

    pos_square_root = pos_square_root_tmpl.apply()

    assert pos_square_root(number=9) == {'+√': '=: 3.0'}
    assert pos_square_root_tmpl.name == pos_square_root.name == 'pos_sqrt'

    with pytest.raises(TypeError):
        pos_square_root_tmpl.run()

    with pytest.raises(TypeError):
        pos_square_root_tmpl.run(4, 'answer')


@pc.parametrize_with_cases('case', cases='.cases.flows', has_tag='pos_square_root')
def test_revise_refine_three_task_flow(
        runtime_all_engines: Annotated[None, pytest.fixture],  # noqa
        case: FlowCase):

    pos_square_root = case.flow_template.refine(
        name='pos_sqrt',
        fixed_params=dict(text='='),
        result_key='+√',
    ).apply()

    pos_square_root_new = pos_square_root.revise().refine(
        fixed_params=dict(text='answer'),
        result_key='Positive square root',
    ).apply()

    assert pos_square_root_new(4) == {'Positive square root': 'ANSWER: 2.0'}
    assert pos_square_root_new.name == 'pos_sqrt'


@pc.parametrize_with_cases(
    'case', cases='.cases.flows', prefix='case_sync_dagflow_', has_tag='pos_square_root')
def test_revise_refine_three_task_dagflow_alternative(
        runtime_all_engines: Annotated[None, pytest.fixture],  # noqa
        case: FlowCase):

    pos_square_root = case.flow_template.refine(
        name='pos_sqrt',
        fixed_params=dict(text='='),
        result_key='+√',
    ).apply()

    task_tmpls = list(pos_square_root.task_templates)
    task_tmpls[-1] = task_tmpls[-1].refine(result_key='Positive square root')
    pos_square_root_new = pos_square_root.revise().refine(
        *task_tmpls,
        update=False,
        name='pos_sqrt',
        fixed_params={
            'text': 'answer'
        },
    ).apply()

    assert pos_square_root_new(4) == {'Positive square root': 'ANSWER: 2.0'}
    assert pos_square_root_new.name == 'pos_sqrt'
