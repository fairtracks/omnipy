# mypy: disable-error-code="attr-defined"
# pyright: reportAttributeAccessIssue=false
"""Shared fixtures for integration reused compute tests."""

import pytest

from omnipy.compute.task import TaskTemplateCore

from ....compute.conftest import (
    child_job_list_arg_flow_cls_tuple,
    child_job_list_arg_flow_cls_tuple_flow_cls_tuple,
    dag_flow_cls_tuple,
    flow_cls_tuple,
    flow_cls_tuple__flow_cls_tuple,
    func_arg_flow_cls_tuple,
    func_arg_flow_cls_tuple_flow_cls_tuple,
    func_flow_cls_tuple,
    linear_flow_cls_tuple,
)

__all__ = [
    'child_job_list_arg_flow_cls_tuple',
    'child_job_list_arg_flow_cls_tuple_flow_cls_tuple',
    'dag_flow_cls_tuple',
    'flow_cls_tuple',
    'flow_cls_tuple__flow_cls_tuple',
    'func_arg_flow_cls_tuple',
    'func_arg_flow_cls_tuple_flow_cls_tuple',
    'func_flow_cls_tuple',
    'linear_flow_cls_tuple',
]


@pytest.fixture
def mock_local_runner(runtime_all_engines):
    """Provide mock local runner."""
    return TaskTemplateCore.engine
