from omnipy.compute.task import TaskTemplate

from .models import (FinalSubmissionModel,
                     FtpUrlModel,
                     SampleAndMetadataToBioSampleVaultSubmissionMapper,
                     SubmissionFileSchemaModel,
                     SubmissionFilesDataset,
                     SubmissionMetadataModel,
                     SubmissionModel,
                     SubmissionSampleModel,
                     SubmissionSamplesDataset,
                     SubmissionToSequenceDepotRequestMapper)
from .services import (register_sample_with_biosamplevault,
                       request_sequence_depot_submission_id,
                       submit_final_submission_to_sequence_depot,
                       transfer_file)

# Helper task templates


@TaskTemplate()
def explode_submission_model(submission: SubmissionModel) -> dict[str, object]:
    return {
        'samples': submission.samples,
        'files': submission.files,
        'metadata': submission.metadata,
    }


@TaskTemplate()
def collect_submission_model(
    samples: SubmissionSamplesDataset,
    files: SubmissionFilesDataset,
    submission: SubmissionModel,
) -> SubmissionModel:
    submission.files = files
    submission.samples = samples
    return submission


# Core task templates


@TaskTemplate()
async def allocate_sequence_depot_submission_id(submission: SubmissionModel) -> SubmissionModel:
    request_return = await request_sequence_depot_submission_id(
        SubmissionToSequenceDepotRequestMapper(submission),)
    submission.metadata.sequence_depot_submission_id = request_return.sequence_depot_submission_id

    return submission


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


def _create_staging_url(
    file: SubmissionFileSchemaModel,
    metadata: SubmissionMetadataModel,
) -> FtpUrlModel:
    staging_uri = FtpUrlModel('ftps://seq-depot-staging')
    staging_uri.path // metadata.broker_id // metadata.local_submission_alias // file.file_name
    return staging_uri


@TaskTemplate(iterate_over_data_files=True)
async def transfer_all_files(
    dataset: SubmissionFileSchemaModel,
    *,
    metadata: SubmissionMetadataModel,
) -> SubmissionFileSchemaModel:
    file = dataset
    file.staging_storage_uri = _create_staging_url(file, metadata)
    status, error = await transfer_file(username=metadata.broker_id,
                                        source_uri=file.source_storage_uri,
                                        target_uri=file.staging_storage_uri)
    file.transfer_status = status
    file.error = error

    return file


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
