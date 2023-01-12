from typing import Annotated, Type

import pytest

from omnipy.compute.flow import LinearFlowTemplate
from omnipy.compute.mixins.serialize import PersistOutputsOptions, RestoreOutputsOptions
from omnipy.compute.task import TaskTemplate
from omnipy.config.job import ConfigPersistOutputsOptions, ConfigRestoreOutputsOptions, JobConfig
from omnipy.engine.protocols import IsRuntime

from .cases.raw.functions import json_func


@pytest.fixture(scope='function')
def json_task_tmpl() -> TaskTemplate:
    return TaskTemplate()(json_func)


@pytest.fixture(scope='function')
def json_flow_tmpl(json_task_tmpl: Annotated[TaskTemplate, pytest.fixture]) -> LinearFlowTemplate:
    return LinearFlowTemplate(json_task_tmpl)(json_func)


def test_all_properties_pytest_default_config(
    json_task_tmpl: Annotated[TaskTemplate, pytest.fixture],) -> None:

    for job_obj in json_task_tmpl, json_task_tmpl.apply():
        assert job_obj.persist_outputs is None
        assert job_obj.will_persist_outputs is PersistOutputsOptions.DISABLED
        assert job_obj.restore_outputs is None
        assert job_obj.will_restore_outputs is RestoreOutputsOptions.DISABLED


def test_all_properties_runtime_default_config(
    runtime: Annotated[IsRuntime, pytest.fixture],
    json_task_tmpl: Annotated[TaskTemplate, pytest.fixture],
    json_flow_tmpl: Annotated[LinearFlowTemplate, pytest.fixture],
) -> None:

    assert runtime.config.job.persist_outputs == \
           ConfigPersistOutputsOptions.ENABLE_FLOW_AND_TASK_OUTPUTS
    assert runtime.config.job.restore_outputs == ConfigRestoreOutputsOptions.DISABLED

    for job_obj in json_task_tmpl, json_task_tmpl.apply(), json_flow_tmpl, json_flow_tmpl.apply():
        assert job_obj.persist_outputs is PersistOutputsOptions.FOLLOW_CONFIG
        assert job_obj.will_persist_outputs is PersistOutputsOptions.ENABLED

        assert job_obj.restore_outputs is RestoreOutputsOptions.FOLLOW_CONFIG
        assert job_obj.will_restore_outputs is RestoreOutputsOptions.DISABLED


def test_properties_persist_outputs_enable_disable(
    runtime: Annotated[IsRuntime, pytest.fixture],
    json_task_tmpl: Annotated[TaskTemplate, pytest.fixture],
    json_flow_tmpl: Annotated[LinearFlowTemplate, pytest.fixture],
) -> None:

    runtime.config.job.persist_outputs = ConfigPersistOutputsOptions.ENABLE_FLOW_OUTPUTS
    assert TaskTemplate.config.persist_outputs == ConfigPersistOutputsOptions.ENABLE_FLOW_OUTPUTS

    for job_obj in json_task_tmpl, json_task_tmpl.apply():
        assert job_obj.persist_outputs is PersistOutputsOptions.FOLLOW_CONFIG
        assert job_obj.will_persist_outputs is PersistOutputsOptions.DISABLED

    for job_obj in json_flow_tmpl, json_flow_tmpl.apply():
        assert job_obj.persist_outputs is PersistOutputsOptions.FOLLOW_CONFIG
        assert job_obj.will_persist_outputs is PersistOutputsOptions.ENABLED

    runtime.config.job.persist_outputs = \
        ConfigPersistOutputsOptions.ENABLE_FLOW_AND_TASK_OUTPUTS

    for job_obj in json_task_tmpl, json_task_tmpl.apply(), json_flow_tmpl, json_flow_tmpl.apply():
        assert job_obj.persist_outputs is PersistOutputsOptions.FOLLOW_CONFIG
        assert job_obj.will_persist_outputs is PersistOutputsOptions.ENABLED

    runtime.config.job.persist_outputs = ConfigPersistOutputsOptions.DISABLED

    for job_obj in json_task_tmpl, json_task_tmpl.apply(), json_flow_tmpl, json_flow_tmpl.apply():
        assert job_obj.persist_outputs is PersistOutputsOptions.FOLLOW_CONFIG
        assert job_obj.will_persist_outputs is PersistOutputsOptions.DISABLED


def test_properties_persist_outputs_override_config(
    runtime: Annotated[IsRuntime, pytest.fixture],
    json_task_tmpl: Annotated[TaskTemplate, pytest.fixture],
    json_flow_tmpl: Annotated[LinearFlowTemplate, pytest.fixture],
) -> None:

    assert runtime.config.job.persist_outputs == \
           ConfigPersistOutputsOptions.ENABLE_FLOW_AND_TASK_OUTPUTS

    json_task_tmpl_2 = json_task_tmpl.refine(persist_outputs='disabled')
    json_flow_tmpl_2 = json_flow_tmpl.refine(persist_outputs='disabled')

    for job_obj_2 in json_task_tmpl_2, json_task_tmpl_2.apply(), \
            json_flow_tmpl_2, json_flow_tmpl_2.apply():
        assert job_obj_2.persist_outputs is PersistOutputsOptions.DISABLED
        assert job_obj_2.will_persist_outputs is PersistOutputsOptions.DISABLED

    json_task_tmpl_3 = json_task_tmpl.refine(persist_outputs='enabled')
    json_flow_tmpl_3 = json_flow_tmpl.refine(persist_outputs='enabled')

    for job_obj_3 in json_task_tmpl_3, json_task_tmpl_3.apply(), \
            json_flow_tmpl_3, json_flow_tmpl_3.apply():
        assert job_obj_3.persist_outputs is PersistOutputsOptions.ENABLED
        assert job_obj_3.will_persist_outputs is PersistOutputsOptions.ENABLED

    runtime.config.job.persist_outputs = 'disabled'

    for job_obj in json_task_tmpl, json_task_tmpl.apply(), json_flow_tmpl, json_flow_tmpl.apply():
        assert job_obj.persist_outputs is PersistOutputsOptions.FOLLOW_CONFIG
        assert job_obj.will_persist_outputs is PersistOutputsOptions.DISABLED

    for job_obj_3 in json_task_tmpl_3, json_task_tmpl_3.apply(), \
            json_flow_tmpl_3, json_flow_tmpl_3.apply():
        assert job_obj_3.persist_outputs is PersistOutputsOptions.ENABLED
        assert job_obj_3.will_persist_outputs is PersistOutputsOptions.ENABLED

    json_task_tmpl_4 = json_task_tmpl_3.refine(persist_outputs=PersistOutputsOptions.FOLLOW_CONFIG)
    json_flow_tmpl_4 = json_flow_tmpl_3.refine(persist_outputs=PersistOutputsOptions.FOLLOW_CONFIG)

    for job_obj_4 in json_task_tmpl_4, json_task_tmpl_4.apply(), \
            json_flow_tmpl_4, json_flow_tmpl_4.apply():
        assert job_obj_4.persist_outputs is PersistOutputsOptions.FOLLOW_CONFIG
        assert job_obj_4.will_persist_outputs is PersistOutputsOptions.DISABLED


def test_properties_restore_outputs_enable_disable(
    runtime: Annotated[IsRuntime, pytest.fixture],
    json_task_tmpl: Annotated[TaskTemplate, pytest.fixture],
    json_flow_tmpl: Annotated[LinearFlowTemplate, pytest.fixture],
) -> None:

    runtime.config.job.restore_outputs = \
        ConfigRestoreOutputsOptions.AUTO_ENABLE_IGNORE_PARAMS

    for job_obj in json_task_tmpl, json_task_tmpl.apply(), json_flow_tmpl, json_flow_tmpl.apply():
        assert job_obj.restore_outputs is RestoreOutputsOptions.FOLLOW_CONFIG
        assert job_obj.will_restore_outputs is RestoreOutputsOptions.AUTO_ENABLE_IGNORE_PARAMS

    runtime.config.job.restore_outputs = ConfigRestoreOutputsOptions.DISABLED

    for job_obj in json_task_tmpl, json_task_tmpl.apply(), json_flow_tmpl, json_flow_tmpl.apply():
        assert job_obj.restore_outputs is RestoreOutputsOptions.FOLLOW_CONFIG
        assert job_obj.will_restore_outputs is RestoreOutputsOptions.DISABLED


def test_properties_restore_outputs_override_config(
    runtime: Annotated[IsRuntime, pytest.fixture],
    json_task_tmpl: Annotated[TaskTemplate, pytest.fixture],
    json_flow_tmpl: Annotated[LinearFlowTemplate, pytest.fixture],
) -> None:

    assert runtime.config.job.restore_outputs == ConfigRestoreOutputsOptions.DISABLED

    json_task_tmpl_2 = json_task_tmpl.refine(restore_outputs='auto_ignore_params')
    json_flow_tmpl_2 = json_flow_tmpl.refine(restore_outputs='auto_ignore_params')

    for job_obj_2 in json_task_tmpl_2, json_task_tmpl_2.apply(), \
            json_flow_tmpl_2, json_flow_tmpl_2.apply():
        assert job_obj_2.restore_outputs is RestoreOutputsOptions.AUTO_ENABLE_IGNORE_PARAMS
        assert job_obj_2.will_restore_outputs is RestoreOutputsOptions.AUTO_ENABLE_IGNORE_PARAMS

    json_task_tmpl_3 = json_task_tmpl.refine(restore_outputs='force_ignore_params')
    json_flow_tmpl_3 = json_flow_tmpl.refine(restore_outputs='force_ignore_params')

    for job_obj_3 in json_task_tmpl_3, json_task_tmpl_3.apply(), \
            json_flow_tmpl_3, json_flow_tmpl_3.apply():
        assert job_obj_3.restore_outputs is RestoreOutputsOptions.FORCE_ENABLE_IGNORE_PARAMS
        assert job_obj_3.will_restore_outputs is RestoreOutputsOptions.FORCE_ENABLE_IGNORE_PARAMS

    runtime.config.job.restore_outputs = 'auto_ignore_params'

    for job_obj in json_task_tmpl, json_task_tmpl.apply(), json_flow_tmpl, json_flow_tmpl.apply():
        assert job_obj.restore_outputs is RestoreOutputsOptions.FOLLOW_CONFIG
        assert job_obj.will_restore_outputs is RestoreOutputsOptions.AUTO_ENABLE_IGNORE_PARAMS

    for job_obj_3 in json_task_tmpl_3, json_task_tmpl_3.apply(), \
            json_flow_tmpl_3, json_flow_tmpl_3.apply():
        assert job_obj_3.restore_outputs is RestoreOutputsOptions.FORCE_ENABLE_IGNORE_PARAMS
        assert job_obj_3.will_restore_outputs is RestoreOutputsOptions.FORCE_ENABLE_IGNORE_PARAMS

    json_task_tmpl_4 = json_task_tmpl_3.refine(restore_outputs=PersistOutputsOptions.FOLLOW_CONFIG)
    json_flow_tmpl_4 = json_flow_tmpl_3.refine(restore_outputs=PersistOutputsOptions.FOLLOW_CONFIG)

    for job_obj_4 in json_task_tmpl_4, json_task_tmpl_4.apply(), \
            json_flow_tmpl_4, json_flow_tmpl_4.apply():
        assert job_obj_4.restore_outputs is RestoreOutputsOptions.FOLLOW_CONFIG
        assert job_obj_4.will_restore_outputs is RestoreOutputsOptions.AUTO_ENABLE_IGNORE_PARAMS


# def test_auto_detect_serializer(json_task_tmpl: Annotated[TaskTemplate, pytest.fixture],):
#     assert auto_detect_serializer(json_task_tmpl.run()) == JsonDatasetToTarFileSerializer
