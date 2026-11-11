from collections import defaultdict
from typing import Literal, TypeAlias, TypedDict

from omnipy.components.general.models import ConverterModel, PrimaryKeyDatasetModel
from omnipy.components.raw.models import DateModel
from omnipy.components.remote.models import HostUrlModel, HttpUrlModel
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.data.primary_key import PrimaryKey
from omnipy.data.typing.helpers import mimics
import omnipy.util.pydantic as pyd

StrippedUpperStr: TypeAlias = pyd.constr(  # type: ignore[valid-type]
    strip_whitespace=True, to_upper=True
)

StrippedLowerStr: TypeAlias = pyd.constr(  # type: ignore[valid-type]
    strip_whitespace=True, to_lower=True
)

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
    local_sample_id: StrippedLowerStr
    specimen_type: str
    collection_site: str
    sampled_at: DateModel
    biosample_vault_sample_id: StrippedUpperStr | None = None


@mimics(SubmissionSampleSchema)
class SubmissionSampleModel(Model[SubmissionSampleSchema]): ...


class SubmissionSamplesDataset(Dataset[SubmissionSampleModel]): ...


@mimics(SubmissionSamplesDataset)
class SubmissionSamplesByIdModel(
    PrimaryKeyDatasetModel[PrimaryKey[Literal['local_sample_id']], SubmissionSampleSchema]
):
    """Samples keyed by their local id, from a list of samples or a Dataset."""


class SubmissionFileSchema(pyd.BaseModel):
    local_file_id: StrippedLowerStr
    local_sample_id: StrippedLowerStr
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
class SubmissionFileSchemaModel(Model[SubmissionFileSchema]): ...


class SubmissionFilesDataset(Dataset[SubmissionFileSchemaModel]): ...


@mimics(SubmissionFilesDataset)
class SubmissionFilesByIdModel(
    PrimaryKeyDatasetModel[PrimaryKey[Literal['local_file_id']], SubmissionFileSchema]
):
    """Files keyed by their local id, from a list of files or a Dataset."""


class SubmissionMetadataSchema(pyd.BaseModel):
    broker_id: StrippedLowerStr
    local_submission_id: StrippedLowerStr
    project_code: StrippedLowerStr
    study_title: str
    release_date: DateModel
    submission_checklist_version: str
    sequence_depot_submission_id: str | None = None


@mimics(SubmissionMetadataSchema)
class SubmissionMetadataModel(Model[SubmissionMetadataSchema]): ...


class SubmissionStatusSchema(pyd.BaseModel):
    sequence_depot_submission_id_status: Status = 'pending'
    biosample_vault_status: Status = 'pending'
    transfer_status: Status = 'pending'
    sequence_depot_submission_status: Status = 'pending'


@mimics(SubmissionStatusSchema)
class SubmissionStatusModel(Model[SubmissionStatusSchema]): ...


class ServiceSchema(pyd.BaseModel):
    """Settings for using an external service."""

    url: HttpUrlModel

    # TODO: Add authentication with the service when Omnipy supports handling secrets. Secrets
    #       should then be referenced from here, not stored in the data.


class ServicesSchema(pyd.BaseModel):
    """The external services used by the broker, by default those in production."""

    sequence_depot: ServiceSchema = ServiceSchema(
        url=HttpUrlModel('https://api.sequence-depot.example/')
    )
    biosample_vault: ServiceSchema = ServiceSchema(
        url=HttpUrlModel('https://api.biosample-vault.example/')
    )
    file_transfer: ServiceSchema = ServiceSchema(
        url=HttpUrlModel('https://transfers.sequence-depot.example/')
    )


@mimics(ServicesSchema)
class ServicesModel(Model[ServicesSchema]): ...


class LogisticsSchema(pyd.BaseModel):
    """The broker's handling of a submission: the services to use and how far it has got.

    Logistics are not part of the submission sent to the Sequence Depot. Other broker-side
    settings for a submission belong here as well.
    """

    # Settings, provided as input and only read by the dataflow
    services: ServicesModel = pyd.Field(default_factory=ServicesModel)

    # State, derived from the submission content as the dataflow proceeds
    status: SubmissionStatusModel = pyd.Field(default_factory=SubmissionStatusModel)


@mimics(LogisticsSchema)
class LogisticsModel(Model[LogisticsSchema]): ...


class _SubmissionDict(TypedDict):
    samples: SubmissionSamplesByIdModel
    files: SubmissionFilesByIdModel
    metadata: SubmissionMetadataModel


class SubmissionSchema(pyd.BaseModel):
    """The content of a submission, as sent to the Sequence Depot."""

    samples: SubmissionSamplesByIdModel
    files: SubmissionFilesByIdModel
    metadata: SubmissionMetadataModel

    @pyd.validator('files')
    def _samples_have_one_read1_and_one_read2(
        cls,
        files: SubmissionFilesByIdModel,
        values: _SubmissionDict,
    ) -> SubmissionFilesByIdModel:
        file_roles_per_sample: defaultdict[str, set[FileRole]] = defaultdict(set)

        for file in files.values():
            file_roles = file_roles_per_sample[file.local_sample_id]
            if file.file_role in file_roles:
                raise ValueError(
                    f"Duplicate file role '{file.file_role}' for sample '{file.local_sample_id}'"
                )
            file_roles.add(file.file_role)

        # Missing if the samples failed validation, which is reported separately
        if 'samples' in values:
            for sample in values['samples'].values():
                file_roles = file_roles_per_sample[sample.local_sample_id]
                if file_roles != {'read1', 'read2'}:
                    raise ValueError(
                        f"Sample '{sample.local_sample_id}' must have exactly two files "
                        '(read1 and read2).'
                    )

        return files

    # TODO: Consider general support for remote key validation in Models of
    #       Pydantic models containing datasets.

    @pyd.validator('files')
    def _file_sample_ids_exist(
        cls,
        files: SubmissionFilesByIdModel,
        values: _SubmissionDict,
    ) -> SubmissionFilesByIdModel:
        # Missing if the samples failed validation, which is reported separately
        if 'samples' in values:
            sample_ids = {sample.local_sample_id for sample in values['samples'].values()}
            for file in files.values():
                if file.local_sample_id not in sample_ids:
                    raise ValueError(
                        f'File "{file.local_file_id}" has local_sample_id '
                        f'"{file.local_sample_id}" which does not match any '
                        f'sample in the submission.'
                    )
        return files


class SubmissionWithLogisticsSchema(SubmissionSchema):
    logistics: LogisticsModel = pyd.Field(default_factory=LogisticsModel)

    # TODO: Redesign _update_sequence_depot_submission_id_status,
    #       _update_transfer_status and _update_biosample_vault_status as
    #       @computed_fields in Pydantic v2
    @pyd.validator('logistics')
    def _update_sequence_depot_submission_id_status(
        cls,
        logistics: LogisticsModel,
        values: _SubmissionDict,
    ) -> LogisticsModel:
        # Missing if the metadata failed validation, which is reported separately
        if 'metadata' in values:
            status = logistics.status
            if values['metadata'].sequence_depot_submission_id is not None:
                status.sequence_depot_submission_id_status = 'completed'
            else:
                status.sequence_depot_submission_id_status = 'pending'

        return logistics

    @pyd.validator('logistics')
    def _update_transfer_status(
        cls,
        logistics: LogisticsModel,
        values: _SubmissionDict,
    ) -> LogisticsModel:
        # Missing if the files failed validation, which is reported separately
        if 'files' in values:
            status = logistics.status
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

        return logistics

    @pyd.validator('logistics')
    def _update_biosample_vault_status(
        cls,
        logistics: LogisticsModel,
        values: dict,
    ) -> LogisticsModel:
        status = logistics.status
        samples = values.get('samples', {})
        all_samples_biosample_vault_ids: set[StrippedUpperStr] = {
            sample.biosample_vault_sample_id
            for sample in samples.values()
            if sample.biosample_vault_sample_id is not None
        }
        if len(samples) == 0:
            status.biosample_vault_status = 'N/A'
        elif len(all_samples_biosample_vault_ids) == len(samples):
            status.biosample_vault_status = 'completed'
        else:
            status.biosample_vault_status = 'pending'

        return logistics


@mimics(SubmissionWithLogisticsSchema)
class SubmissionModel(Model[SubmissionWithLogisticsSchema]): ...


@mimics(SubmissionSchema)
class FinalSubmissionModel(Model[SubmissionSchema]): ...


class SequenceDepotSubmissionIdRequest(pyd.BaseModel):
    local_submission_id: str
    project_code: str
    sequence_depot_submission_id: str | None = None


class SequenceDepotSubmissionReceipt(pyd.BaseModel):
    accepted: bool


class FileTransferRequest(pyd.BaseModel):
    username: str
    source_uri: S3UrlModel
    target_uri: FtpUrlModel


class FileTransferResponse(pyd.BaseModel):
    status: Status
    error: str | None = None


@mimics(SequenceDepotSubmissionIdRequest)
class SubmissionToSequenceDepotRequestMapper(
    ConverterModel[
        SubmissionModel,
        SequenceDepotSubmissionIdRequest,
    ]
):
    @classmethod
    def _convert(cls, data: SubmissionModel) -> SequenceDepotSubmissionIdRequest:
        return SequenceDepotSubmissionIdRequest(
            local_submission_id=data.metadata.local_submission_id,
            project_code=data.metadata.project_code,
        )


class BioSampleVaultSampleSubmissionSchema(pyd.BaseModel):
    broker_id: StrippedLowerStr
    project_code: StrippedLowerStr
    study_title: str
    local_sample_id: StrippedLowerStr
    specimen_type: str
    geolocation: str
    sampling_date: DateModel
    biosample_vault_sample_id: StrippedUpperStr | None = None


@mimics(BioSampleVaultSampleSubmissionSchema)
class SampleAndMetadataToBioSampleVaultSubmissionMapper(
    ConverterModel[
        Model[tuple[SubmissionSampleModel, SubmissionMetadataModel]],
        BioSampleVaultSampleSubmissionSchema,
    ]
):
    @classmethod
    def _convert(
        cls, data: Model[tuple[SubmissionSampleModel, SubmissionMetadataModel]]
    ) -> BioSampleVaultSampleSubmissionSchema:
        sample, metadata = data
        return BioSampleVaultSampleSubmissionSchema(
            broker_id=metadata.broker_id,
            project_code=metadata.project_code,
            study_title=metadata.study_title,
            local_sample_id=sample.local_sample_id,
            specimen_type=sample.specimen_type,
            geolocation=sample.collection_site,
            sampling_date=sample.sampled_at,
        )
