from omnipy.compute.task import TaskTemplate
from omnipy.data.model import Model
from omnipy.util.helpers import resolve

from .models import (
    BioSampleVaultSampleSubmissionSchema,
    FileAndMetadataToFileTransferRequestMapper,
    FileTransferResponseSchema,
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
    presubmit_api_url = submission.logistics.services.seq_depot.urls['presubmit']
    presubmit_request = SubmissionToSeqDepotPresubmitMapper(submission)

    response = await resolve(
        presubmit_request.post(
            presubmit_api_url,
            response_cls=Model[SeqDepotPresubmitSchema],
        )
    )

    with submission.updating():
        submission.metadata.seq_depot_submission_id = response.seq_depot_submission_id

    return submission


@TaskTemplate(iterate_over_data_files=True)
async def register_all_samples_with_biosamplevault(
    dataset: SubmissionSampleModel,
    *,
    metadata: SubmissionMetadataModel,
    services: ServicesModel,
) -> SubmissionSampleModel:
    sample = dataset
    samples_api_url = services.biosamplevault.urls['samples']
    sample_submission = SampleAndMetadataToBioSampleVaultSubmissionMapper((sample, metadata))

    response = await resolve(
        sample_submission.post(
            samples_api_url,
            response_cls=Model[BioSampleVaultSampleSubmissionSchema],
        )
    )

    sample.biosamplevault_sample_id = response.biosamplevault_sample_id

    return sample


@TaskTemplate(iterate_over_data_files=True)
async def transfer_all_files(
    dataset: SubmissionFileModel,
    *,
    metadata: SubmissionMetadataModel,
    services: ServicesModel,
) -> SubmissionFileModel:
    file = dataset
    staging_base_url = services.seq_depot.urls['staging']
    transfers_api_url = services.file_transfer.urls['transfers']
    transfer_request = FileAndMetadataToFileTransferRequestMapper(
        (file, metadata, staging_base_url)
    )

    response = await resolve(
        transfer_request.post(
            transfers_api_url,
            response_cls=Model[FileTransferResponseSchema],
        )
    )

    file.transfer_status = response.status
    file.error = response.error
    if response.status == 'completed':
        file.staging_storage_uri = response.target_uri

    return file


@TaskTemplate()
async def finalize_seq_depot_submission(
    submission: SubmissionModel,
) -> SubmissionModel:
    assert submission.logistics.status.seq_depot_submission_id_status == 'completed'
    assert submission.logistics.status.biosamplevault_status == 'completed'
    assert submission.logistics.status.file_transfer_status == 'completed'

    submissions_api_url = submission.logistics.services.seq_depot.urls['submissions']
    submission_payload = SeqDepotSubmissionPayloadModel(
        samples=submission.samples,
        files=submission.files,
        metadata=submission.metadata,
    )

    receipt = await resolve(
        submission_payload.post(
            submissions_api_url,
            response_cls=Model[SeqDepotSubmissionReceiptSchema],
        )
    )

    assert receipt.accepted
    submission.logistics.status.seq_depot_submission_status = 'completed'

    return submission
