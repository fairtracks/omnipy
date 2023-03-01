import pytest_cases as pc

from omnipy.compute.flow import DagFlowTemplate, FuncFlowTemplate, LinearFlowTemplate
from omnipy.compute.task import TaskTemplate


@pc.case(
    id='task-plus_one(number)',
    tags=['sync', 'function', 'task', 'plain'],
)
def case_task_plus_one_template() -> TaskTemplate:
    @TaskTemplate
    def plus_one(number: int) -> int:
        return number + 1

    return plus_one  # noqa  # Pycharm static type checker bug


@pc.case(
    id='task-plus_other(number, other=1)',
    tags=['sync', 'function', 'task', 'with_kw_params'],
)
def case_task_plus_other_as_plus_one_template() -> TaskTemplate:
    @TaskTemplate(
        name='plus_one',
        fixed_params=dict(other=1),
    )
    def plus_other(number: int, other: int) -> int:
        return number + other

    return plus_other  # noqa  # Pycharm static type checker bug


@pc.case(
    id='linear_flow-plus_five(number)',
    tags=['sync', 'function', 'linear_flow', 'plain'],
)
@pc.parametrize_with_cases('plus_one_template', cases='.', has_tag='task')
def case_linear_flow_number_plus_five_template(plus_one_template) -> LinearFlowTemplate:
    @LinearFlowTemplate(*((plus_one_template,) * 5))
    def plus_five(number: int) -> int:  # noqa
        ...

    return plus_five  # noqa  # Pycharm static type checker bug


@pc.case(
    id='linear_flow-plus_five(x)',
    tags=['sync', 'function', 'linear_flow', 'with_kw_params'],
)
@pc.parametrize_with_cases('plus_one_template', cases='.', has_tag='task')
def case_linear_flow_x_plus_five_template(plus_one_template) -> FuncFlowTemplate:
    iterative_x_plus_one_template = plus_one_template.refine(param_key_map=dict(number='x'),)

    @LinearFlowTemplate(*((iterative_x_plus_one_template,) * 5))
    def plus_five(x: int) -> int:  # noqa
        ...

    return plus_five  # noqa  # Pycharm static type checker bug


@pc.case(
    id='dag_flow-plus_five(number)',
    tags=['sync', 'function', 'dag_flow', 'plain'],
)
@pc.parametrize_with_cases('plus_one_template', cases='.', has_tag='task')
def case_dag_flow_number_plus_five_template(plus_one_template) -> DagFlowTemplate:

    iterative_number_plus_one_template = plus_one_template.refine(result_key='number')

    @DagFlowTemplate(*((iterative_number_plus_one_template,) * 5))
    def plus_five(number: int) -> int:  # noqa
        ...

    return plus_five  # noqa  # Pycharm static type checker bug


@pc.case(
    id='dag_flow-plus_five(x)',
    tags=['sync', 'function', 'dag_flow', 'with_kw_params'],
)
@pc.parametrize_with_cases('plus_one_template', cases='.', has_tag='task')
def case_dag_flow_x_plus_five_template(plus_one_template) -> FuncFlowTemplate:
    # TDDD: Expand on this example with param_key_map and result_key, given these
    #       are reimplemented as mixins

    iterative_x_plus_one_template = plus_one_template.refine(
        param_key_map=dict(number='x'),
        result_key='x',
    )

    @DagFlowTemplate(*((iterative_x_plus_one_template,) * 5))
    def plus_five(x: int) -> int:  # noqa
        ...

    return plus_five  # noqa  # Pycharm static type checker bug


@pc.case(
    id='func_flow-plus_y(number, y)',
    tags=['sync', 'function', 'func_flow', 'plain'],
)
@pc.parametrize_with_cases('plus_one_template', cases='.', has_tag='task')
def case_func_flow_plus_y_template(plus_one_template) -> FuncFlowTemplate:
    @FuncFlowTemplate
    def plus_y(number: int, y: int) -> int:
        for _ in range(y):
            number = plus_one_template(number=number)
        return number

    return plus_y  # noqa  # Pycharm static type checker bug


@pc.case(
    id='func_flow-plus_func(x, y)',
    tags=['sync', 'function', 'func_flow', 'with_kw_params'],
)
@pc.parametrize_with_cases('plus_one_template', cases='.', has_tag='task')
def case_func_flow_plus_function_as_plus_y_template(plus_one_template) -> FuncFlowTemplate:
    # TDDD: Expand on this example with param_key_map and result_key, given these
    #       are reimplemented as mixins

    @FuncFlowTemplate(name='plus_y')
    def plus_function(x: int, y: int) -> int:
        for _ in range(y):
            x = plus_one_template(number=x)
        return x

    return plus_function  # noqa  # Pycharm static type checker bug
