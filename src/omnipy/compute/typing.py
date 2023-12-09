from typing import cast

from omnipy.api.protocols.public.compute import (IsDagFlowTemplate,
                                                 IsFuncFlowTemplate,
                                                 IsLinearFlowTemplate,
                                                 IsTaskTemplate)

# Needed due to lack of support for class decorators in mypy.
# See: https://github.com/python/mypy/issues/3135


def mypy_fix_task_template(task_template: object) -> 'IsTaskTemplate':
    return cast('IsTaskTemplate', task_template)


def mypy_fix_linear_flow_template(linear_flow_template: object) -> 'IsLinearFlowTemplate':
    return cast('IsLinearFlowTemplate', linear_flow_template)


def mypy_fix_dag_flow_template(dag_flow_template: object) -> 'IsDagFlowTemplate':
    return cast('IsDagFlowTemplate', dag_flow_template)


def mypy_fix_func_flow_template(func_flow_template: object) -> 'IsFuncFlowTemplate':
    return cast('IsFuncFlowTemplate', func_flow_template)
