from collections import Counter
from typing import cast
from typing import Literal

import omnipy as om
import omnipy.util.pydantic as pyd


def _normalize_alias(value: str) -> str:
    return value.strip().lower()


class SubmissionSchemaBase(pyd.BaseModel):
    class Config:
        extra = pyd.Extra.forbid


class SubmissionSampleSchema(SubmissionSchemaBase):
    local_submission_alias: str
    local_sample_alias: str
    specimen_type: str
    collection_site: str
    sampled_at: str
    biosamplevault_sample_id: str | None = None

    _normalize_alias_fields = pyd.validator(
        'local_submission_alias',
        'local_sample_alias',
        pre=True,
        allow_reuse=True,
    )(_normalize_alias)


class SubmissionFileSchema(SubmissionSchemaBase):
    local_submission_alias: str
    local_sample_alias: str
    file_role: Literal['read1', 'read2']
    file_name: str
    storage_uri: str
    md5: str
    transfer_ticket: str | None = None

    _normalize_alias_fields = pyd.validator(
        'local_submission_alias',
        'local_sample_alias',
        pre=True,
        allow_reuse=True,
    )(_normalize_alias)


class SubmissionMetadataSchema(SubmissionSchemaBase):
    local_submission_alias: str
    local_sample_aliases: list[str]
    project_code: str
    study_title: str
    release_date: str
    submission_checklist_version: str
    transfer_status: Literal['pending', 'completed-external'] = 'pending'
    archive_status: Literal['draft', 'files-verified', 'samples-registered', 'submitted'] = 'draft'
    sequence_depot_submission_id: str | None = None
    external_transfer_ticket: str | None = None
    final_receipt_message: str | None = None
    workflow_events: list[str] = pyd.Field(default_factory=list)

    _normalize_submission_alias = pyd.validator(
        'local_submission_alias',
        pre=True,
        allow_reuse=True,
    )(_normalize_alias)

    @pyd.validator('local_sample_aliases', pre=True, allow_reuse=True)
    def _normalize_sample_alias_list(cls, values: list[str]) -> list[str]:
        return [_normalize_alias(value) for value in values]


class SubmissionMetadataModel(om.Model[SubmissionMetadataSchema]):
    ...


class SubmissionSamplesTable(om.TableOfPydanticRecordsModel[SubmissionSampleSchema]):
    ...


class SubmissionFilesTable(om.TableOfPydanticRecordsModel[SubmissionFileSchema]):
    ...


class SubmissionPackage(
    om.Dataset[SubmissionSamplesTable | SubmissionFilesTable | SubmissionMetadataModel]):
    ...


def build_submission_package(
    *,
    submission_samples: list[dict[str, object]],
    submission_files: list[dict[str, object]],
    submission_metadata: dict[str, object],
) -> SubmissionPackage:
    return SubmissionPackage(
        submission_samples=SubmissionSamplesTable(submission_samples),
        submission_files=SubmissionFilesTable(submission_files),
        submission_metadata=SubmissionMetadataModel(submission_metadata),
    )


def clone_submission_package(package: SubmissionPackage) -> SubmissionPackage:
    return build_submission_package(
        submission_samples=cast(list[dict[str, object]], package['submission_samples'].to_data()),
        submission_files=cast(list[dict[str, object]], package['submission_files'].to_data()),
        submission_metadata=cast(dict[str, object], package['submission_metadata'].to_data()),
    )


def append_workflow_event(package: SubmissionPackage, event: str) -> SubmissionPackage:
    metadata = cast(dict[str, object], package['submission_metadata'].to_data())
    updated_events = [*cast(list[str], metadata['workflow_events']), event]
    updated_metadata = metadata | {'workflow_events': updated_events}

    return build_submission_package(
        submission_samples=cast(list[dict[str, object]], package['submission_samples'].to_data()),
        submission_files=cast(list[dict[str, object]], package['submission_files'].to_data()),
        submission_metadata=updated_metadata,
    )


def update_submission_metadata(
    package: SubmissionPackage,
    **metadata_updates: object,
) -> SubmissionPackage:
    metadata = cast(dict[str, object], package['submission_metadata'].to_data())
    updated_metadata = metadata | metadata_updates

    return build_submission_package(
        submission_samples=cast(list[dict[str, object]], package['submission_samples'].to_data()),
        submission_files=cast(list[dict[str, object]], package['submission_files'].to_data()),
        submission_metadata=updated_metadata,
    )


def update_submission_samples(
    package: SubmissionPackage,
    submission_samples: list[dict[str, object]],
) -> SubmissionPackage:
    return build_submission_package(
        submission_samples=submission_samples,
        submission_files=cast(list[dict[str, object]], package['submission_files'].to_data()),
        submission_metadata=cast(dict[str, object], package['submission_metadata'].to_data()),
    )


def update_submission_files(
    package: SubmissionPackage,
    submission_files: list[dict[str, object]],
) -> SubmissionPackage:
    return build_submission_package(
        submission_samples=cast(list[dict[str, object]], package['submission_samples'].to_data()),
        submission_files=submission_files,
        submission_metadata=cast(dict[str, object], package['submission_metadata'].to_data()),
    )


def validate_submission_linkage(package: SubmissionPackage) -> None:
    samples = cast(list[dict[str, object]], package['submission_samples'].to_data())
    files = cast(list[dict[str, object]], package['submission_files'].to_data())
    metadata = cast(dict[str, object], package['submission_metadata'].to_data())

    submission_alias = cast(str, metadata['local_submission_alias'])
    sample_aliases = [cast(str, sample['local_sample_alias']) for sample in samples]
    file_sample_aliases = [cast(str, file_row['local_sample_alias']) for file_row in files]

    assert all(sample['local_submission_alias'] == submission_alias for sample in samples)
    assert all(file_row['local_submission_alias'] == submission_alias for file_row in files)
    assert sorted(sample_aliases) == sorted(cast(list[str], metadata['local_sample_aliases']))
    assert set(file_sample_aliases) == set(sample_aliases)

    file_roles_per_sample = Counter(
        (cast(str, file_row['local_sample_alias']), cast(str, file_row['file_role']))
        for file_row in files)
    assert all(file_roles_per_sample[(sample_alias, 'read1')] == 1 for sample_alias in sample_aliases)
    assert all(file_roles_per_sample[(sample_alias, 'read2')] == 1 for sample_alias in sample_aliases)


def assert_submission_ready_for_final_submission(package: SubmissionPackage) -> None:
    metadata = cast(dict[str, object], package['submission_metadata'].to_data())
    samples = cast(list[dict[str, object]], package['submission_samples'].to_data())

    assert metadata['sequence_depot_submission_id'] is not None
    assert metadata['transfer_status'] == 'completed-external'
    assert all(sample['biosamplevault_sample_id'] is not None for sample in samples)
