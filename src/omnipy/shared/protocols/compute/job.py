from datetime import datetime
from typing import ParamSpec, Protocol, TypeVar

from omnipy.shared.protocols.compute._job import (IsFuncArgJob,
                                                  IsFuncArgJobTemplate,
                                                  IsTaskTemplateArgsJob,
                                                  IsTaskTemplateArgsJobTemplate)
from omnipy.shared.protocols.compute.mixins import IsNestedContext

_CallP = ParamSpec('_CallP')
_RetT = TypeVar('_RetT')
_RetCovT = TypeVar('_RetCovT', covariant=True)


class IsTaskTemplate(IsFuncArgJobTemplate['IsTaskTemplate[_CallP, _RetT]',
                                          'IsTask[_CallP, _RetT]',
                                          _CallP,
                                          _RetT],
                     Protocol[_CallP, _RetT]):
    """
    Loosely coupled type replacement for the :py:class:`~omnipy.compute.task.TaskTemplate` class
    """
    ...


class IsTask(IsFuncArgJob['IsTaskTemplate[_CallP, _RetT]', 'IsTask[_CallP, _RetT]', _CallP, _RetT],
             Protocol[_CallP, _RetT]):
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
                                                         'IsLinearFlowTemplate[_CallP, _RetCovT]',
                                                         'IsLinearFlow[_CallP, _RetCovT]',
                                                         _CallP,
                                                         _RetCovT],
                           IsFlowTemplate,
                           Protocol[_CallP, _RetCovT]):
    """"""
    ...


class IsLinearFlow(IsTaskTemplateArgsJob[IsTaskTemplate,
                                         'IsLinearFlowTemplate[_CallP, _RetCovT]',
                                         'IsLinearFlow[_CallP, _RetCovT]',
                                         _CallP,
                                         _RetCovT],
                   IsFlow,
                   Protocol[_CallP, _RetCovT]):
    """"""
    ...


class IsDagFlowTemplate(IsTaskTemplateArgsJobTemplate[IsTaskTemplate,
                                                      'IsDagFlowTemplate[_CallP, _RetCovT]',
                                                      'IsDagFlow[_CallP, _RetCovT]',
                                                      _CallP,
                                                      _RetCovT],
                        IsFlowTemplate,
                        Protocol[_CallP, _RetCovT]):
    """"""
    ...


class IsDagFlow(IsTaskTemplateArgsJob[IsTaskTemplate,
                                      'IsDagFlowTemplate[_CallP, _RetCovT]',
                                      'IsDagFlow[_CallP, _RetCovT]',
                                      _CallP,
                                      _RetCovT],
                IsFlow,
                Protocol[_CallP, _RetCovT]):
    """"""
    ...


class IsFuncFlowTemplate(IsFuncArgJobTemplate['IsFuncFlowTemplate[_CallP, _RetCovT]',
                                              'IsFuncFlow[_CallP, _RetCovT]',
                                              _CallP,
                                              _RetCovT],
                         IsFlowTemplate,
                         Protocol[_CallP, _RetCovT]):
    """"""
    ...


class IsFuncFlow(IsFuncArgJob['IsFuncFlowTemplate[_CallP, _RetCovT]',
                              'IsFuncFlow[_CallP, _RetCovT]',
                              _CallP,
                              _RetCovT],
                 IsFlow,
                 Protocol[_CallP, _RetCovT]):
    """"""
    ...
