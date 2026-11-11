from typing import Annotated

import pytest

from omnipy.shared.enums.job import RunState

from .....engine.helpers.functions import assert_job_state
from .conftest import JsonRequest, MockService, ReceivedRequests
from .flows import broker_sequence_submission_flow, coordinate_external_file_transfer
from .models import SubmissionModel


def _sorted_by(received_requests: ReceivedRequests, field: str) -> ReceivedRequests:
    """Order requests sent concurrently, for comparison with expected requests."""

    def _field_value(request: JsonRequest) -> str:
        return str(request[field])

    return {
        path: sorted(requests, key=_field_value) for path, requests in received_requests.items()
    }


def test_submission_rejects_duplicate_file_role(
    samples: Annotated[list[dict[str, str]], pytest.fixture],
    files: Annotated[list[dict[str, str]], pytest.fixture],
    metadata: Annotated[dict[str, str], pytest.fixture],
) -> None:
    duplicate_read1_files = [*files, {**files[0], 'local_file_id': 'file-id-5'}]

    with pytest.raises(ValueError, match="Duplicate file role 'read1' for sample 'sample-a'"):
        SubmissionModel(
            samples=samples,
            files=duplicate_read1_files,
            metadata=metadata,
        )


def test_submission_rejects_duplicate_biosamplevault_sample_id(
    samples: Annotated[list[dict[str, str]], pytest.fixture],
    files: Annotated[list[dict[str, str]], pytest.fixture],
    metadata: Annotated[dict[str, str], pytest.fixture],
) -> None:
    samples_with_same_vault_id = [
        {**sample, 'biosamplevault_sample_id': 'BSV:80907461'} for sample in samples
    ]

    with pytest.raises(
        ValueError,
        match="BioSample Vault sample id 'BSV:80907461' is assigned to both sample 'sample-a' "
        "and 'sample-b'",
    ):
        SubmissionModel(
            samples=samples_with_same_vault_id,
            files=files,
            metadata=metadata,
        )


def test_submission_requires_file_pair_for_every_sample(
    samples: Annotated[list[dict[str, str]], pytest.fixture],
    files: Annotated[list[dict[str, str]], pytest.fixture],
    metadata: Annotated[dict[str, str], pytest.fixture],
) -> None:
    files_for_first_sample = [file for file in files if file['local_sample_id'] == 'Sample-A']

    with pytest.raises(
        ValueError,
        match="Sample 'sample-b' must have exactly two files \\(read1 and read2\\).",
    ):
        SubmissionModel(
            samples=samples,
            files=files_for_first_sample,
            metadata=metadata,
        )


@pytest.mark.usefixtures('runtime_all_engines')
async def test_sequence_submission_brokering(
    samples: Annotated[list[dict[str, str]], pytest.fixture],
    files: Annotated[list[dict[str, str]], pytest.fixture],
    metadata: Annotated[dict[str, str], pytest.fixture],
    services: Annotated[dict[str, dict[str, dict[str, str]]], pytest.fixture],
    seq_depot: Annotated[MockService, pytest.fixture],
    biosamplevault: Annotated[MockService, pytest.fixture],
    file_transfer: Annotated[MockService, pytest.fixture],
    expected_completed_submission: Annotated[dict[str, object], pytest.fixture],
    expected_seq_depot_requests: Annotated[ReceivedRequests, pytest.fixture],
    expected_biosamplevault_requests: Annotated[ReceivedRequests, pytest.fixture],
    expected_file_transfer_requests: Annotated[ReceivedRequests, pytest.fixture],
) -> None:
    submission = SubmissionModel(
        samples=samples,
        files=files,
        metadata=metadata,
        logistics={'services': services},
    )

    print()
    print('Input submission:')
    submission.full(width=160)

    brokering_flow = broker_sequence_submission_flow.apply()
    completed_submission = await brokering_flow(submission)

    assert completed_submission.to_data() == expected_completed_submission

    assert seq_depot.requests == expected_seq_depot_requests
    assert _sorted_by(biosamplevault.requests, 'local_sample_id') == (
        expected_biosamplevault_requests
    )
    assert _sorted_by(file_transfer.requests, 'source_uri') == expected_file_transfer_requests

    assert_job_state(brokering_flow, [RunState.FINISHED])

    print()
    print('Completed submission:')
    completed_submission.full(width=160)


_FAILING_SOURCE_URI = 's3://lab-sequences/sub-2026-alpha/sample-b_R2.fastq.gz'


@pytest.mark.usefixtures('runtime_all_engines')
@pytest.mark.parametrize('failing_source_uris', [(_FAILING_SOURCE_URI,)])
async def test_failed_file_transfer_is_recorded_without_staging_uri(
    samples: Annotated[list[dict[str, str]], pytest.fixture],
    files: Annotated[list[dict[str, str]], pytest.fixture],
    metadata: Annotated[dict[str, str], pytest.fixture],
    services: Annotated[dict[str, dict[str, dict[str, str]]], pytest.fixture],
) -> None:
    submission = SubmissionModel(
        samples=samples,
        files=files,
        metadata=metadata,
        logistics={'services': services},
    )

    transfer_flow = coordinate_external_file_transfer.apply()
    transferred_submission = await transfer_flow(submission)

    for file in transferred_submission.files.values():
        if str(file.source_storage_uri) == _FAILING_SOURCE_URI:
            assert file.transfer_status == 'failed'
            assert file.error == 'Source file not found'
            assert file.staging_storage_uri is None
        else:
            assert file.transfer_status == 'completed'
            assert file.error is None
            assert file.staging_storage_uri is not None

    assert transferred_submission.logistics.status.file_transfer_status == 'failed'

    assert_job_state(transfer_flow, [RunState.FINISHED])
