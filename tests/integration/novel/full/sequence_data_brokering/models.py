from typing import Literal

from omnipy.data._typing.helpers import mimics
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
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
    )(
        _normalize_alias)


class SubmissionFileSchema(SubmissionSchemaBase):
    local_submission_alias: str
    local_sample_alias: str
    file_id: str
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
    )(
        _normalize_alias)


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
    )(
        _normalize_alias)

    @pyd.validator('local_sample_aliases', pre=True, allow_reuse=True)
    def _normalize_sample_alias_list(cls, values: list[str]) -> list[str]:
        return [_normalize_alias(value) for value in values]


@mimics(SubmissionMetadataSchema)
class SubmissionMetadataModel(Model[SubmissionMetadataSchema]):
    ...


@mimics(SubmissionSampleSchema)
class SubmissionSampleModel(Model[SubmissionSampleSchema]):
    ...


class SubmissionSamplesDataset(Dataset[SubmissionSampleModel]):
    ...


@mimics(SubmissionFileSchema)
class SubmissionFileSchemaModel(Model[SubmissionFileSchema]):
    ...


class SubmissionFilesDataset(Dataset[SubmissionFileSchemaModel]):
    ...


class SubmissionRecord(pyd.BaseModel):
    samples: SubmissionSamplesDataset
    files: SubmissionFilesDataset
    metadata: SubmissionMetadataModel


@mimics(SubmissionRecord)
class SubmissionModel(Model[SubmissionRecord]):
    ...
