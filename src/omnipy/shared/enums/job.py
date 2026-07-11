"""Job-related literal enums for execution, persistence, and restoration settings."""

from typing import Literal

from omnipy.util.literal_enum import LiteralEnum


class PersistOutputsOptions(LiteralEnum[str]):
    """Per-run options for whether to persist outputs."""

    Literals = Literal['disabled', 'config', 'enabled']

    DISABLED: Literal['disabled'] = 'disabled'
    FOLLOW_CONFIG: Literal['config'] = 'config'
    ENABLED: Literal['enabled'] = 'enabled'


class RestoreOutputsOptions(LiteralEnum[str]):
    """Per-run options for whether to restore persisted outputs."""

    Literals = Literal['disabled', 'config', 'auto_ignore_params', 'force_ignore_params']

    DISABLED: Literal['disabled'] = 'disabled'
    FOLLOW_CONFIG: Literal['config'] = 'config'
    AUTO_ENABLE_IGNORE_PARAMS: Literal['auto_ignore_params'] = 'auto_ignore_params'
    FORCE_ENABLE_IGNORE_PARAMS: Literal['force_ignore_params'] = 'force_ignore_params'


class OutputStorageProtocolOptions(LiteralEnum[str]):
    """Per-run options for which output storage protocol to use."""

    Literals = Literal['local', 's3', 'config']

    LOCAL: Literal['local'] = 'local'
    S3: Literal['s3'] = 's3'
    FOLLOW_CONFIG: Literal['config'] = 'config'


class ConfigPersistOutputsOptions(LiteralEnum[str]):
    """Configuration defaults for persisting flow and task outputs."""

    Literals = Literal['disabled', 'flow', 'all']

    DISABLED: Literal['disabled'] = 'disabled'
    ENABLE_FLOW_OUTPUTS: Literal['flow'] = 'flow'
    ENABLE_FLOW_AND_TASK_OUTPUTS: Literal['all'] = 'all'


class ConfigRestoreOutputsOptions(LiteralEnum[str]):
    """Configuration defaults for restoring persisted outputs."""

    Literals = Literal['disabled', 'auto_ignore_params']

    DISABLED: Literal['disabled'] = 'disabled'
    AUTO_ENABLE_IGNORE_PARAMS: Literal['auto_ignore_params'] = 'auto_ignore_params'


class ConfigOutputStorageProtocolOptions(LiteralEnum[str]):
    """Configuration defaults for output storage protocols."""

    Literals = Literal['local', 's3']

    LOCAL: Literal['local'] = 'local'
    S3: Literal['s3'] = 's3'


class EngineChoice(LiteralEnum[str]):
    """Execution engine enum values for running jobs."""

    Literals = Literal['local', 'prefect']

    LOCAL: Literal['local'] = 'local'
    PREFECT: Literal['prefect'] = 'prefect'


class TaskJobType(LiteralEnum[str]):
    """Literal enum values for task job categories."""

    Literals = Literal['task']

    TASK: Literal['task'] = 'task'


class FlowJobType(LiteralEnum[str]):
    """Literal enum values for supported flow job categories."""

    Literals = Literal['linear_flow', 'dag_flow', 'func_flow']

    LINEAR_FLOW: Literal['linear_flow'] = 'linear_flow'
    DAG_FLOW: Literal['dag_flow'] = 'dag_flow'
    FUNC_FLOW: Literal['func_flow'] = 'func_flow'


class JobType(TaskJobType, FlowJobType):
    """Combined literal enum values for all supported Omnipy job categories."""

    Literals = Literal[TaskJobType.Literals, FlowJobType.Literals]


class RunState(LiteralEnum[int]):
    """Lifecycle state enum values for a running job."""

    Literals = Literal[1, 2, 3]

    INITIALIZED: Literal[1] = 1
    RUNNING: Literal[2] = 2
    FINISHED: Literal[3] = 3


class RunStateLogMessages(LiteralEnum[str]):
    """Default log message templates associated with each run state."""

    Literals = Literal['Initialized "{}"', 'Started running "{}"...', 'Finished running "{}"!']

    INITIALIZED: Literal['Initialized "{}"'] = 'Initialized "{}"'
    RUNNING: Literal['Started running "{}"...'] = 'Started running "{}"...'
    FINISHED: Literal['Finished running "{}"!'] = 'Finished running "{}"!'


# TODO: Add 'apply' state
# TODO: Add 'failed' state and error management
# TODO: Consider the need for a 'waiting' state
