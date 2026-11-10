"""Clients for the external services of the sequence submission dataflow.

Each client function posts a JSON request to an HTTP endpoint of its service and
parses the JSON response according to the service's own request/response schemas.
In the tests, the services are simulated by local mock HTTP endpoints.
"""

from typing import TypeVar

from omnipy.components.json.models import JsonModel
from omnipy.components.remote.models import HttpUrlModel
from omnipy.components.remote.tasks import post_json_to_api_endpoint
from omnipy.data.model import Model
import omnipy.util.pydantic as pyd

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

_RequestSchemaT = TypeVar('_RequestSchemaT', bound=pyd.BaseModel)
_ResponseSchemaT = TypeVar('_ResponseSchemaT', bound=pyd.BaseModel)

_post_json_to_service_endpoint = post_json_to_api_endpoint.refine(
    name='post_json_to_service_endpoint',
    iterate_over_data_files=False,
    output_dataset_cls=None,
)


def _endpoint_url(service_url: HttpUrlModel, endpoint: str) -> HttpUrlModel:
    endpoint_url = HttpUrlModel(service_url)
    endpoint_url.path /= endpoint
    return endpoint_url


async def _post_to_service(
    endpoint_url: HttpUrlModel,
    request: Model[_RequestSchemaT],
    response_schema: type[_ResponseSchemaT],
) -> _ResponseSchemaT:
    # The static signature of the refined template still declares the dataset-iterating form
    response = await _post_json_to_service_endpoint(  # pyright: ignore[reportGeneralTypeIssues]
        endpoint_url,  # pyright: ignore[reportArgumentType]
        JsonModel(request.to_data()),
    )
    return response_schema.parse_obj(response.to_data())


async def request_sequence_depot_submission_id(
    sequence_depot_url: HttpUrlModel,
    request: SequenceDepotSubmissionIdRequest,
) -> SequenceDepotSubmissionIdRequest:
    return await _post_to_service(
        _endpoint_url(sequence_depot_url, 'submission-ids'),
        Model[SequenceDepotSubmissionIdRequest](request),
        SequenceDepotSubmissionIdRequest,
    )


async def transfer_file(
    file_transfer_url: HttpUrlModel,
    username: str,
    source_uri: S3UrlModel,
    target_uri: FtpUrlModel,
) -> tuple[Status, str | None]:
    response = await _post_to_service(
        _endpoint_url(file_transfer_url, 'transfers'),
        Model[FileTransferRequest](
            FileTransferRequest(username=username, source_uri=source_uri, target_uri=target_uri)
        ),
        FileTransferResponse,
    )
    return response.status, response.error


async def register_sample_with_biosamplevault(
    biosample_vault_url: HttpUrlModel,
    request: BioSampleVaultSampleSubmissionSchema,
) -> BioSampleVaultSampleSubmissionSchema:
    return await _post_to_service(
        _endpoint_url(biosample_vault_url, 'samples'),
        Model[BioSampleVaultSampleSubmissionSchema](request),
        BioSampleVaultSampleSubmissionSchema,
    )


async def submit_final_submission_to_sequence_depot(
    sequence_depot_url: HttpUrlModel,
    submission: FinalSubmissionModel,
) -> bool:
    receipt = await _post_to_service(
        _endpoint_url(sequence_depot_url, 'submissions'),
        submission,
        SequenceDepotSubmissionReceipt,
    )
    return receipt.accepted
