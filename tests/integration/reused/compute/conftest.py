import pytest

from omnipy.compute.task import TaskTemplate

from ....compute.conftest import dag_flow_cls_tuple  # noqa
from ....compute.conftest import flow_cls_tuple  # noqa
from ....compute.conftest import flow_cls_tuple__flow_cls_tuple  # type: ignore[attr-defined] # noqa
from ....compute.conftest import func_arg_flow_cls_tuple  # noqa
from ....compute.conftest import func_arg_flow_cls_tuple_flow_cls_tuple  # type: ignore # noqa
from ....compute.conftest import func_flow_cls_tuple  # noqa
from ....compute.conftest import linear_flow_cls_tuple  # noqa
from ....compute.conftest import task_tmpl_arg_flow_cls_tuple  # noqa
from ....compute.conftest import task_tmpl_arg_flow_cls_tuple_flow_cls_tuple  # type: ignore # noqa


@pytest.fixture
def mock_local_runner(runtime_all_engines):
    return TaskTemplate.engine
