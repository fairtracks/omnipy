from __future__ import annotations

from datetime import datetime
from typing import Callable, Optional, Protocol, TypeVar

from omnipy.api.protocols.private.compute.job import (IsFuncArgJob,
                                                      IsFuncArgJobTemplate,
                                                      IsTaskTemplateArgsJob,
                                                      IsTaskTemplateArgsJobTemplate)
from omnipy.api.protocols.private.compute.mixins import IsNestedContext

C = TypeVar('C', bound=Callable)


class IsTaskTemplate(IsFuncArgJobTemplate['IsTaskTemplate', 'IsTask', C], Protocol[C]):
    """"""
    ...


class IsTask(IsFuncArgJob[IsTaskTemplate, C], Protocol[C]):
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
    def time_of_last_run(self) -> Optional[datetime]:
        ...


class IsLinearFlowTemplate(IsTaskTemplateArgsJobTemplate[IsTaskTemplate,
                                                         'IsLinearFlowTemplate',
                                                         'IsLinearFlow',
                                                         C],
                           IsFlowTemplate,
                           Protocol[C]):
    """"""
    ...


class IsLinearFlow(IsTaskTemplateArgsJob[IsTaskTemplate, IsLinearFlowTemplate, C],
                   IsFlow,
                   Protocol[C]):
    """"""
    ...


class IsDagFlowTemplate(IsTaskTemplateArgsJobTemplate[IsTaskTemplate,
                                                      'IsDagFlowTemplate',
                                                      'IsDagFlow',
                                                      C],
                        IsFlowTemplate,
                        Protocol[C]):
    """"""
    ...


class IsDagFlow(IsTaskTemplateArgsJob[IsTaskTemplate, IsDagFlowTemplate, C], IsFlow, Protocol[C]):
    """"""
    ...


class IsFuncFlowTemplate(IsFuncArgJobTemplate['IsFuncFlowTemplate', 'IsFuncFlow', C],
                         IsFlowTemplate,
                         Protocol[C]):
    """"""
    ...


class IsFuncFlow(IsFuncArgJob[IsFuncFlowTemplate, C], Protocol[C]):
    """"""
    ...
