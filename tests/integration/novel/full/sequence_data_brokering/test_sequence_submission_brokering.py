from typing import Annotated

import pytest

from omnipy.components.remote.models import HttpUrlModel
from omnipy.shared.enums.job import RunState

from .....engine.helpers.functions import assert_job_state
from .conftest import JsonRequest, ReceivedRequests
from .flows import broker_sequence_submission_flow
from .models import (
    SubmissionFilesDataset,
    SubmissionMetadataModel,
    SubmissionModel,
    SubmissionRecord,
    SubmissionSamplesDataset,
)


def _sorted_by(received_requests: ReceivedRequests, field: str) -> ReceivedRequests:
    """Order requests sent concurrently, for comparison with expected requests."""

    def _field_value(request: JsonRequest) -> str:
        return str(request[field])

    return {
        path: sorted(requests, key=_field_value) for path, requests in received_requests.items()
    }


def test_submission_rejects_duplicate_file_role(
    samples: Annotated[dict[str, dict[str, str]], pytest.fixture],
    files: Annotated[dict[str, dict[str, str]], pytest.fixture],
    metadata: Annotated[dict[str, str], pytest.fixture],
) -> None:
    duplicate_read1_files = {
        **files,
        'file-id-5': {
            **files['file-id-1'],
            'file_id': 'file-id-5',
        },
    }

    with pytest.raises(ValueError, match="Duplicate file role 'read1' for sample 'sample-a'"):
        SubmissionRecord(
            samples=SubmissionSamplesDataset(samples),
            files=SubmissionFilesDataset(duplicate_read1_files),
            metadata=SubmissionMetadataModel(metadata),
        )


def test_submission_requires_file_pair_for_every_sample(
    samples: Annotated[dict[str, dict[str, str]], pytest.fixture],
    files: Annotated[dict[str, dict[str, str]], pytest.fixture],
    metadata: Annotated[dict[str, str], pytest.fixture],
) -> None:
    files_for_first_sample = {
        dataset_key: file
        for dataset_key, file in files.items()
        if file['local_sample_alias'] == 'Sample-A'
    }

    with pytest.raises(
        ValueError,
        match="Sample 'sample-b' must have exactly two files \\(read1 and read2\\).",
    ):
        SubmissionRecord(
            samples=SubmissionSamplesDataset(samples),
            files=SubmissionFilesDataset(files_for_first_sample),
            metadata=SubmissionMetadataModel(metadata),
        )


@pytest.mark.usefixtures('runtime_all_engines')
async def test_sequence_submission_brokering(
    samples: Annotated[dict[str, dict[str, str]], pytest.fixture],
    files: Annotated[dict[str, dict[str, str]], pytest.fixture],
    metadata: Annotated[dict[str, str], pytest.fixture],
    sequence_depot_url: Annotated[HttpUrlModel, pytest.fixture],
    biosample_vault_url: Annotated[HttpUrlModel, pytest.fixture],
    file_transfer_url: Annotated[HttpUrlModel, pytest.fixture],
    sequence_depot_requests: Annotated[ReceivedRequests, pytest.fixture],
    biosample_vault_requests: Annotated[ReceivedRequests, pytest.fixture],
    file_transfer_requests: Annotated[ReceivedRequests, pytest.fixture],
    expected_sequence_depot_submission_payload: Annotated[dict[str, object], pytest.fixture],
    expected_sequence_depot_requests: Annotated[ReceivedRequests, pytest.fixture],
    expected_biosample_vault_requests: Annotated[ReceivedRequests, pytest.fixture],
    expected_file_transfer_requests: Annotated[ReceivedRequests, pytest.fixture],
) -> None:
    submission = SubmissionModel(samples=samples, files=files, metadata=metadata)

    print()
    print('Input submission:')
    submission.full(width=160)

    brokering_flow = broker_sequence_submission_flow.apply()
    completed_submission = await brokering_flow(
        submission,
        sequence_depot_url=sequence_depot_url,
        biosample_vault_url=biosample_vault_url,
        file_transfer_url=file_transfer_url,
    )

    assert completed_submission.to_data() == expected_sequence_depot_submission_payload

    assert sequence_depot_requests == expected_sequence_depot_requests
    assert _sorted_by(biosample_vault_requests, 'local_sample_alias') == (
        expected_biosample_vault_requests
    )
    assert _sorted_by(file_transfer_requests, 'source_uri') == expected_file_transfer_requests

    assert_job_state(brokering_flow, [RunState.FINISHED])

    print()
    print('Completed submission:')
    completed_submission.full(width=160)
