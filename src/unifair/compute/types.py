from typing import Callable, Mapping, Optional, Protocol, TypeVar

from unifair.engine.protocols import IsTaskTemplate

JobBaseT = TypeVar('JobBaseT', bound='JobBase', covariant=True)
JobT = TypeVar('JobT', bound='Job', covariant=True)
JobTemplateT = TypeVar('JobTemplateT', bound='JobTemplate', covariant=True)

FuncJobTemplateT = TypeVar('FuncJobTemplateT', bound='FuncJobTemplate', covariant=True)


class FuncJobTemplateCallable(Protocol[FuncJobTemplateT]):
    def __call__(
        self,
        name: Optional[str] = None,
        fixed_params: Optional[Mapping[str, object]] = None,
        param_key_map: Optional[Mapping[str, str]] = None,
        result_key: Optional[str] = None,
        iterate_over_data_files: bool = False,
        **kwargs: object,
    ) -> Callable[[Callable], FuncJobTemplateT]:
        ...


TaskTemplatesFlowTemplateT = TypeVar(
    'TaskTemplatesFlowTemplateT', bound='TaskTemplatesFlowTemplate', covariant=True)


class TaskTemplatesFlowTemplateCallable(Protocol[TaskTemplatesFlowTemplateT]):
    def __call__(
        self,
        *task_templates: IsTaskTemplate,
        name: Optional[str] = None,
        fixed_params: Optional[Mapping[str, object]] = None,
        param_key_map: Optional[Mapping[str, str]] = None,
        result_key: Optional[str] = None,
        iterate_over_data_files: bool = False,
        **kwargs: object,
    ) -> Callable[[Callable], TaskTemplatesFlowTemplateT]:
        ...


FlowT = TypeVar('FlowT', bound='Flow', covariant=True)
FlowBaseT = TypeVar('FlowBaseT', bound='FlowBase', covariant=True)
FlowTemplateT = TypeVar('FlowTemplateT', bound='FlowTemplate', covariant=True)
