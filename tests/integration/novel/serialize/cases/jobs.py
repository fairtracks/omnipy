import pytest_cases as pc

from omnipy.compute.flow import LinearFlowTemplate
from omnipy.compute.task import TaskTemplate
from omnipy.shared.protocols.compute.job import IsLinearFlowTemplate, IsTaskTemplate


@pc.case(tags=['task'])
def case_pandas_task_tmpl(pandas_func) -> IsTaskTemplate:
    return TaskTemplate()(pandas_func)


@pc.case(tags=['flow'])
def case_pandas_flow_tmpl(pandas_func) -> IsLinearFlowTemplate:
    return LinearFlowTemplate(case_pandas_task_tmpl(pandas_func))(pandas_func)


@pc.case(tags=['task'])
def case_json_table_task_tmpl(json_table_func) -> IsTaskTemplate:
    return TaskTemplate()(json_table_func)


@pc.case(tags=['flow'])
def case_json_table_flow_tmpl(json_table_func) -> IsLinearFlowTemplate:
    return LinearFlowTemplate(case_json_table_task_tmpl(json_table_func))(json_table_func)


@pc.case(tags=['task'])
def case_json_nested_table_task_tmpl(json_nested_table_func) -> IsTaskTemplate:
    return TaskTemplate()(json_nested_table_func)


@pc.case(tags=['flow'])
def case_json_nested_table_flow_tmpl(json_nested_table_func) -> IsLinearFlowTemplate:
    return LinearFlowTemplate(case_json_nested_table_task_tmpl(json_nested_table_func))(
        json_nested_table_func)


@pc.case(tags=['task'])
def case_json_table_as_str_task_tmpl(json_table_as_str_func) -> IsTaskTemplate:
    return TaskTemplate()(json_table_as_str_func)


@pc.case(tags=['flow'])
def case_json_table_as_str_flow_tmpl(json_table_as_str_func) -> IsLinearFlowTemplate:
    return LinearFlowTemplate(case_json_table_as_str_task_tmpl(json_table_as_str_func))(
        json_table_as_str_func)


@pc.case(tags=['task'])
def case_config_json_task_tmpl(json_func) -> IsTaskTemplate:
    return TaskTemplate()(json_func)


@pc.case(tags=['flow'])
def case_config_json_flow_tmpl(json_func) -> IsLinearFlowTemplate:
    return LinearFlowTemplate(case_config_json_task_tmpl(json_func))(json_func)


@pc.case(tags=['task'])
def case_json_str_task_tmpl(json_str_func) -> IsTaskTemplate:
    return TaskTemplate()(json_str_func)


@pc.case(tags=['flow'])
def case_json_str_flow_tmpl(json_str_func) -> IsLinearFlowTemplate:
    return LinearFlowTemplate(case_json_str_task_tmpl(json_str_func))(json_str_func)


@pc.case(tags=['task'])
def case_csv_task_tmpl(csv_func) -> IsTaskTemplate:
    return TaskTemplate()(csv_func)


@pc.case(tags=['flow'])
def case_csv_flow_tmpl(csv_func) -> IsLinearFlowTemplate:
    return LinearFlowTemplate(case_csv_task_tmpl(csv_func))(csv_func)


@pc.case(tags=['task'])
def case_str_task_tmpl(str_func) -> IsTaskTemplate:
    return TaskTemplate()(str_func)


@pc.case(tags=['flow'])
def case_str_flow_tmpl(str_func) -> IsLinearFlowTemplate:
    return LinearFlowTemplate(case_str_task_tmpl(str_func))(str_func)


@pc.case(tags=['task'])
def case_str_unicode_task_tmpl(str_unicode_func) -> IsTaskTemplate:
    return TaskTemplate()(str_unicode_func)


@pc.case(tags=['flow'])
def case_str_unicode_flow_tmpl(str_unicode_func) -> IsLinearFlowTemplate:
    return LinearFlowTemplate(case_str_unicode_task_tmpl(str_unicode_func))(str_unicode_func)


@pc.case(tags=['task'])
def fail_case_python_task_tmpl(python_func) -> IsTaskTemplate:
    return TaskTemplate()(python_func)


@pc.case(tags=['flow'])
def fail_case_python_flow_tmpl(python_func) -> IsLinearFlowTemplate:
    return LinearFlowTemplate(fail_case_python_task_tmpl(python_func))(python_func)
