from datetime import datetime
from typing import ParamSpec, Protocol, TypeVar

from omnipy.api.protocols.private.compute.job import (IsFuncArgJob,
                                                      IsFuncArgJobTemplate,
                                                      IsTaskTemplateArgsJob,
                                                      IsTaskTemplateArgsJobTemplate)
from omnipy.api.protocols.private.compute.mixins import IsNestedContext

CallP = ParamSpec('CallP')
RetT = TypeVar('RetT')
RetCovT = TypeVar('RetCovT', covariant=True)


class IsTaskTemplate(IsFuncArgJobTemplate['IsTaskTemplate[CallP, RetT]',
                                          'IsTask[CallP, RetT]',
                                          CallP,
                                          RetT],
                     Protocol[CallP, RetT]):
    """
    Loosely coupled type replacement for the :py:class:`~omnipy.compute.task.TaskTemplate` class
    """
    ...


class IsTask(IsFuncArgJob['IsTaskTemplate[CallP, RetT]', 'IsTask[CallP, RetT]', CallP, RetT],
             Protocol[CallP, RetT]):
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
                                                         'IsLinearFlowTemplate[CallP, RetCovT]',
                                                         'IsLinearFlow[CallP, RetCovT]',
                                                         CallP,
                                                         RetCovT],
                           IsFlowTemplate,
                           Protocol[CallP, RetCovT]):
    """"""
    ...


class IsLinearFlow(IsTaskTemplateArgsJob[IsTaskTemplate,
                                         'IsLinearFlowTemplate[CallP, RetCovT]',
                                         'IsLinearFlow[CallP, RetCovT]',
                                         CallP,
                                         RetCovT],
                   IsFlow,
                   Protocol[CallP, RetCovT]):
    """"""
    ...


class IsDagFlowTemplate(IsTaskTemplateArgsJobTemplate[IsTaskTemplate,
                                                      'IsDagFlowTemplate[CallP, RetCovT]',
                                                      'IsDagFlow[CallP, RetCovT]',
                                                      CallP,
                                                      RetCovT],
                        IsFlowTemplate,
                        Protocol[CallP, RetCovT]):
    """"""
    ...


class IsDagFlow(IsTaskTemplateArgsJob[IsTaskTemplate,
                                      'IsDagFlowTemplate[CallP, RetCovT]',
                                      'IsDagFlow[CallP, RetCovT]',
                                      CallP,
                                      RetCovT],
                IsFlow,
                Protocol[CallP, RetCovT]):
    """"""
    ...


class IsFuncFlowTemplate(IsFuncArgJobTemplate['IsFuncFlowTemplate[CallP, RetCovT]',
                                              'IsFuncFlow[CallP, RetCovT]',
                                              CallP,
                                              RetCovT],
                         IsFlowTemplate,
                         Protocol[CallP, RetCovT]):
    """"""
    ...


class IsFuncFlow(IsFuncArgJob['IsFuncFlowTemplate[CallP, RetCovT]',
                              'IsFuncFlow[CallP, RetCovT]',
                              CallP,
                              RetCovT],
                 IsFlow,
                 Protocol[CallP, RetCovT]):
    """"""
    ...
