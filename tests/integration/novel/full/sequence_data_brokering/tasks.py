from omnipy.compute.task import TaskTemplate

from .models import (
    FinalSubmissionModel,
    FtpUrlModel,
    SampleAndMetadataToBioSampleVaultSubmissionMapper,
    ServicesModel,
    SubmissionFilesByIdModel,
    SubmissionFileSchemaModel,
    SubmissionMetadataModel,
    SubmissionModel,
    SubmissionSampleModel,
    SubmissionSamplesByIdModel,
    SubmissionToSequenceDepotRequestMapper,
)
from .services import (
    register_sample_with_biosamplevault,
    request_sequence_depot_submission_id,
    submit_final_submission_to_sequence_depot,
    transfer_file,
)

# Helper task templates


@TaskTemplate()
def explode_submission_model(submission: SubmissionModel) -> dict[str, object]:
    return {
        'samples': submission.samples,
        'files': submission.files,
        'metadata': submission.metadata,
        'services': submission.logistics.services,
    }


@TaskTemplate()
def collect_submission_model(
    samples: SubmissionSamplesByIdModel,
    files: SubmissionFilesByIdModel,
    submission: SubmissionModel,
) -> SubmissionModel:
    submission.files = files
    submission.samples = samples
    return submission


# Core task templates


@TaskTemplate()
async def allocate_sequence_depot_submission_id(
    submission: SubmissionModel,
) -> SubmissionModel:
    request_return = await request_sequence_depot_submission_id(
        submission.logistics.services.sequence_depot.url,
        SubmissionToSequenceDepotRequestMapper(submission),
    )
    metadata = submission.metadata
    metadata.sequence_depot_submission_id = request_return.sequence_depot_submission_id

    # Assigning through the submission reruns its validators, deriving the status
    submission.metadata = metadata

    return submission


@TaskTemplate(iterate_over_data_files=True)
async def register_all_samples_with_biosamplevault(
    dataset: SubmissionSampleModel,
    *,
    metadata: SubmissionMetadataModel,
    services: ServicesModel,
) -> SubmissionSampleModel:
    sample = dataset
    bsv_submission = SampleAndMetadataToBioSampleVaultSubmissionMapper((sample, metadata))
    bsv_submission = await register_sample_with_biosamplevault(
        services.biosample_vault.url,
        bsv_submission,
    )
    sample.biosample_vault_sample_id = bsv_submission.biosample_vault_sample_id
    return sample


def _create_staging_url(
    file: SubmissionFileSchemaModel,
    metadata: SubmissionMetadataModel,
) -> FtpUrlModel:
    staging_uri = FtpUrlModel('ftps://seq-depot-staging')
    staging_uri.path // metadata.broker_id // metadata.local_submission_id // file.file_name
    return staging_uri


@TaskTemplate(iterate_over_data_files=True)
async def transfer_all_files(
    dataset: SubmissionFileSchemaModel,
    *,
    metadata: SubmissionMetadataModel,
    services: ServicesModel,
) -> SubmissionFileSchemaModel:
    file = dataset
    file.staging_storage_uri = _create_staging_url(file, metadata)
    status, error = await transfer_file(
        services.file_transfer.url,
        username=metadata.broker_id,
        source_uri=file.source_storage_uri,
        target_uri=file.staging_storage_uri,
    )
    file.transfer_status = status
    file.error = error

    return file


@TaskTemplate()
async def finalize_sequence_depot_submission(
    submission: SubmissionModel,
) -> SubmissionModel:
    assert submission.logistics.status.sequence_depot_submission_id_status == 'completed'
    assert submission.logistics.status.biosample_vault_status == 'completed'
    assert submission.logistics.status.transfer_status == 'completed'

    final_submission = FinalSubmissionModel(
        samples=submission.samples,
        files=submission.files,
        metadata=submission.metadata,
    )
    ok = await submit_final_submission_to_sequence_depot(
        submission.logistics.services.sequence_depot.url,
        final_submission,
    )
    assert ok
    submission.logistics.status.sequence_depot_submission_status = 'completed'

    return submission
