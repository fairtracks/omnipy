"""Clients for the external services of the sequence submission dataflow.

Each client function posts a JSON request to an HTTP endpoint of its service and
parses the JSON response according to the service's own request/response schemas.
In the tests, the services are simulated by local mock HTTP endpoints.
"""

from omnipy.components.remote.models import HttpUrlModel
from omnipy.data.model import Model
from omnipy.util.helpers import resolve

from .models import (
    BioSampleVaultSampleSubmissionSchema,
    FileTransferRequest,
    FileTransferResponse,
    FinalSubmissionModel,
    FtpUrlModel,
    S3UrlModel,
    SequenceDepotSubmissionIdRequest,
    SequenceDepotSubmissionReceipt,
    Status,
)


def _endpoint_url(service_url: HttpUrlModel, endpoint: str) -> HttpUrlModel:
    endpoint_url = HttpUrlModel(service_url)
    endpoint_url.path /= endpoint
    return endpoint_url


async def request_sequence_depot_submission_id(
    sequence_depot_url: HttpUrlModel,
    request: SequenceDepotSubmissionIdRequest,
) -> SequenceDepotSubmissionIdRequest:
    response = await resolve(
        Model[SequenceDepotSubmissionIdRequest](request).post(
            _endpoint_url(sequence_depot_url, 'submission-ids'),
            response_cls=Model[SequenceDepotSubmissionIdRequest],
        )
    )
    return response.content


async def transfer_file(
    file_transfer_url: HttpUrlModel,
    username: str,
    source_uri: S3UrlModel,
    target_uri: FtpUrlModel,
) -> tuple[Status, str | None]:
    request = FileTransferRequest(username=username, source_uri=source_uri, target_uri=target_uri)
    response = await resolve(
        Model[FileTransferRequest](request).post(
            _endpoint_url(file_transfer_url, 'transfers'),
            response_cls=Model[FileTransferResponse],
        )
    )
    return response.status, response.error


async def register_sample_with_biosamplevault(
    biosample_vault_url: HttpUrlModel,
    request: BioSampleVaultSampleSubmissionSchema,
) -> BioSampleVaultSampleSubmissionSchema:
    response = await resolve(
        Model[BioSampleVaultSampleSubmissionSchema](request).post(
            _endpoint_url(biosample_vault_url, 'samples'),
            response_cls=Model[BioSampleVaultSampleSubmissionSchema],
        )
    )
    return response.content


async def submit_final_submission_to_sequence_depot(
    sequence_depot_url: HttpUrlModel,
    submission: FinalSubmissionModel,
) -> bool:
    receipt = await resolve(
        submission.post(
            _endpoint_url(sequence_depot_url, 'submissions'),
            response_cls=Model[SequenceDepotSubmissionReceipt],
        )
    )
    return receipt.accepted
