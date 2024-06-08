from typing import Annotated, Iterator

import pytest
import pytest_cases as pc

from omnipy.api.enums import (ConfigOutputStorageProtocolOptions,
                              ConfigPersistOutputsOptions,
                              ConfigRestoreOutputsOptions,
                              OutputStorageProtocolOptions,
                              PersistOutputsOptions,
                              RestoreOutputsOptions)
from omnipy.api.protocols.public.hub import IsRuntime
from omnipy.compute.task import FuncArgJobBase


@pc.parametrize_with_cases('case_tmpl', cases='.cases.jobs', has_tag='task', prefix='case_config_')
def test_all_properties_pytest_default_config(case_tmpl) -> None:
    for job_obj in case_tmpl, case_tmpl.apply():
        assert job_obj.persist_outputs is None
        assert job_obj.will_persist_outputs is PersistOutputsOptions.DISABLED
        assert job_obj.restore_outputs is None
        assert job_obj.will_restore_outputs is RestoreOutputsOptions.DISABLED
        assert job_obj.output_storage_protocol is None
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
    case_tmpl: Annotated[FuncArgJobBase, pc.case],
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
    assert_snapshot_holder_and_deepcopy_memo_are_empty: Annotated[Iterator[None], pytest.fixture],
    case_tmpl: Annotated[FuncArgJobBase, pc.case],
) -> None:
    case_persist_tmpl = case_tmpl.refine(persist_outputs='enabled')
    dataset_persist = case_persist_tmpl.run()

    case_restore_tmpl = case_tmpl.refine(restore_outputs='force_ignore_params')
    dataset_restore = case_restore_tmpl.run()

    assert dataset_restore.to_data() == dataset_persist.to_data()
