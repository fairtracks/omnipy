"""Tests for serialization."""

import asyncio
from inspect import isawaitable
from pathlib import Path
from types import SimpleNamespace
from typing import Annotated

import pytest
import pytest_cases as pc

from omnipy.components import get_serializer_registry
from omnipy.components.json.datasets import JsonDataset
from omnipy.compute.flow import FuncFlowTemplate
from omnipy.compute.task import TaskTemplate
from omnipy.shared.enums.job import (ConfigOutputStorageProtocolOptions,
                                     ConfigPersistOutputsOptions,
                                     ConfigRestoreOutputsOptions,
                                     OutputStorageProtocolOptions,
                                     PersistOutputsOptions,
                                     RestoreOutputsOptions)
from omnipy.shared.protocols.compute.job import IsFuncArgJobTemplate
from omnipy.shared.protocols.hub.runtime import IsRuntime


@pc.parametrize_with_cases('case_tmpl', cases='.cases.jobs', has_tag='task', prefix='case_config_')
def test_all_properties_pytest_default_config(case_tmpl) -> None:
    for job_obj in case_tmpl, case_tmpl.apply():
        assert job_obj.persist_outputs is PersistOutputsOptions.FOLLOW_CONFIG
        assert job_obj.will_persist_outputs is PersistOutputsOptions.ENABLED
        assert job_obj.restore_outputs is RestoreOutputsOptions.FOLLOW_CONFIG
        assert job_obj.will_restore_outputs is RestoreOutputsOptions.DISABLED
        assert job_obj.output_storage_protocol is OutputStorageProtocolOptions.FOLLOW_CONFIG
        assert job_obj.output_storage_protocol_to_use is OutputStorageProtocolOptions.LOCAL


@pc.parametrize_with_cases('case_tmpl', cases='.cases.jobs', prefix='case_config_')
def test_all_properties_runtime_default_config(
    runtime: Annotated[IsRuntime, pytest.fixture],
    case_tmpl,
) -> None:
    assert runtime.config.job.output_storage.persist_outputs == \
           ConfigPersistOutputsOptions.ENABLE_FLOW_AND_TASK_OUTPUTS
    assert runtime.config.job.output_storage.restore_outputs == ConfigRestoreOutputsOptions.DISABLED
    assert runtime.config.job.output_storage.protocol == ConfigOutputStorageProtocolOptions.LOCAL

    for job_obj in case_tmpl, case_tmpl.apply():
        assert job_obj.persist_outputs is PersistOutputsOptions.FOLLOW_CONFIG
        assert job_obj.will_persist_outputs is PersistOutputsOptions.ENABLED

        assert job_obj.restore_outputs is RestoreOutputsOptions.FOLLOW_CONFIG
        assert job_obj.will_restore_outputs is RestoreOutputsOptions.DISABLED

        assert job_obj.output_storage_protocol is OutputStorageProtocolOptions.FOLLOW_CONFIG
        assert job_obj.output_storage_protocol_to_use is OutputStorageProtocolOptions.LOCAL


@pc.parametrize_with_cases(
    'case_task_tmpl', cases='.cases.jobs', has_tag='task', prefix='case_config_')
@pc.parametrize_with_cases(
    'case_flow_tmpl', cases='.cases.jobs', has_tag='flow', prefix='case_config_')
def test_properties_persist_outputs_enable_disable(
    runtime: Annotated[IsRuntime, pytest.fixture],
    case_task_tmpl,
    case_flow_tmpl,
) -> None:
    runtime.config.job.output_storage.persist_outputs = (
        ConfigPersistOutputsOptions.ENABLE_FLOW_OUTPUTS)

    for task_obj in case_task_tmpl, case_task_tmpl.apply():
        assert task_obj.persist_outputs is PersistOutputsOptions.FOLLOW_CONFIG
        assert task_obj.will_persist_outputs is PersistOutputsOptions.DISABLED

    for flow_obj in case_flow_tmpl, case_flow_tmpl.apply():
        assert flow_obj.persist_outputs is PersistOutputsOptions.FOLLOW_CONFIG
        assert flow_obj.will_persist_outputs is PersistOutputsOptions.ENABLED

    runtime.config.job.output_storage.persist_outputs = (
        ConfigPersistOutputsOptions.ENABLE_FLOW_AND_TASK_OUTPUTS)

    for job_obj in case_task_tmpl, case_task_tmpl.apply(), case_flow_tmpl, case_flow_tmpl.apply():
        assert job_obj.persist_outputs is PersistOutputsOptions.FOLLOW_CONFIG
        assert job_obj.will_persist_outputs is PersistOutputsOptions.ENABLED

    runtime.config.job.output_storage.persist_outputs = ConfigPersistOutputsOptions.DISABLED

    for job_obj in case_task_tmpl, case_task_tmpl.apply(), case_flow_tmpl, case_flow_tmpl.apply():
        assert job_obj.persist_outputs is PersistOutputsOptions.FOLLOW_CONFIG
        assert job_obj.will_persist_outputs is PersistOutputsOptions.DISABLED


@pc.parametrize_with_cases('case_tmpl', cases='.cases.jobs', prefix='case_config_')
def test_properties_persist_outputs_override_config(
    runtime: Annotated[IsRuntime, pytest.fixture],
    case_tmpl,
) -> None:
    assert runtime.config.job.output_storage.persist_outputs == \
           ConfigPersistOutputsOptions.ENABLE_FLOW_AND_TASK_OUTPUTS

    case_tmpl_2 = case_tmpl.refine(persist_outputs='disabled')

    for job_obj_2 in case_tmpl_2, case_tmpl_2.apply():
        assert job_obj_2.persist_outputs is PersistOutputsOptions.DISABLED
        assert job_obj_2.will_persist_outputs is PersistOutputsOptions.DISABLED

    case_tmpl_3 = case_tmpl.refine(persist_outputs='enabled')

    for job_obj_3 in case_tmpl_3, case_tmpl_3.apply():
        assert job_obj_3.persist_outputs is PersistOutputsOptions.ENABLED
        assert job_obj_3.will_persist_outputs is PersistOutputsOptions.ENABLED

    runtime.config.job.output_storage.persist_outputs = 'disabled'

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
    runtime.config.job.output_storage.restore_outputs = \
        ConfigRestoreOutputsOptions.AUTO_ENABLE_IGNORE_PARAMS

    for job_obj in case_tmpl, case_tmpl.apply():
        assert job_obj.restore_outputs is RestoreOutputsOptions.FOLLOW_CONFIG
        assert job_obj.will_restore_outputs is RestoreOutputsOptions.AUTO_ENABLE_IGNORE_PARAMS

    runtime.config.job.output_storage.restore_outputs = ConfigRestoreOutputsOptions.DISABLED

    for job_obj in case_tmpl, case_tmpl.apply():
        assert job_obj.restore_outputs is RestoreOutputsOptions.FOLLOW_CONFIG
        assert job_obj.will_restore_outputs is RestoreOutputsOptions.DISABLED


@pc.parametrize_with_cases('case_tmpl', cases='.cases.jobs', prefix='case_config_')
def test_properties_restore_outputs_override_config(
    runtime: Annotated[IsRuntime, pytest.fixture],
    case_tmpl: Annotated[IsFuncArgJobTemplate, pc.case],
) -> None:
    assert runtime.config.job.output_storage.restore_outputs == ConfigRestoreOutputsOptions.DISABLED

    case_tmpl_2 = case_tmpl.refine(restore_outputs='auto_ignore_params')

    for job_obj_2 in case_tmpl_2, case_tmpl_2.apply():
        assert job_obj_2.restore_outputs is RestoreOutputsOptions.AUTO_ENABLE_IGNORE_PARAMS
        assert job_obj_2.will_restore_outputs is RestoreOutputsOptions.AUTO_ENABLE_IGNORE_PARAMS

    case_tmpl_3 = case_tmpl.refine(restore_outputs='force_ignore_params')

    for job_obj_3 in case_tmpl_3, case_tmpl_3.apply():
        assert job_obj_3.restore_outputs is RestoreOutputsOptions.FORCE_ENABLE_IGNORE_PARAMS
        assert job_obj_3.will_restore_outputs is RestoreOutputsOptions.FORCE_ENABLE_IGNORE_PARAMS

    runtime.config.job.output_storage.restore_outputs = 'auto_ignore_params'

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


@pc.parametrize_with_cases(
    'case_task_tmpl', cases='.cases.jobs', has_tag='task', prefix='case_config_')
@pc.parametrize_with_cases(
    'case_flow_tmpl', cases='.cases.jobs', has_tag='flow', prefix='case_config_')
def test_properties_output_storage_protocols(
    runtime: Annotated[IsRuntime, pytest.fixture],
    case_task_tmpl,
    case_flow_tmpl,
) -> None:
    runtime.config.job.output_storage.protocol = ConfigOutputStorageProtocolOptions.S3

    for job_obj in case_task_tmpl, case_task_tmpl.apply(), case_flow_tmpl, case_flow_tmpl.apply():
        assert job_obj.output_storage_protocol is OutputStorageProtocolOptions.FOLLOW_CONFIG
        assert job_obj.output_storage_protocol_to_use is OutputStorageProtocolOptions.S3

    runtime.config.job.output_storage.protocol = ConfigOutputStorageProtocolOptions.LOCAL

    for job_obj in case_task_tmpl, case_task_tmpl.apply(), case_flow_tmpl, case_flow_tmpl.apply():
        assert job_obj.output_storage_protocol is OutputStorageProtocolOptions.FOLLOW_CONFIG
        assert job_obj.output_storage_protocol_to_use is OutputStorageProtocolOptions.LOCAL


@pc.parametrize_with_cases('case_tmpl', cases='.cases.jobs', prefix='case_config_')
def test_properties_output_storage_protocols_override_config(
    runtime: Annotated[IsRuntime, pytest.fixture],
    case_tmpl,
) -> None:
    assert runtime.config.job.output_storage.protocol == ConfigOutputStorageProtocolOptions.LOCAL

    case_tmpl_2 = case_tmpl.refine(output_storage_protocol='s3')

    for job_obj_2 in case_tmpl_2, case_tmpl_2.apply():
        assert job_obj_2.output_storage_protocol is OutputStorageProtocolOptions.S3
        assert job_obj_2.output_storage_protocol_to_use is OutputStorageProtocolOptions.S3

    case_tmpl_3 = case_tmpl.refine(output_storage_protocol='local')

    for job_obj_3 in case_tmpl_3, case_tmpl_3.apply():
        assert job_obj_3.output_storage_protocol is OutputStorageProtocolOptions.LOCAL
        assert job_obj_3.output_storage_protocol_to_use is OutputStorageProtocolOptions.LOCAL

    runtime.config.job.output_storage.protocol = 's3'

    for job_obj in case_tmpl, case_tmpl.apply():
        assert job_obj.output_storage_protocol is OutputStorageProtocolOptions.FOLLOW_CONFIG
        assert job_obj.output_storage_protocol_to_use is OutputStorageProtocolOptions.S3

    for job_obj_3 in case_tmpl_3, case_tmpl_3.apply():
        assert job_obj_3.output_storage_protocol is OutputStorageProtocolOptions.LOCAL
        assert job_obj_3.output_storage_protocol_to_use is OutputStorageProtocolOptions.LOCAL

    case_tmpl_4 = case_tmpl_3.refine(output_storage_protocol='config')

    for job_obj_4 in case_tmpl_4, case_tmpl_4.apply():
        assert job_obj_4.output_storage_protocol is OutputStorageProtocolOptions.FOLLOW_CONFIG
        assert job_obj_4.output_storage_protocol_to_use is OutputStorageProtocolOptions.S3


@pc.parametrize_with_cases('case_tmpl', cases='.cases.jobs', prefix='case_')
def test_persist_and_restore(
    runtime: Annotated[IsRuntime, pytest.fixture],
    case_tmpl: Annotated[IsFuncArgJobTemplate, pc.case],
) -> None:
    case_persist_tmpl = case_tmpl.refine(persist_outputs='enabled')
    dataset_persist = case_persist_tmpl.run()

    case_restore_tmpl = case_tmpl.refine(restore_outputs='force_ignore_params')
    dataset_restore = case_restore_tmpl.run()

    assert dataset_restore.to_data() == dataset_persist.to_data()


def _persisted_tar_files(runtime: IsRuntime) -> set[Path]:
    persist_dir_path = Path(runtime.config.job.output_storage.local.persist_data_dir_path)
    if not persist_dir_path.exists():
        return set()

    return set(persist_dir_path.rglob('*.tar.gz'))


def _new_persisted_tar_files(runtime: IsRuntime, before_files: set[Path]) -> list[Path]:
    return sorted(_persisted_tar_files(runtime) - before_files)


def _restore_json_dataset_from_tar_file(tar_file_path: Path) -> JsonDataset:
    restored_dataset = get_serializer_registry().load_from_tar_file_path_based_on_file_suffix(
        log_obj=SimpleNamespace(log=lambda _msg: None),
        tar_file_path=str(tar_file_path),
        to_dataset=JsonDataset(),
    )

    assert isinstance(restored_dataset, JsonDataset)
    return restored_dataset


def test_async_task_serialize_then_result_key_without_running_loop(
    runtime: Annotated[IsRuntime, pytest.fixture],
    json_dataset: Annotated[JsonDataset, pytest.fixture],
) -> None:
    @TaskTemplate(
        auto_async=True,
        persist_outputs='enabled',
        result_key='wrapped',
    )
    async def async_json_task() -> JsonDataset:
        await asyncio.sleep(0)
        return json_dataset

    persisted_files_before = _persisted_tar_files(runtime)

    wrapped_result = async_json_task.run()
    assert wrapped_result == {'wrapped': json_dataset}

    new_tar_files = _new_persisted_tar_files(runtime, persisted_files_before)
    assert len(new_tar_files) == 1

    restored_dataset = _restore_json_dataset_from_tar_file(new_tar_files[0])
    assert restored_dataset.to_data() == json_dataset.to_data()


@pytest.mark.anyio
async def test_async_task_serialize_then_result_key_inside_running_loop(
    runtime: Annotated[IsRuntime, pytest.fixture],
    json_dataset: Annotated[JsonDataset, pytest.fixture],
) -> None:
    @TaskTemplate(
        auto_async=True,
        persist_outputs='enabled',
        result_key='wrapped',
    )
    async def async_json_task() -> JsonDataset:
        await asyncio.sleep(0)
        return json_dataset

    persisted_files_before = _persisted_tar_files(runtime)

    wrapped_result = async_json_task.run()
    wrapped_task = wrapped_result['wrapped']
    assert isinstance(wrapped_task, asyncio.Task)

    wrapped_dataset = await wrapped_task
    assert wrapped_dataset.to_data() == json_dataset.to_data()

    await asyncio.sleep(0)

    new_tar_files = _new_persisted_tar_files(runtime, persisted_files_before)
    assert len(new_tar_files) == 1

    restored_dataset = _restore_json_dataset_from_tar_file(new_tar_files[0])
    assert restored_dataset.to_data() == json_dataset.to_data()


@pytest.mark.anyio
async def test_async_func_flow_serialize_then_result_key_in_flow_context(
    runtime: Annotated[IsRuntime, pytest.fixture],
    json_dataset: Annotated[JsonDataset, pytest.fixture],
) -> None:
    @FuncFlowTemplate(
        auto_async=True,
        persist_outputs='enabled',
        result_key='flow_wrapped',
    )
    async def async_inner_flow() -> JsonDataset:
        await asyncio.sleep(0)
        return json_dataset

    @FuncFlowTemplate(
        auto_async=False,
        persist_outputs='disabled',
    )
    async def outer_flow() -> JsonDataset:
        wrapped_result = async_inner_flow.run()
        wrapped_value = wrapped_result['flow_wrapped']

        assert isawaitable(wrapped_value)
        assert not isinstance(wrapped_value, asyncio.Task)

        return await wrapped_value

    persisted_files_before = _persisted_tar_files(runtime)

    outer_result = outer_flow.run()
    assert isawaitable(outer_result)

    resolved_outer_result = await outer_result
    assert resolved_outer_result.to_data() == json_dataset.to_data()

    new_tar_files = _new_persisted_tar_files(runtime, persisted_files_before)
    assert len(new_tar_files) == 1

    restored_dataset = _restore_json_dataset_from_tar_file(new_tar_files[0])
    assert restored_dataset.to_data() == json_dataset.to_data()
