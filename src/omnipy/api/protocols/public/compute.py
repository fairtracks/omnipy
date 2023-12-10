from datetime import datetime
from typing import Protocol

from omnipy.api.protocols.private.compute.job import (IsFuncArgJob,
                                                      IsFuncArgJobTemplate,
                                                      IsTaskTemplateArgsJob,
                                                      IsTaskTemplateArgsJobTemplate)
from omnipy.api.protocols.private.compute.mixins import IsNestedContext


class IsTaskTemplate(IsFuncArgJobTemplate['IsTaskTemplate', 'IsTask'], Protocol):
    """
    Loosely coupled type replacement for the :py:class:`~omnipy.compute.task.TaskTemplate` class
    """
    ...


class IsTask(IsFuncArgJob[IsTaskTemplate], Protocol):
    """"""
    ...


class IsFlowTemplate(Protocol):
    """"""
    ...


class IsFlow(Protocol):
    """"""
    @property
    def flow_context(self) -> IsNestedContext:
        ...

    @property
    def time_of_last_run(self) -> datetime | None:
        ...


class IsLinearFlowTemplate(IsTaskTemplateArgsJobTemplate[IsTaskTemplate,
                                                         'IsLinearFlowTemplate',
                                                         'IsLinearFlow'],
                           IsFlowTemplate,
                           Protocol):
    """"""
    ...


class IsLinearFlow(IsTaskTemplateArgsJob[IsTaskTemplate, IsLinearFlowTemplate], IsFlow, Protocol):
    """"""
    ...


class IsDagFlowTemplate(IsTaskTemplateArgsJobTemplate[IsTaskTemplate,
                                                      'IsDagFlowTemplate',
                                                      'IsDagFlow'],
                        IsFlowTemplate,
                        Protocol):
    """"""
    ...


class IsDagFlow(IsTaskTemplateArgsJob[IsTaskTemplate, IsDagFlowTemplate], IsFlow, Protocol):
    """"""
    ...


class IsFuncFlowTemplate(IsFuncArgJobTemplate['IsFuncFlowTemplate', 'IsFuncFlow'],
                         IsFlowTemplate,
                         Protocol):
    """"""
    ...


class IsFuncFlow(IsFuncArgJob[IsFuncFlowTemplate], Protocol):
    """"""
    ...
