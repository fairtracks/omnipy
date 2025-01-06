from typing import Callable, Generic, ParamSpec, TypeAlias, TypeVar

from typing_extensions import NamedTuple

from omnipy import DagFlow, FuncFlow, LinearFlow
from omnipy.compute.job import JobTemplateMixin
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.shared.protocols.public.compute import (IsDagFlowTemplate,
                                                    IsFuncFlowTemplate,
                                                    IsLinearFlowTemplate,
                                                    IsTaskTemplate)

CallP = ParamSpec('CallP')
RetT = TypeVar('RetT')

SingleTaskLinearFlowTemplateCallable: TypeAlias = Callable[[IsTaskTemplate],
                                                           Callable[[Callable[CallP, RetT]],
                                                                    IsLinearFlowTemplate[CallP,
                                                                                         RetT]]]
SingleTaskDagFlowTemplateCallable: TypeAlias = Callable[[IsTaskTemplate],
                                                        Callable[[Callable[CallP, RetT]],
                                                                 IsDagFlowTemplate[CallP, RetT]]]
FuncFlowTemplateCallable: TypeAlias = Callable[[],
                                               Callable[[Callable[CallP, RetT]],
                                                        IsFuncFlowTemplate[CallP, RetT]]]

#
# class FlowClsTuple(NamedTuple):
#     flow_cls: type[LinearFlow] | type[DagFlow] | type[FuncFlow]
#     flow_tmpl_cls: (
#         SingleTaskLinearFlowTemplateCallable | SingleTaskDagFlowTemplateCallable
#         | FuncFlowTemplateCallable)
#     assert_flow_tmpl_cls: type[JobTemplateMixin]

FlowClsT = TypeVar('FlowClsT', bound=type[LinearFlow] | type[DagFlow] | type[FuncFlow])
FlowTmplClsT = TypeVar(
    'FlowTmplClsT',
    bound=SingleTaskLinearFlowTemplateCallable | SingleTaskDagFlowTemplateCallable
    | FuncFlowTemplateCallable)


class FlowClsTuple(NamedTuple, Generic[FlowClsT, FlowTmplClsT]):
    flow_cls: FlowClsT
    flow_tmpl_cls: FlowTmplClsT
    assert_flow_tmpl_cls: type[JobTemplateMixin]


FuncArgFlowClsTuple: TypeAlias = FlowClsTuple[type[FuncFlow], FuncFlowTemplateCallable]
TaskTemplateArgFlowClsTuple: TypeAlias = FlowClsTuple[type[LinearFlow] | type[DagFlow],
                                                      SingleTaskLinearFlowTemplateCallable
                                                      | SingleTaskDagFlowTemplateCallable]
AnyFlowClsTuple: TypeAlias = FlowClsTuple[type[LinearFlow] | type[DagFlow] | type[FuncFlow],
                                          SingleTaskLinearFlowTemplateCallable
                                          | SingleTaskDagFlowTemplateCallable
                                          | FuncFlowTemplateCallable]


class CustomStrModel(Model[str]):
    ...


class CustomStrDataset(Dataset[CustomStrModel]):
    ...
