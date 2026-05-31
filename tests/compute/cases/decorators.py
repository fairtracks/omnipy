"""Provide decorator-based compute test cases."""

import pytest_cases as pc

from omnipy.compute.flow import DagFlowTemplate, FuncFlowTemplate, LinearFlowTemplate
from omnipy.compute.task import TaskTemplate
from omnipy.shared.protocols.compute.job import (IsDagFlowTemplate,
                                                 IsFuncFlowTemplate,
                                                 IsLinearFlowTemplate,
                                                 IsTaskTemplate)


@pc.case(
    id='task-plus_one(number)',
    tags=['sync', 'function', 'task', 'plain'],
)
def case_task_plus_one_template() -> IsTaskTemplate:
    """Provide a plain plus-one task template."""
    @TaskTemplate()
    def plus_one(number: int) -> int:
        return number + 1

    return plus_one


@pc.case(
    id='task-plus_other(number, other=1)',
    tags=['sync', 'function', 'task', 'with_kw_params'],
)
def case_task_plus_other_as_plus_one_template() -> IsTaskTemplate:
    """Provide a renamed plus-one task template with fixed params."""
    @TaskTemplate(
        name='plus_one',
        fixed_params=dict(other=1),
    )
    def plus_other(number: int, other: int) -> int:
        return number + other

    return plus_other


@pc.case(
    id='linear_flow-plus_five(number)',
    tags=['sync', 'function', 'linear_flow', 'plain'],
)
@pc.parametrize_with_cases('plus_one_template', cases='.', has_tag='task')
def case_linear_flow_number_plus_five_template(plus_one_template) -> IsLinearFlowTemplate:
    """Provide a linear flow template that adds five."""
    @LinearFlowTemplate(*((plus_one_template,) * 5))
    def plus_five(number: int) -> int:
        ...

    return plus_five


@pc.case(
    id='linear_flow-plus_five(x)',
    tags=['sync', 'function', 'linear_flow', 'with_kw_params'],
)
@pc.parametrize_with_cases('plus_one_template', cases='.', has_tag='task')
def case_linear_flow_x_plus_five_template(plus_one_template) -> IsLinearFlowTemplate:
    """Provide an x-based linear flow template that adds five."""
    iterative_x_plus_one_template = plus_one_template.refine(param_key_map=dict(number='x'),)

    @LinearFlowTemplate(*((iterative_x_plus_one_template,) * 5))
    def plus_five(x: int) -> int:
        ...

    return plus_five


@pc.case(
    id='dag_flow-plus_five(number)',
    tags=['sync', 'function', 'dag_flow', 'plain'],
)
@pc.parametrize_with_cases('plus_one_template', cases='.', has_tag='task')
def case_dag_flow_number_plus_five_template(plus_one_template) -> IsDagFlowTemplate:
    """Provide a DAG flow template that adds five."""

    iterative_number_plus_one_template = plus_one_template.refine(result_key='number')

    @DagFlowTemplate(*((iterative_number_plus_one_template,) * 5))
    def plus_five(number: int) -> int:
        ...

    return plus_five


@pc.case(
    id='dag_flow-plus_five(x)',
    tags=['sync', 'function', 'dag_flow', 'with_kw_params'],
)
@pc.parametrize_with_cases('plus_one_template', cases='.', has_tag='task')
def case_dag_flow_x_plus_five_template(plus_one_template) -> IsDagFlowTemplate:
    """Provide an x-based DAG flow template that adds five."""
    # TODO: Expand on this example with param_key_map and result_key, given these
    #       are reimplemented as mixins

    iterative_x_plus_one_template = plus_one_template.refine(
        param_key_map=dict(number='x'),
        result_key='x',
    )

    @DagFlowTemplate(*((iterative_x_plus_one_template,) * 5))
    def plus_five(x: int) -> int:
        ...

    return plus_five


@pc.case(
    id='func_flow-plus_y(number, y)',
    tags=['sync', 'function', 'func_flow', 'plain'],
)
@pc.parametrize_with_cases('plus_one_template', cases='.', has_tag='task')
def case_func_flow_plus_y_template(plus_one_template) -> IsFuncFlowTemplate:
    """Provide a function flow template that adds y."""
    @FuncFlowTemplate()
    def plus_y(number: int, y: int) -> int:
        for _ in range(y):
            number = plus_one_template(number=number)
        return number

    return plus_y


@pc.case(
    id='func_flow-plus_func(x, y)',
    tags=['sync', 'function', 'func_flow', 'with_kw_params'],
)
@pc.parametrize_with_cases('plus_one_template', cases='.', has_tag='task')
def case_func_flow_plus_function_as_plus_y_template(plus_one_template) -> IsFuncFlowTemplate:
    """Provide a renamed function flow template that adds y."""
    # TODO: Expand on this example with param_key_map and result_key, given these
    #       are reimplemented as mixins

    @FuncFlowTemplate(name='plus_y')
    def plus_function(x: int, y: int) -> int:
        for _ in range(y):
            x = plus_one_template(number=x)
        return x

    return plus_function
