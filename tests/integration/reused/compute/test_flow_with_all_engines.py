# mypy: disable-error-code="attr-defined"
# pyright: reportAttributeAccessIssue=false
"""Tests for flow with all engines."""

from ....compute.test_flow import (
    sync_dagflow_single_task,
    sync_funcflow_single_task,
    sync_linearflow_single_task,
    test_dag_flow_ignore_args_and_non_matched_kwarg_returns,
    test_dynamic_dag_flow_by_returned_dict,
    test_fail_init_flow_cls_tuple,
    test_fail_init_func_arg_flow_classes,
    test_flow_context_mock,
    test_flow_run_flow_cls_tuple,
    test_flow_run_flow_cls_tuple_case,
    test_init_child_job_list_arg_flow_templates,
    test_init_func_arg_flow_templates,
    test_linear_flow_only_first_positional,
    test_time_of_flow_run_mock,
    test_time_of_multi_level_flow_run_flow_cls_tuple,
)

__all__ = [
    'sync_dagflow_single_task',
    'sync_funcflow_single_task',
    'sync_linearflow_single_task',
    'test_dag_flow_ignore_args_and_non_matched_kwarg_returns',
    'test_dynamic_dag_flow_by_returned_dict',
    'test_fail_init_flow_cls_tuple',
    'test_fail_init_func_arg_flow_classes',
    'test_flow_context_mock',
    'test_flow_run_flow_cls_tuple',
    'test_flow_run_flow_cls_tuple_case',
    'test_init_child_job_list_arg_flow_templates',
    'test_init_func_arg_flow_templates',
    'test_linear_flow_only_first_positional',
    'test_time_of_flow_run_mock',
    'test_time_of_multi_level_flow_run_flow_cls_tuple',
]
