from collections import defaultdict
from typing import Literal, TypeAlias, TypedDict

from omnipy.components.general.models import ConverterModel
from omnipy.components.raw.models import DateModel
from omnipy.components.remote.models import HostUrlModel
from omnipy.data._typing.helpers import mimics
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
import omnipy.util.pydantic as pyd

StrippedUpperStr: TypeAlias = pyd.constr(  # type: ignore[valid-type]
    strip_whitespace=True, to_upper=True)

StrippedLowerStr: TypeAlias = pyd.constr(  # type: ignore[valid-type]
    strip_whitespace=True, to_lower=True)

_hex_regex = r'^[0-9a-f]+$'

Md5Str: TypeAlias = pyd.constr(  # type: ignore[valid-type]
    strip_whitespace=True,
    to_lower=True,
    regex=_hex_regex,
    min_length=32,
    max_length=32,
)

_safe_filename_regexp = r'^[^\\/:*?"<>|]*$'

FileName: TypeAlias = pyd.constr(  # type: ignore[valid-type]
    strip_whitespace=True,
    regex=_safe_filename_regexp,
    max_length=255,
)


class S3UrlModel(HostUrlModel):
    @classmethod
    def _get_scheme_filter(cls) -> set[str]:
        return {'s3'}


class FtpUrlModel(HostUrlModel):
    @classmethod
    def _get_scheme_filter(cls) -> set[str]:
        return {'ftp', 'ftps'}


FileRole = Literal['read1', 'read2']
Status = Literal['N/A', 'pending', 'failed', 'completed']


class SubmissionSampleSchema(pyd.BaseModel):
    local_sample_alias: StrippedLowerStr
    specimen_type: str
    collection_site: str
    sampled_at: DateModel
    biosample_vault_sample_id: StrippedUpperStr | None = None


@mimics(SubmissionSampleSchema)
class SubmissionSampleModel(Model[SubmissionSampleSchema]):
    ...


class SubmissionSamplesDataset(Dataset[SubmissionSampleModel]):
    ...


class SubmissionFileSchema(pyd.BaseModel):
    file_id: StrippedLowerStr
    local_sample_alias: StrippedLowerStr
    file_role: FileRole
    md5: Md5Str
    source_storage_uri: S3UrlModel
    staging_storage_uri: FtpUrlModel | None = None
    file_name: FileName = pyd.Field(default='')
    transfer_status: Status = 'pending'
    error: str | None = None

    @pyd.validator('file_name')
    def _extract_file_name_from_source_storage_uri(cls, file_name: str, values: dict) -> str:
        if not file_name and 'source_storage_uri' in values:
            file_name = values['source_storage_uri'].path.name
        return file_name


@mimics(SubmissionFileSchema)
class SubmissionFileSchemaModel(Model[SubmissionFileSchema]):
    ...


class SubmissionFilesDataset(Dataset[SubmissionFileSchemaModel]):
    ...


class SubmissionMetadataSchema(pyd.BaseModel):
    broker_id: StrippedLowerStr
    local_submission_alias: StrippedLowerStr
    project_code: StrippedLowerStr
    study_title: str
    release_date: DateModel
    submission_checklist_version: str
    sequence_depot_submission_id: str | None = None


@mimics(SubmissionMetadataSchema)
class SubmissionMetadataModel(Model[SubmissionMetadataSchema]):
    ...


class SubmissionStatusSchema(pyd.BaseModel):
    sequence_depot_submission_id_status: Status = 'pending'
    biosample_vault_status: Status = 'pending'
    transfer_status: Status = 'pending'
    sequence_depot_submission_status: Status = 'pending'


@mimics(SubmissionStatusSchema)
class SubmissionStatusModel(Model[SubmissionStatusSchema]):
    ...


class _SubmissionRecordDict(TypedDict):
    samples: SubmissionSamplesDataset
    files: SubmissionFilesDataset
    metadata: SubmissionMetadataModel
    status: SubmissionStatusModel


class SubmissionRecord(pyd.BaseModel):
    samples: SubmissionSamplesDataset
    files: SubmissionFilesDataset
    metadata: SubmissionMetadataModel
    status: SubmissionStatusModel = pyd.Field(default_factory=SubmissionStatusModel)

    @pyd.validator('files')
    def _two_reads_per_sample(
        cls,
        files: SubmissionFilesDataset,
    ) -> SubmissionFilesDataset:
        file_roles_per_sample: defaultdict[str, set[FileRole]] = defaultdict(set)

        for file in files.values():
            key = (file.local_sample_alias, file.file_role)
            if key in file_roles_per_sample[file.local_sample_alias]:
                raise ValueError(
                    f"Duplicate file role '{file.file_role}' for sample '{file.local_sample_alias}'"
                )
            file_roles_per_sample[file.local_sample_alias].add(file.file_role)

        for sample_alias in file_roles_per_sample:
            assert len(file_roles_per_sample[sample_alias]) == 2, (
                f"Sample '{sample_alias}' must have exactly two files (read1 and read2).")

        return files

    # TODO: Consider general support for remote key validation in Models of
    #       of Pydantic models containing datasets.

    @pyd.validator('files')
    def _file_sample_aliases_exist(
        cls,
        files: SubmissionFilesDataset,
        values: _SubmissionRecordDict,
    ) -> SubmissionFilesDataset:
        sample_aliases = {sample.local_sample_alias for sample in values['samples'].values()}
        for file in files.values():
            if file.local_sample_alias not in sample_aliases:
                raise ValueError(f'File "{file.file_id}" has local_sample_alias '
                                 f'"{file.local_sample_alias}" which does not match any '
                                 f'sample in the submission.')
        return files


class SubmissionRecordWithStatus(SubmissionRecord):
    status: SubmissionStatusModel = pyd.Field(default_factory=SubmissionStatusModel)

    # TODO: Redesign _update_sequence_depot_submission_id_status,
    #       _update_transfer_status and _update_biosample_vault_status as
    #       @computed_fields in Pydantic v2
    @pyd.validator('status')
    def _update_sequence_depot_submission_id_status(
        cls,
        status: SubmissionStatusModel,
        values: _SubmissionRecordDict,
    ) -> SubmissionStatusModel:
        if values['metadata'].sequence_depot_submission_id is not None:
            status.sequence_depot_submission_id_status = 'completed'
        else:
            status.sequence_depot_submission_id_status = 'pending'

        return status

    @pyd.validator('status')
    def _update_transfer_status(
        cls,
        status: SubmissionStatusModel,
        values: _SubmissionRecordDict,
    ) -> SubmissionStatusModel:
        all_files_transfer_status: set[Status] = {
            file.transfer_status for file in values['files'].values()
        }
        if len(all_files_transfer_status) == 0:
            status.transfer_status = 'N/A'
        elif 'failed' in all_files_transfer_status:
            status.transfer_status = 'failed'
        elif 'pending' in all_files_transfer_status:
            status.transfer_status = 'pending'
        else:
            status.transfer_status = 'completed'

        return status

    @pyd.validator('status')
    def _update_biosample_vault_status(
        cls,
        status: SubmissionStatusModel,
        values: dict,
    ) -> SubmissionStatusModel:
        samples = values.get('samples', {}).values()
        all_samples_biosample_vault_ids: set[StrippedUpperStr] = {
            sample.biosample_vault_sample_id
            for sample in samples
            if sample.biosample_vault_sample_id is not None
        }
        if len(samples) == 0:
            status.biosample_vault_status = 'N/A'
        elif len(all_samples_biosample_vault_ids) == len(samples):
            status.biosample_vault_status = 'completed'
        else:
            status.biosample_vault_status = 'pending'

        return status


@mimics(SubmissionRecordWithStatus)
class SubmissionModel(Model[SubmissionRecordWithStatus]):
    ...


@mimics(SubmissionRecord)
class FinalSubmissionModel(Model[SubmissionRecord]):
    ...


class SequenceDepotSubmissionIdRequest(pyd.BaseModel):
    local_submission_alias: str
    project_code: str
    sequence_depot_submission_id: str | None = None


@mimics(SequenceDepotSubmissionIdRequest)
class SubmissionToSequenceDepotRequestMapper(ConverterModel[
        SubmissionModel,
        SequenceDepotSubmissionIdRequest,
]):
    @classmethod
    def _convert(cls, data: SubmissionModel) -> SequenceDepotSubmissionIdRequest:
        return SequenceDepotSubmissionIdRequest(
            local_submission_alias=data.metadata.local_submission_alias,
            project_code=data.metadata.project_code,
        )


class BioSampleVaultSampleSubmissionSchema(pyd.BaseModel):
    broker_id: StrippedLowerStr
    project_code: StrippedLowerStr
    study_title: str
    local_sample_alias: StrippedLowerStr
    specimen_type: str
    geolocation: str
    sampling_date: DateModel
    biosample_vault_sample_id: StrippedUpperStr | None = None


@mimics(BioSampleVaultSampleSubmissionSchema)
class SampleAndMetadataToBioSampleVaultSubmissionMapper(ConverterModel[
        Model[tuple[SubmissionSampleModel, SubmissionMetadataModel]],
        BioSampleVaultSampleSubmissionSchema,
]):
    @classmethod
    def _convert(
        cls, data: Model[tuple[SubmissionSampleModel, SubmissionMetadataModel]]
    ) -> BioSampleVaultSampleSubmissionSchema:
        sample, metadata = data
        return BioSampleVaultSampleSubmissionSchema(
            broker_id=metadata.broker_id,
            project_code=metadata.project_code,
            study_title=metadata.study_title,
            local_sample_alias=sample.local_sample_alias,
            specimen_type=sample.specimen_type,
            geolocation=sample.collection_site,
            sampling_date=sample.sampled_at,
        )
