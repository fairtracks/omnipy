"""Job cases for integration novel serialization tests."""

import pytest_cases as pc

from omnipy.compute.flow import LinearFlowTemplate
from omnipy.compute.task import TaskTemplate
from omnipy.shared.protocols.compute.job import IsLinearFlowTemplate, IsTaskTemplate


@pc.case(tags=['task'])
def case_pandas_task_tmpl(pandas_func) -> IsTaskTemplate:
    """Return the pandas task template case."""
    return TaskTemplate()(pandas_func)


@pc.case(tags=['flow'])
def case_pandas_flow_tmpl(pandas_func) -> IsLinearFlowTemplate:
    """Return the pandas flow template case."""
    return LinearFlowTemplate(case_pandas_task_tmpl(pandas_func))(pandas_func)


@pc.case(tags=['task'])
def case_json_table_task_tmpl(json_table_func) -> IsTaskTemplate:
    """Return the jSON table task template case."""
    return TaskTemplate()(json_table_func)


@pc.case(tags=['flow'])
def case_json_table_flow_tmpl(json_table_func) -> IsLinearFlowTemplate:
    """Return the jSON table flow template case."""
    return LinearFlowTemplate(case_json_table_task_tmpl(json_table_func))(json_table_func)


@pc.case(tags=['task'])
def case_json_nested_table_task_tmpl(json_nested_table_func) -> IsTaskTemplate:
    """Return the jSON nested table task template case."""
    return TaskTemplate()(json_nested_table_func)


@pc.case(tags=['flow'])
def case_json_nested_table_flow_tmpl(json_nested_table_func) -> IsLinearFlowTemplate:
    """Return the jSON nested table flow template case."""
    return LinearFlowTemplate(case_json_nested_table_task_tmpl(json_nested_table_func))(
        json_nested_table_func)


@pc.case(tags=['task'])
def case_json_table_as_str_task_tmpl(json_table_as_str_func) -> IsTaskTemplate:
    """Return the jSON table as string task template case."""
    return TaskTemplate()(json_table_as_str_func)


@pc.case(tags=['flow'])
def case_json_table_as_str_flow_tmpl(json_table_as_str_func) -> IsLinearFlowTemplate:
    """Return the jSON table as string flow template case."""
    return LinearFlowTemplate(case_json_table_as_str_task_tmpl(json_table_as_str_func))(
        json_table_as_str_func)


@pc.case(tags=['task'])
def case_config_json_task_tmpl(json_func) -> IsTaskTemplate:
    """Return the config JSON task template case."""
    return TaskTemplate()(json_func)


@pc.case(tags=['flow'])
def case_config_json_flow_tmpl(json_func) -> IsLinearFlowTemplate:
    """Return the config JSON flow template case."""
    return LinearFlowTemplate(case_config_json_task_tmpl(json_func))(json_func)


@pc.case(tags=['task'])
def case_json_str_task_tmpl(json_str_func) -> IsTaskTemplate:
    """Return the jSON string task template case."""
    return TaskTemplate()(json_str_func)


@pc.case(tags=['flow'])
def case_json_str_flow_tmpl(json_str_func) -> IsLinearFlowTemplate:
    """Return the jSON string flow template case."""
    return LinearFlowTemplate(case_json_str_task_tmpl(json_str_func))(json_str_func)


@pc.case(tags=['task'])
def case_csv_task_tmpl(csv_func) -> IsTaskTemplate:
    """Return the cSV task template case."""
    return TaskTemplate()(csv_func)


@pc.case(tags=['flow'])
def case_csv_flow_tmpl(csv_func) -> IsLinearFlowTemplate:
    """Return the cSV flow template case."""
    return LinearFlowTemplate(case_csv_task_tmpl(csv_func))(csv_func)


@pc.case(tags=['task'])
def case_str_task_tmpl(str_func) -> IsTaskTemplate:
    """Return the string task template case."""
    return TaskTemplate()(str_func)


@pc.case(tags=['flow'])
def case_str_flow_tmpl(str_func) -> IsLinearFlowTemplate:
    """Return the string flow template case."""
    return LinearFlowTemplate(case_str_task_tmpl(str_func))(str_func)


@pc.case(tags=['task'])
def case_str_unicode_task_tmpl(str_unicode_func) -> IsTaskTemplate:
    """Return the string unicode task template case."""
    return TaskTemplate()(str_unicode_func)


@pc.case(tags=['flow'])
def case_str_unicode_flow_tmpl(str_unicode_func) -> IsLinearFlowTemplate:
    """Return the string unicode flow template case."""
    return LinearFlowTemplate(case_str_unicode_task_tmpl(str_unicode_func))(str_unicode_func)


@pc.case(tags=['task'])
def fail_case_python_task_tmpl(python_func) -> IsTaskTemplate:
    """Return the fail case python task template case."""
    return TaskTemplate()(python_func)


@pc.case(tags=['flow'])
def fail_case_python_flow_tmpl(python_func) -> IsLinearFlowTemplate:
    """Return the fail case python flow template case."""
    return LinearFlowTemplate(fail_case_python_task_tmpl(python_func))(python_func)
