from omnipy.compute.task import TaskTemplate
from omnipy.data.model import Model
from omnipy.util.helpers import resolve

from .models import (
    BioSampleVaultSampleSubmissionSchema,
    FileTransferRequestSchema,
    FileTransferResponseSchema,
    FtpUrlModel,
    SampleAndMetadataToBioSampleVaultSubmissionMapper,
    SeqDepotPresubmitSchema,
    SeqDepotSubmissionPayloadModel,
    SeqDepotSubmissionReceiptSchema,
    ServicesModel,
    SubmissionFileModel,
    SubmissionFilesDataset,
    SubmissionMetadataModel,
    SubmissionModel,
    SubmissionSampleModel,
    SubmissionSamplesDataset,
    SubmissionToSeqDepotPresubmitMapper,
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
    samples: SubmissionSamplesDataset,
    files: SubmissionFilesDataset,
    submission: SubmissionModel,
) -> SubmissionModel:
    submission.files = files
    submission.samples = samples
    return submission


# Core task templates


@TaskTemplate()
async def allocate_seq_depot_submission_id(
    submission: SubmissionModel,
) -> SubmissionModel:
    response = await resolve(
        SubmissionToSeqDepotPresubmitMapper(submission).post(
            submission.logistics.services.seq_depot.urls['presubmit'],
            response_cls=Model[SeqDepotPresubmitSchema],
        )
    )
    metadata = submission.metadata
    metadata.seq_depot_submission_id = response.seq_depot_submission_id

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
    response = await resolve(
        SampleAndMetadataToBioSampleVaultSubmissionMapper((sample, metadata)).post(
            services.biosamplevault.urls['samples'],
            response_cls=Model[BioSampleVaultSampleSubmissionSchema],
        )
    )
    sample.biosamplevault_sample_id = response.biosamplevault_sample_id
    return sample


def _create_staging_uri(
    file: SubmissionFileModel,
    metadata: SubmissionMetadataModel,
    services: ServicesModel,
) -> FtpUrlModel:
    staging_uri = FtpUrlModel(services.seq_depot.urls['staging'])
    # The local sample id keeps files with the same name from different samples apart
    (
        staging_uri.path
        // metadata.broker_id
        // metadata.local_submission_id
        // file.local_sample_id
        // file.file_name
    )
    return staging_uri


@TaskTemplate(iterate_over_data_files=True)
async def transfer_all_files(
    dataset: SubmissionFileModel,
    *,
    metadata: SubmissionMetadataModel,
    services: ServicesModel,
) -> SubmissionFileModel:
    file = dataset
    file.staging_storage_uri = _create_staging_uri(file, metadata, services)
    request = FileTransferRequestSchema(
        username=metadata.broker_id,
        source_uri=file.source_storage_uri,
        target_uri=file.staging_storage_uri,
    )
    response = await resolve(
        Model[FileTransferRequestSchema](request).post(
            services.file_transfer.urls['transfers'],
            response_cls=Model[FileTransferResponseSchema],
        )
    )
    file.transfer_status = response.status
    file.error = response.error

    return file


@TaskTemplate()
async def finalize_seq_depot_submission(
    submission: SubmissionModel,
) -> SubmissionModel:
    assert submission.logistics.status.seq_depot_submission_id_status == 'completed'
    assert submission.logistics.status.biosamplevault_status == 'completed'
    assert submission.logistics.status.file_transfer_status == 'completed'

    submission_payload = SeqDepotSubmissionPayloadModel(
        samples=submission.samples,
        files=submission.files,
        metadata=submission.metadata,
    )
    receipt = await resolve(
        submission_payload.post(
            submission.logistics.services.seq_depot.urls['submissions'],
            response_cls=Model[SeqDepotSubmissionReceiptSchema],
        )
    )
    assert receipt.accepted
    submission.logistics.status.seq_depot_submission_status = 'completed'

    return submission
