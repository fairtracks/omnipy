import asyncio
from collections.abc import Mapping
from contextvars import ContextVar

from .models import (
    BioSampleVaultSampleSubmissionSchema,
    FinalSubmissionModel,
    FtpUrlModel,
    S3UrlModel,
    SequenceDepotSubmissionIdRequest,
    Status,
)


async def request_sequence_depot_submission_id(
    request: SequenceDepotSubmissionIdRequest,
) -> SequenceDepotSubmissionIdRequest:
    await asyncio.sleep(0)
    request.sequence_depot_submission_id = 'SQD:4021372983'
    return request


async def transfer_file(
    username: str,
    source_uri: S3UrlModel,
    target_uri: FtpUrlModel,
) -> tuple[Status, str | None]:
    await asyncio.sleep(0)
    return 'completed', None


async def register_sample_with_biosamplevault(
    request: BioSampleVaultSampleSubmissionSchema,
) -> BioSampleVaultSampleSubmissionSchema:
    await asyncio.sleep(0)
    sample_ids_mapping = biosample_vault_ids_mapping.get()
    request.biosample_vault_sample_id = sample_ids_mapping[request.local_sample_alias]
    return request


async def submit_final_submission_to_sequence_depot(submission: FinalSubmissionModel) -> bool:
    await asyncio.sleep(0)
    return True


biosample_vault_ids_mapping = ContextVar[Mapping[str, str]]('biosample_vault_ids')
