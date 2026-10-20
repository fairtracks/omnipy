import asyncio
from itertools import count
from typing import Annotated

import pytest

from omnipy.compute.flow import DagFlowTemplate, LinearFlowTemplate
from omnipy.compute.task import TaskTemplate
from omnipy.shared.enums.job import RunState

from .....engine.helpers.functions import assert_job_state
from .models import (BioSampleVaultSampleSubmissionSchema,
                     FinalSubmissionModel,
                     FtpUrlModel,
                     S3UrlModel,
                     SampleAndMetadataToBioSampleVaultSubmissionMapper,
                     SequenceDepotSubmissionIdRequest,
                     Status,
                     SubmissionFileSchemaModel,
                     SubmissionFilesDataset,
                     SubmissionMetadataModel,
                     SubmissionModel,
                     SubmissionSampleModel,
                     SubmissionSamplesDataset,
                     SubmissionToSequenceDepotRequestMapper)


async def test_sequence_submission_brokering(
    runtime_all_engines: Annotated[None, pytest.fixture],  # noqa
    samples: Annotated[dict[str, dict[str, str]], pytest.fixture],
    files: Annotated[dict[str, dict[str, str]], pytest.fixture],
    metadata: Annotated[dict[str, str], pytest.fixture],
    expected_sequence_depot_submission_payload: Annotated[
        dict[str, object],
        pytest.fixture,
    ],
) -> None:
    submission = SubmissionModel(samples=samples, files=files, metadata=metadata)
    print()
    submission.full(width=160)

    brokering_flow = broker_sequence_submission_flow.apply()
    final_submission = await brokering_flow(submission)

    assert final_submission.to_data() == \
        expected_sequence_depot_submission_payload

    assert_job_state(brokering_flow, [RunState.FINISHED])


async def request_sequence_depot_submission_id(
        request: SequenceDepotSubmissionIdRequest) -> SequenceDepotSubmissionIdRequest:
    await asyncio.sleep(0)
    request.sequence_depot_submission_id = 'SQD:4021372983'
    return request


@TaskTemplate()
async def allocate_sequence_depot_submission_id(submission: SubmissionModel) -> SubmissionModel:
    request_return = await request_sequence_depot_submission_id(
        SubmissionToSequenceDepotRequestMapper(submission))
    submission.metadata.sequence_depot_submission_id = request_return.sequence_depot_submission_id

    return submission


@TaskTemplate()
def explode_submission_model(submission: SubmissionModel) -> dict[str, object]:
    return {
        'samples': submission.samples,
        'files': submission.files,
        'metadata': submission.metadata,
    }


async def transfer_file(
    username: str,
    source_uri: S3UrlModel,
    target_uri: FtpUrlModel,
) -> tuple[Status, str | None]:
    await asyncio.sleep(0)
    return 'completed', None


@TaskTemplate(iterate_over_data_files=True)
async def transfer_all_files(
    dataset: SubmissionFileSchemaModel,
    *,
    metadata: SubmissionMetadataModel,
) -> SubmissionFileSchemaModel:
    file = dataset
    staging_uri = FtpUrlModel('ftps://seq-depot-staging')
    staging_uri.path // metadata.broker_id
    staging_uri.path // metadata.local_submission_alias
    staging_uri.path // file.file_name
    file.staging_storage_uri = staging_uri

    status, error = await transfer_file(username=metadata.broker_id,
                                        source_uri=file.source_storage_uri,
                                        target_uri=file.staging_storage_uri)
    file.transfer_status = status
    file.error = error

    return file


@TaskTemplate()
def collect_submission_model(
    samples: SubmissionSamplesDataset,
    files: SubmissionFilesDataset,
    submission: SubmissionModel,
) -> SubmissionModel:
    submission.files = files
    submission.samples = samples
    return submission


@DagFlowTemplate(
    explode_submission_model,
    transfer_all_files.refine(
        param_key_map={'dataset': 'files'},
        result_key='files',
    ),
    collect_submission_model,
    consume_kwargs_from_results=False,
)
async def coordinate_external_file_transfer(submission: SubmissionModel) -> SubmissionModel:
    ...


biosample_vault_sample_id_generator: count[int] = count(start=80907461)


async def register_sample_with_biosamplevault(
        request: BioSampleVaultSampleSubmissionSchema) -> BioSampleVaultSampleSubmissionSchema:
    await asyncio.sleep(0)
    request.biosample_vault_sample_id = f'BSV:{next(biosample_vault_sample_id_generator)}'
    return request


@TaskTemplate(iterate_over_data_files=True)
async def register_all_samples_with_biosamplevault(
    dataset: SubmissionSampleModel,
    *,
    metadata: SubmissionMetadataModel,
) -> SubmissionSampleModel:
    sample = dataset
    bsv_submission = SampleAndMetadataToBioSampleVaultSubmissionMapper((sample, metadata))
    bsv_submission = await register_sample_with_biosamplevault(bsv_submission)
    sample.biosample_vault_sample_id = bsv_submission.biosample_vault_sample_id
    return sample


@DagFlowTemplate(
    explode_submission_model,
    register_all_samples_with_biosamplevault.refine(
        param_key_map={'dataset': 'samples'},
        result_key='samples',
    ),
    collect_submission_model,
    consume_kwargs_from_results=False,
)
async def coordinate_biosamplevault_registration(submission: SubmissionModel) -> SubmissionModel:
    ...


async def submit_final_submission_to_sequence_depot(submission: FinalSubmissionModel) -> bool:
    await asyncio.sleep(0)
    return True


@TaskTemplate()
async def finalize_sequence_depot_submission(submission: SubmissionModel) -> SubmissionModel:
    assert submission.status.sequence_depot_submission_id_status == 'completed'
    assert submission.status.biosample_vault_status == 'completed'
    assert submission.status.transfer_status == 'completed'

    final_submission = FinalSubmissionModel(
        samples=submission.samples,
        files=submission.files,
        metadata=submission.metadata,
    )
    ok = await submit_final_submission_to_sequence_depot(final_submission)
    assert ok
    submission.status.sequence_depot_submission_status = 'completed'

    return submission


@LinearFlowTemplate(
    allocate_sequence_depot_submission_id,
    coordinate_biosamplevault_registration,
    coordinate_external_file_transfer,
    finalize_sequence_depot_submission,
)
async def broker_sequence_submission_flow(submission: SubmissionModel) -> SubmissionModel:
    ...
