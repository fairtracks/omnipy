from dataclasses import dataclass
from enum import Enum


class GlobalSerializeOutputsOptions(Enum):
    OFF = 0
    WRITE_FLOW_OUTPUTS = 1
    WRITE_FLOW_AND_TASK_OUTPUTS = 2


class GlobalResumePreviousRunsOptions(Enum):
    OFF = 0
    AUTO_READ_IGNORE_PARAMS = 1


@dataclass
class JobConfig:
    serialize_outputs: GlobalSerializeOutputsOptions = \
        GlobalSerializeOutputsOptions.WRITE_FLOW_AND_TASK_OUTPUTS
    resume_previous_runs: GlobalResumePreviousRunsOptions = \
        GlobalResumePreviousRunsOptions.OFF
