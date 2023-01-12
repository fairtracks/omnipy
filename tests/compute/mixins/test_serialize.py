import tempfile
from typing import Annotated

import pytest
import pytest_cases as pc

from compute.mixins.cases.raw.functions import json_func
from omnipy.compute.flow import LinearFlowTemplate
from omnipy.compute.mixins.serialize import PersistOutputsOptions, RestoreOutputsOptions
from omnipy.compute.private.job import FuncJob, FuncJobBase, FuncJobTemplate
from omnipy.compute.task import TaskTemplate
from omnipy.config.job import ConfigPersistOutputsOptions, ConfigRestoreOutputsOptions
from omnipy.engine.protocols import IsRuntime


@pc.parametrize_with_cases('case_tmpl', cases='.cases.jobs', has_tag='task', prefix='case_config_')
def test_all_properties_pytest_default_config(case_tmpl) -> None:
    for job_obj in case_tmpl, case_tmpl.apply():
        assert job_obj.persist_outputs is None
        assert job_obj.will_persist_outputs is PersistOutputsOptions.DISABLED
        assert job_obj.restore_outputs is None
        assert job_obj.will_restore_outputs is RestoreOutputsOptions.DISABLED


@pc.parametrize_with_cases('case_tmpl', cases='.cases.jobs', prefix='case_config_')
def test_all_properties_runtime_default_config(
    runtime: Annotated[IsRuntime, pytest.fixture],
    case_tmpl,
) -> None:

    assert runtime.config.job.persist_outputs == \
           ConfigPersistOutputsOptions.ENABLE_FLOW_AND_TASK_OUTPUTS
    assert runtime.config.job.restore_outputs == ConfigRestoreOutputsOptions.DISABLED

    for job_obj in case_tmpl, case_tmpl.apply():
        assert job_obj.persist_outputs is PersistOutputsOptions.FOLLOW_CONFIG
        assert job_obj.will_persist_outputs is PersistOutputsOptions.ENABLED

        assert job_obj.restore_outputs is RestoreOutputsOptions.FOLLOW_CONFIG
        assert job_obj.will_restore_outputs is RestoreOutputsOptions.DISABLED


@pc.parametrize_with_cases(
    'case_task_tmpl', cases='.cases.jobs', has_tag='task', prefix='case_config_')
@pc.parametrize_with_cases(
    'case_flow_tmpl', cases='.cases.jobs', has_tag='flow', prefix='case_config_')
def test_properties_persist_outputs_enable_disable(
    runtime: Annotated[IsRuntime, pytest.fixture],
    case_task_tmpl,
    case_flow_tmpl,
) -> None:

    runtime.config.job.persist_outputs = ConfigPersistOutputsOptions.ENABLE_FLOW_OUTPUTS
    assert TaskTemplate.config.persist_outputs == ConfigPersistOutputsOptions.ENABLE_FLOW_OUTPUTS

    for task_obj in case_task_tmpl, case_task_tmpl.apply():
        assert task_obj.persist_outputs is PersistOutputsOptions.FOLLOW_CONFIG
        assert task_obj.will_persist_outputs is PersistOutputsOptions.DISABLED

    for flow_obj in case_flow_tmpl, case_flow_tmpl.apply():
        assert flow_obj.persist_outputs is PersistOutputsOptions.FOLLOW_CONFIG
        assert flow_obj.will_persist_outputs is PersistOutputsOptions.ENABLED

    runtime.config.job.persist_outputs = \
        ConfigPersistOutputsOptions.ENABLE_FLOW_AND_TASK_OUTPUTS

    for job_obj in case_task_tmpl, case_task_tmpl.apply(), case_flow_tmpl, case_flow_tmpl.apply():
        assert job_obj.persist_outputs is PersistOutputsOptions.FOLLOW_CONFIG
        assert job_obj.will_persist_outputs is PersistOutputsOptions.ENABLED

    runtime.config.job.persist_outputs = ConfigPersistOutputsOptions.DISABLED

    for job_obj in case_task_tmpl, case_task_tmpl.apply(), case_flow_tmpl, case_flow_tmpl.apply():
        assert job_obj.persist_outputs is PersistOutputsOptions.FOLLOW_CONFIG
        assert job_obj.will_persist_outputs is PersistOutputsOptions.DISABLED


@pc.parametrize_with_cases('case_tmpl', cases='.cases.jobs', prefix='case_config_')
def test_properties_persist_outputs_override_config(
    runtime: Annotated[IsRuntime, pytest.fixture],
    case_tmpl,
) -> None:

    assert runtime.config.job.persist_outputs == \
           ConfigPersistOutputsOptions.ENABLE_FLOW_AND_TASK_OUTPUTS

    case_tmpl_2 = case_tmpl.refine(persist_outputs='disabled')

    for job_obj_2 in case_tmpl_2, case_tmpl_2.apply():
        assert job_obj_2.persist_outputs is PersistOutputsOptions.DISABLED
        assert job_obj_2.will_persist_outputs is PersistOutputsOptions.DISABLED

    case_tmpl_3 = case_tmpl.refine(persist_outputs='enabled')

    for job_obj_3 in case_tmpl_3, case_tmpl_3.apply():
        assert job_obj_3.persist_outputs is PersistOutputsOptions.ENABLED
        assert job_obj_3.will_persist_outputs is PersistOutputsOptions.ENABLED

    runtime.config.job.persist_outputs = 'disabled'

    for job_obj in case_tmpl, case_tmpl.apply():
        assert job_obj.persist_outputs is PersistOutputsOptions.FOLLOW_CONFIG
        assert job_obj.will_persist_outputs is PersistOutputsOptions.DISABLED

    for job_obj_3 in case_tmpl_3, case_tmpl_3.apply():
        assert job_obj_3.persist_outputs is PersistOutputsOptions.ENABLED
        assert job_obj_3.will_persist_outputs is PersistOutputsOptions.ENABLED

    case_tmpl_4 = case_tmpl_3.refine(persist_outputs=PersistOutputsOptions.FOLLOW_CONFIG)

    for job_obj_4 in case_tmpl_4, case_tmpl_4.apply():
        assert job_obj_4.persist_outputs is PersistOutputsOptions.FOLLOW_CONFIG
        assert job_obj_4.will_persist_outputs is PersistOutputsOptions.DISABLED


@pc.parametrize_with_cases('case_tmpl', cases='.cases.jobs', prefix='case_config_')
def test_properties_restore_outputs_enable_disable(
    runtime: Annotated[IsRuntime, pytest.fixture],
    case_tmpl,
) -> None:

    runtime.config.job.restore_outputs = \
        ConfigRestoreOutputsOptions.AUTO_ENABLE_IGNORE_PARAMS

    for job_obj in case_tmpl, case_tmpl.apply():
        assert job_obj.restore_outputs is RestoreOutputsOptions.FOLLOW_CONFIG
        assert job_obj.will_restore_outputs is RestoreOutputsOptions.AUTO_ENABLE_IGNORE_PARAMS

    runtime.config.job.restore_outputs = ConfigRestoreOutputsOptions.DISABLED

    for job_obj in case_tmpl, case_tmpl.apply():
        assert job_obj.restore_outputs is RestoreOutputsOptions.FOLLOW_CONFIG
        assert job_obj.will_restore_outputs is RestoreOutputsOptions.DISABLED


@pc.parametrize_with_cases('case_tmpl', cases='.cases.jobs', prefix='case_config_')
def test_properties_restore_outputs_override_config(
    runtime: Annotated[IsRuntime, pytest.fixture],
    case_tmpl: Annotated[FuncJobBase, pc.case],
) -> None:

    assert runtime.config.job.restore_outputs == ConfigRestoreOutputsOptions.DISABLED

    case_tmpl_2 = case_tmpl.refine(restore_outputs='auto_ignore_params')

    for job_obj_2 in case_tmpl_2, case_tmpl_2.apply():
        assert job_obj_2.restore_outputs is RestoreOutputsOptions.AUTO_ENABLE_IGNORE_PARAMS
        assert job_obj_2.will_restore_outputs is RestoreOutputsOptions.AUTO_ENABLE_IGNORE_PARAMS

    case_tmpl_3 = case_tmpl.refine(restore_outputs='force_ignore_params')

    for job_obj_3 in case_tmpl_3, case_tmpl_3.apply():
        assert job_obj_3.restore_outputs is RestoreOutputsOptions.FORCE_ENABLE_IGNORE_PARAMS
        assert job_obj_3.will_restore_outputs is RestoreOutputsOptions.FORCE_ENABLE_IGNORE_PARAMS

    runtime.config.job.restore_outputs = 'auto_ignore_params'

    for job_obj in case_tmpl, case_tmpl.apply():
        assert job_obj.restore_outputs is RestoreOutputsOptions.FOLLOW_CONFIG
        assert job_obj.will_restore_outputs is RestoreOutputsOptions.AUTO_ENABLE_IGNORE_PARAMS

    for job_obj_3 in case_tmpl_3, case_tmpl_3.apply():
        assert job_obj_3.restore_outputs is RestoreOutputsOptions.FORCE_ENABLE_IGNORE_PARAMS
        assert job_obj_3.will_restore_outputs is RestoreOutputsOptions.FORCE_ENABLE_IGNORE_PARAMS

    case_tmpl_4 = case_tmpl_3.refine(restore_outputs=PersistOutputsOptions.FOLLOW_CONFIG)

    for job_obj_4 in case_tmpl_4, case_tmpl_4.apply():
        assert job_obj_4.restore_outputs is RestoreOutputsOptions.FOLLOW_CONFIG
        assert job_obj_4.will_restore_outputs is RestoreOutputsOptions.AUTO_ENABLE_IGNORE_PARAMS


@pc.parametrize_with_cases('case_tmpl', cases='.cases.jobs', prefix='case_')
def test_persist_and_restore(
    runtime: Annotated[IsRuntime, pytest.fixture],
    case_tmpl: Annotated[FuncJobTemplate[FuncJob], pc.case],
) -> None:

    with tempfile.TemporaryDirectory() as tmp_dir_path:
        runtime.config.job.persist_data_dir_path = tmp_dir_path

        case_persist_tmpl = case_tmpl.refine(persist_outputs='enabled')
        dataset_persist = case_persist_tmpl.run()

        case_restore_tmpl = case_tmpl.refine(restore_outputs='force_ignore_params')
        dataset_restore = case_restore_tmpl.run()

        assert dataset_persist == dataset_restore
