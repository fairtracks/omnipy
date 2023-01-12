from typing import Annotated

import pytest

from compute.mixins.cases.raw.functions import json_func
from omnipy.compute.flow import LinearFlowTemplate
from omnipy.compute.task import TaskTemplate


@pytest.fixture(scope='function')
def json_task_tmpl() -> TaskTemplate:
    return TaskTemplate()(json_func)


@pytest.fixture(scope='function')
def json_flow_tmpl(json_task_tmpl: Annotated[TaskTemplate, pytest.fixture]) -> LinearFlowTemplate:
    return LinearFlowTemplate(json_task_tmpl)(json_func)
