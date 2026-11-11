"""Models of the sequence submission dataflow.

`SeqDepot` and `seq_depot` are short for the Sequence Depot, the repository receiving the
sequence submissions.
"""

from collections import defaultdict
from typing import Literal, TypeAlias, TypedDict

from omnipy.components.general.models import ConverterModel, PrimaryKeyDatasetModel
from omnipy.components.raw.models import DateModel
from omnipy.components.remote.datasets import HostUrlDataset
from omnipy.components.remote.models import HostUrlModel
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
    biosamplevault_sample_id: StrippedUpperStr | None = None


@mimics(SubmissionSampleSchema)
class SubmissionSampleModel(Model[SubmissionSampleSchema]): ...


@mimics(Dataset[SubmissionSampleModel])
class SubmissionSamplesDataset(
    PrimaryKeyDatasetModel[PrimaryKey[Literal['local_sample_id']], SubmissionSampleSchema]
):
    """Samples keyed by their local id, from a list of samples or a Dataset."""


class SeqDepotSubmissionFileSchema(pyd.BaseModel):
    local_file_id: StrippedLowerStr
    local_sample_id: StrippedLowerStr
    file_role: FileRole
    md5: Md5Str
    source_storage_uri: S3UrlModel
    staging_storage_uri: FtpUrlModel | None = None
    file_name: FileName = pyd.Field(default='')

    @pyd.validator('file_name')
    def _extract_file_name_from_source_storage_uri(cls, file_name: str, values: dict) -> str:
        if not file_name and 'source_storage_uri' in values:
            file_name = values['source_storage_uri'].path.name
        return file_name


@mimics(SeqDepotSubmissionFileSchema)
class SeqDepotSubmissionFileModel(Model[SeqDepotSubmissionFileSchema]): ...


@mimics(Dataset[SeqDepotSubmissionFileModel])
class SeqDepotSubmissionFilesDataset(
    PrimaryKeyDatasetModel[PrimaryKey[Literal['local_file_id']], SeqDepotSubmissionFileSchema]
):
    """Files keyed by their local id, from a list of files or a Dataset."""


class SubmissionFileSchema(SeqDepotSubmissionFileSchema):
    """A file of the submission, with the outcome of its transfer to the staging area."""

    transfer_status: Status = 'pending'
    error: str | None = None


@mimics(SubmissionFileSchema)
class SubmissionFileModel(Model[SubmissionFileSchema]): ...


@mimics(Dataset[SubmissionFileModel])
class SubmissionFilesDataset(
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
    seq_depot_submission_id: str | None = None


@mimics(SubmissionMetadataSchema)
class SubmissionMetadataModel(Model[SubmissionMetadataSchema]): ...


class BrokeringStatusSchema(pyd.BaseModel):
    seq_depot_submission_id_status: Status = 'pending'
    biosamplevault_status: Status = 'pending'
    file_transfer_status: Status = 'pending'
    seq_depot_submission_status: Status = 'pending'


@mimics(BrokeringStatusSchema)
class BrokeringStatusModel(Model[BrokeringStatusSchema]): ...


class ServiceSchema(pyd.BaseModel):
    """Settings for an external service, with the URLs of its endpoints and storage areas."""

    urls: HostUrlDataset

    # TODO: Add authentication with the service when Omnipy supports handling secrets. Secrets
    #       should then be referenced from here, not stored in the data.


class ServicesSchema(pyd.BaseModel):
    """The external services used by the broker, by default those in production."""

    seq_depot: ServiceSchema = ServiceSchema(
        urls=HostUrlDataset(
            {
                'presubmit': 'https://api.sequence-depot.example/presubmit',
                'submissions': 'https://api.sequence-depot.example/submissions',
                'staging': 'ftps://ftp.sequence-depot.example/staging',
            }
        )
    )
    biosamplevault: ServiceSchema = ServiceSchema(
        urls=HostUrlDataset({'samples': 'https://samples.biosamplevault.example/'})
    )
    file_transfer: ServiceSchema = ServiceSchema(
        urls=HostUrlDataset({'transfers': 'https://api.file-transfer.example/'})
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
    status: BrokeringStatusModel = pyd.Field(default_factory=BrokeringStatusModel)


@mimics(LogisticsSchema)
class LogisticsModel(Model[LogisticsSchema]): ...


class _SeqDepotSubmissionPayloadDict(TypedDict):
    samples: SubmissionSamplesDataset
    files: SeqDepotSubmissionFilesDataset
    metadata: SubmissionMetadataModel


class SeqDepotSubmissionPayloadSchema(pyd.BaseModel):
    """The content of a submission, as sent to the Sequence Depot."""

    samples: SubmissionSamplesDataset
    files: SeqDepotSubmissionFilesDataset
    metadata: SubmissionMetadataModel

    # TODO: Consider general support for checking if field values
    #       of Model-wrapped Pydantic records are unique.

    @pyd.validator('samples')
    def _biosamplevault_sample_ids_are_unique(
        cls,
        samples: SubmissionSamplesDataset,
    ) -> SubmissionSamplesDataset:
        # Samples are keyed by their local ids, so ids assigned by the BioSample Vault are
        # checked here
        local_sample_ids_per_vault_id: dict[str, str] = {}
        for sample in samples.values():
            vault_id = sample.biosamplevault_sample_id
            if vault_id is None:
                continue
            if vault_id in local_sample_ids_per_vault_id:
                raise ValueError(
                    f"BioSample Vault sample id '{vault_id}' is assigned to both sample "
                    f"'{local_sample_ids_per_vault_id[vault_id]}' and '{sample.local_sample_id}'"
                )
            local_sample_ids_per_vault_id[vault_id] = sample.local_sample_id
        return samples

    @pyd.validator('files')
    def _samples_have_one_read1_and_one_read2(
        cls,
        files: SeqDepotSubmissionFilesDataset,
        values: _SeqDepotSubmissionPayloadDict,
    ) -> SeqDepotSubmissionFilesDataset:
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
        files: SeqDepotSubmissionFilesDataset,
        values: _SeqDepotSubmissionPayloadDict,
    ) -> SeqDepotSubmissionFilesDataset:
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


class _SubmissionDict(TypedDict):
    samples: SubmissionSamplesDataset
    files: SubmissionFilesDataset
    metadata: SubmissionMetadataModel


class SubmissionSchema(SeqDepotSubmissionPayloadSchema):
    files: SubmissionFilesDataset
    logistics: LogisticsModel = pyd.Field(default_factory=LogisticsModel)

    # TODO: Redesign _update_seq_depot_submission_id_status,
    #       _update_file_transfer_status and _update_biosamplevault_status as
    #       @computed_fields in Pydantic v2
    @pyd.validator('logistics')
    def _update_seq_depot_submission_id_status(
        cls,
        logistics: LogisticsModel,
        values: _SubmissionDict,
    ) -> LogisticsModel:
        # Missing if the metadata failed validation, which is reported separately
        if 'metadata' in values:
            status = logistics.status
            if values['metadata'].seq_depot_submission_id is not None:
                status.seq_depot_submission_id_status = 'completed'
            else:
                status.seq_depot_submission_id_status = 'pending'

        return logistics

    @pyd.validator('logistics')
    def _update_file_transfer_status(
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
                status.file_transfer_status = 'N/A'
            elif 'failed' in all_files_transfer_status:
                status.file_transfer_status = 'failed'
            elif 'pending' in all_files_transfer_status:
                status.file_transfer_status = 'pending'
            else:
                status.file_transfer_status = 'completed'

        return logistics

    @pyd.validator('logistics')
    def _update_biosamplevault_status(
        cls,
        logistics: LogisticsModel,
        values: _SubmissionDict,
    ) -> LogisticsModel:
        # Missing if the samples failed validation, which is reported separately
        if 'samples' in values:
            status = logistics.status
            samples = values['samples'].values()
            if len(samples) == 0:
                status.biosamplevault_status = 'N/A'
            elif all(sample.biosamplevault_sample_id is not None for sample in samples):
                status.biosamplevault_status = 'completed'
            else:
                status.biosamplevault_status = 'pending'

        return logistics


@mimics(SubmissionSchema)
class SubmissionModel(Model[SubmissionSchema]): ...


@mimics(SeqDepotSubmissionPayloadSchema)
class SeqDepotSubmissionPayloadModel(Model[SeqDepotSubmissionPayloadSchema]): ...


class SeqDepotPresubmitSchema(pyd.BaseModel):
    local_submission_id: str
    project_code: str
    seq_depot_submission_id: str | None = None


class SeqDepotSubmissionReceiptSchema(pyd.BaseModel):
    accepted: bool


class FileTransferRequestSchema(pyd.BaseModel):
    username: str
    source_uri: S3UrlModel
    target_uri: FtpUrlModel


class FileTransferResponseSchema(pyd.BaseModel):
    status: Literal['completed', 'failed']
    target_uri: FtpUrlModel | None = None
    error: str | None = None


@mimics(SeqDepotPresubmitSchema)
class SubmissionToSeqDepotPresubmitMapper(
    ConverterModel[
        SubmissionModel,
        SeqDepotPresubmitSchema,
    ]
):
    @classmethod
    def _convert(cls, data: SubmissionModel) -> SeqDepotPresubmitSchema:
        return SeqDepotPresubmitSchema(
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
    biosamplevault_sample_id: StrippedUpperStr | None = None


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


@mimics(FileTransferRequestSchema)
class FileAndMetadataToFileTransferRequestMapper(
    ConverterModel[
        Model[tuple[SubmissionFileModel, SubmissionMetadataModel, HostUrlModel]],
        FileTransferRequestSchema,
    ]
):
    """Converts a file, the metadata and the staging URL into a file transfer request."""

    @classmethod
    def _convert(
        cls, data: Model[tuple[SubmissionFileModel, SubmissionMetadataModel, HostUrlModel]]
    ) -> FileTransferRequestSchema:
        file, metadata, staging_url = data
        target_uri = FtpUrlModel(staging_url)
        (
            target_uri.path
            // metadata.broker_id
            // metadata.local_submission_id
            // file.local_sample_id
            // file.file_name
        )
        return FileTransferRequestSchema(
            username=metadata.broker_id,
            source_uri=file.source_storage_uri,
            target_uri=target_uri,
        )
