# mypy: disable-error-code="attr-defined"
# pyright: reportAttributeAccessIssue=false
from ....compute.test_decorators import (
    dag_flow_plus_five_number_,
    dag_flow_plus_five_x_,
    func_flow_plus_func_x_y_,
    func_flow_plus_y_number_y_,
    test_dag_flow_template_as_decorator,
    test_dag_flow_template_as_decorator_plus_five_template,
    test_fail_func_flow_template_decorator_with_func_argument,
    test_func_flow_template_as_decorator,
    test_func_flow_template_as_decorator_plus_y_template,
    test_task_template_as_decorator,
)

__all__ = [
    'dag_flow_plus_five_number_',
    'dag_flow_plus_five_x_',
    'func_flow_plus_func_x_y_',
    'func_flow_plus_y_number_y_',
    'test_dag_flow_template_as_decorator',
    'test_dag_flow_template_as_decorator_plus_five_template',
    'test_fail_func_flow_template_decorator_with_func_argument',
    'test_func_flow_template_as_decorator',
    'test_func_flow_template_as_decorator_plus_y_template',
    'test_task_template_as_decorator',
]
