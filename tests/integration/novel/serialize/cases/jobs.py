import pytest_cases as pc

from omnipy.compute.flow import LinearFlowTemplate
from omnipy.compute.task import TaskTemplate

from .functions import (csv_func,
                        json_func,
                        json_str_func,
                        json_table_func,
                        pandas_func,
                        python_func,
                        str_func)


@pc.case(tags=['task'])
def case_pandas_task_tmpl() -> TaskTemplate:
    return TaskTemplate()(pandas_func)


@pc.case(tags=['flow'])
def case_pandas_flow_tmpl() -> LinearFlowTemplate:
    return LinearFlowTemplate(case_pandas_task_tmpl())(pandas_func)


@pc.case(tags=['task'])
def case_json_table_task_tmpl() -> TaskTemplate:
    return TaskTemplate()(json_table_func)


@pc.case(tags=['flow'])
def case_json_table_flow_tmpl() -> LinearFlowTemplate:
    return LinearFlowTemplate(case_json_table_task_tmpl())(json_table_func)


@pc.case(tags=['task'])
def case_config_json_task_tmpl() -> TaskTemplate:
    return TaskTemplate()(json_func)


@pc.case(tags=['flow'])
def case_config_json_flow_tmpl() -> LinearFlowTemplate:
    return LinearFlowTemplate(case_config_json_task_tmpl())(json_func)


@pc.case(tags=['task'])
def case_json_str_task_tmpl() -> TaskTemplate:
    return TaskTemplate()(json_str_func)


@pc.case(tags=['flow'])
def case_json_str_flow_tmpl() -> LinearFlowTemplate:
    return LinearFlowTemplate(case_json_str_task_tmpl())(json_str_func)


@pc.case(tags=['task'])
def case_csv_task_tmpl() -> TaskTemplate:
    return TaskTemplate()(csv_func)


@pc.case(tags=['flow'])
def case_csv_flow_tmpl() -> LinearFlowTemplate:
    return LinearFlowTemplate(case_csv_task_tmpl())(csv_func)


@pc.case(tags=['task'])
def case_str_task_tmpl() -> TaskTemplate:
    return TaskTemplate()(str_func)


@pc.case(tags=['flow'])
def case_str_flow_tmpl() -> LinearFlowTemplate:
    return LinearFlowTemplate(case_str_task_tmpl())(str_func)


@pc.case(tags=['task'])
def fail_case_python_task_tmpl() -> TaskTemplate:
    return TaskTemplate()(python_func)


@pc.case(tags=['flow'])
def fail_case_python_flow_tmpl() -> LinearFlowTemplate:
    return LinearFlowTemplate(fail_case_python_task_tmpl())(python_func)
