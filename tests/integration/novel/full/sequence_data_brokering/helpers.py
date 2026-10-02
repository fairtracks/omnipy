from collections import Counter
from typing import cast

from .models import (SubmissionFilesDataset,
                     SubmissionMetadataModel,
                     SubmissionModel,
                     SubmissionSamplesDataset)


def clone_submission(submission: SubmissionModel) -> SubmissionModel:
    return SubmissionModel(
        samples=submission.samples,
        files=submission.files,
        metadata=submission.metadata,
    )


def append_workflow_event(submission: SubmissionModel, event: str) -> SubmissionModel:
    submission.metadata.workflow_events.append(event)
    return submission


def validate_submission_linkage(submission: SubmissionModel) -> None:
    samples = cast(SubmissionSamplesDataset, submission.samples)
    files = cast(SubmissionFilesDataset, submission.files)
    metadata = cast(SubmissionMetadataModel, submission.metadata)

    submission_alias = metadata.local_submission_alias
    sample_aliases = [sample.local_sample_alias for sample in submission.samples.values()]
    file_sample_aliases = [file_row.local_sample_alias for file_row in submission.files.values()]

    assert all(sample.local_submission_alias == submission_alias for sample in samples.values())
    assert all(file_row.local_submission_alias == submission_alias for file_row in files.values())
    assert sorted(sample_aliases) == sorted(metadata.local_sample_aliases)
    assert set(file_sample_aliases) == set(sample_aliases)

    file_roles_per_sample = Counter(
        (file_row.local_sample_alias, file_row.file_role) for file_row in files.values())
    assert all(
        file_roles_per_sample[(sample_alias, 'read1')] == 1 for sample_alias in sample_aliases)
    assert all(
        file_roles_per_sample[(sample_alias, 'read2')] == 1 for sample_alias in sample_aliases)


def assert_submission_ready_for_final_submission(submission: SubmissionModel) -> None:
    metadata = cast(SubmissionMetadataModel, submission.metadata)
    samples = cast(SubmissionSamplesDataset, submission.samples)

    assert metadata.sequence_depot_submission_id is not None
    # assert metadata.transfer_status == 'completed-external'
    assert all(sample.biosamplevault_sample_id is not None for sample in samples.values())
