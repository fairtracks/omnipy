"""Shared fixtures for integration reused compute tests."""

import pytest

from omnipy.compute.task import TaskTemplateCore

from ....compute.conftest import (
    child_job_list_arg_flow_cls_tuple,  # noqa
    child_job_list_arg_flow_cls_tuple_flow_cls_tuple,  # type: ignore # noqa
    dag_flow_cls_tuple,  # noqa
    flow_cls_tuple,  # noqa
    flow_cls_tuple__flow_cls_tuple,  # type: ignore[attr-defined] # noqa
    func_arg_flow_cls_tuple,  # noqa
    func_arg_flow_cls_tuple_flow_cls_tuple,  # type: ignore # noqa
    func_flow_cls_tuple,  # noqa
    linear_flow_cls_tuple,  # noqa
)


@pytest.fixture
def mock_local_runner(runtime_all_engines):
    """Provide mock local runner."""
    return TaskTemplateCore.engine
