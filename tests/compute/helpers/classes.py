"""Provide reusable compute test helper classes."""

from typing import Callable, Generic, ParamSpec, TypeAlias, TypeVar

from typing_extensions import NamedTuple

from omnipy import DagFlow, FuncFlow, LinearFlow
from omnipy.compute._job import JobTemplateMixin
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.shared.protocols.compute.job import (IsDagFlowTemplate,
                                                 IsFuncFlowTemplate,
                                                 IsLinearFlowTemplate,
                                                 IsTaskTemplate)

CallP = ParamSpec('CallP')
RetT = TypeVar('RetT')

SingleChildJobLinearFlowTemplateCallable: TypeAlias = Callable[[IsTaskTemplate],
                                                               Callable[[Callable[CallP, RetT]],
                                                                        IsLinearFlowTemplate[CallP,
                                                                                             RetT]]]
SingleChildJobDagFlowTemplateCallable: TypeAlias = Callable[[IsTaskTemplate],
                                                            Callable[[Callable[CallP, RetT]],
                                                                     IsDagFlowTemplate[CallP,
                                                                                       RetT]]]
FuncFlowTemplateCallable: TypeAlias = Callable[[],
                                               Callable[[Callable[CallP, RetT]],
                                                        IsFuncFlowTemplate[CallP, RetT]]]

#
# class FlowClsTuple(NamedTuple):
#     flow_cls: type[LinearFlow] | type[DagFlow] | type[FuncFlow]
#     flow_tmpl_cls: (
#         SingleChildJobLinearFlowTemplateCallable | SingleChildJobDagFlowTemplateCallable
#         | FuncFlowTemplateCallable)
#     assert_flow_tmpl_cls: type[JobTemplateMixin]

FlowClsT = TypeVar('FlowClsT', bound=type[LinearFlow] | type[DagFlow] | type[FuncFlow])
FlowTmplClsT = TypeVar(
    'FlowTmplClsT',
    bound=SingleChildJobLinearFlowTemplateCallable | SingleChildJobDagFlowTemplateCallable
    | FuncFlowTemplateCallable)


class FlowClsTuple(NamedTuple, Generic[FlowClsT, FlowTmplClsT]):
    """Bundle flow classes with their template helpers."""
    flow_cls: FlowClsT
    flow_tmpl_cls: FlowTmplClsT
    assert_flow_tmpl_cls: type[JobTemplateMixin]


FuncArgFlowClsTuple: TypeAlias = FlowClsTuple[type[FuncFlow], FuncFlowTemplateCallable]
ChildJobListArgFlowClsTuple: TypeAlias = FlowClsTuple[type[LinearFlow] | type[DagFlow],
                                                      SingleChildJobLinearFlowTemplateCallable
                                                      | SingleChildJobDagFlowTemplateCallable]
AnyFlowClsTuple: TypeAlias = FlowClsTuple[type[LinearFlow] | type[DagFlow] | type[FuncFlow],
                                          SingleChildJobLinearFlowTemplateCallable
                                          | SingleChildJobDagFlowTemplateCallable
                                          | FuncFlowTemplateCallable]


class CustomStrModel(Model[str]):
    """Provide a custom string model for tests."""
    ...


class CustomStrDataset(Dataset[CustomStrModel]):
    """Provide a custom string dataset for tests."""
    ...
