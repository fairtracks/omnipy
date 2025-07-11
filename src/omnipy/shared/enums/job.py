from typing import Literal

from omnipy.util.literal_enum import LiteralEnum


class PersistOutputsOptions(LiteralEnum[str]):
    Literals = Literal['disabled', 'config', 'enabled']

    DISABLED: Literal['disabled'] = 'disabled'
    FOLLOW_CONFIG: Literal['config'] = 'config'
    ENABLED: Literal['enabled'] = 'enabled'


class RestoreOutputsOptions(LiteralEnum[str]):
    Literals = Literal['disabled', 'config', 'auto_ignore_params', 'force_ignore_params']

    DISABLED: Literal['disabled'] = 'disabled'
    FOLLOW_CONFIG: Literal['config'] = 'config'
    AUTO_ENABLE_IGNORE_PARAMS: Literal['auto_ignore_params'] = 'auto_ignore_params'
    FORCE_ENABLE_IGNORE_PARAMS: Literal['force_ignore_params'] = 'force_ignore_params'


class OutputStorageProtocolOptions(LiteralEnum[str]):
    Literals = Literal['local', 's3', 'config']

    LOCAL: Literal['local'] = 'local'
    S3: Literal['s3'] = 's3'
    FOLLOW_CONFIG: Literal['config'] = 'config'


class ConfigPersistOutputsOptions(LiteralEnum[str]):
    Literals = Literal['disabled', 'flow', 'all']

    DISABLED: Literal['disabled'] = 'disabled'
    ENABLE_FLOW_OUTPUTS: Literal['flow'] = 'flow'
    ENABLE_FLOW_AND_TASK_OUTPUTS: Literal['all'] = 'all'


class ConfigRestoreOutputsOptions(LiteralEnum[str]):
    Literals = Literal['disabled', 'auto_ignore_params']

    DISABLED: Literal['disabled'] = 'disabled'
    AUTO_ENABLE_IGNORE_PARAMS: Literal['auto_ignore_params'] = 'auto_ignore_params'


class ConfigOutputStorageProtocolOptions(LiteralEnum[str]):
    Literals = Literal['local', 's3']

    LOCAL: Literal['local'] = 'local'
    S3: Literal['s3'] = 's3'


class EngineChoice(LiteralEnum[str]):
    Literals = Literal['local', 'prefect']

    LOCAL: Literal['local'] = 'local'
    PREFECT: Literal['prefect'] = 'prefect'


class RunState(LiteralEnum[int]):
    Literals = Literal[1, 2, 3]

    INITIALIZED: Literal[1] = 1
    RUNNING: Literal[2] = 2
    FINISHED: Literal[3] = 3


class RunStateLogMessages(LiteralEnum[str]):
    Literals = Literal['Initialized "{}"', 'Started running "{}"...', 'Finished running "{}"!']

    INITIALIZED: Literal['Initialized "{}"'] = 'Initialized "{}"'
    RUNNING: Literal['Started running "{}"...'] = 'Started running "{}"...'
    FINISHED: Literal['Finished running "{}"!'] = 'Finished running "{}"!'


# TODO: Add 'apply' state
# TODO: Add 'failed' state and error management
# TODO: Consider the need for a 'waiting' state
