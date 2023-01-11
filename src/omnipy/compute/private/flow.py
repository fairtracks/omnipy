from abc import ABC
from typing import Any, Callable, Generic, Mapping, Optional, Tuple, Union

from omnipy.compute.job import JobTemplate
from omnipy.compute.job_types import FlowBaseT, FlowT, FlowTemplateT, TaskTemplatesFlowTemplateT
from omnipy.compute.mixins.serialize import PersistOutputsOptions, RestoreOutputsOptions
from omnipy.compute.private.job import FuncJob, FuncJobBase, FuncJobTemplate
from omnipy.compute.task import TaskTemplate
from omnipy.util.helpers import remove_none_vals


class FlowBase(FuncJobBase):
    ...


class FlowTemplate(FuncJobTemplate[FlowT], Generic[FlowT], ABC):
    ...


class Flow(FuncJob[FlowBaseT, FlowTemplateT], Generic[FlowBaseT, FlowTemplateT], ABC):
    ...


class TaskTemplatesFlowBase(FlowBase):
    def __init__(
        self,
        job_func: Callable,
        *task_templates: TaskTemplate,
        name: Optional[str] = None,
        fixed_params: Optional[Mapping[str, object]] = None,
        param_key_map: Optional[Mapping[str, str]] = None,
        result_key: Optional[str] = None,
        iterate_over_data_files: bool = False,
        persist_outputs: Optional[PersistOutputsOptions] = None,
        restore_outputs: Optional[RestoreOutputsOptions] = None,
        **kwargs: Any,
    ):
        super().__init__(
            job_func,
            **remove_none_vals(
                name=name,
                fixed_params=fixed_params,
                param_key_map=param_key_map,
                result_key=result_key,
                iterate_over_data_files=iterate_over_data_files,
                persist_outputs=persist_outputs,
                restore_outputs=restore_outputs,
                **kwargs,
            ))

        self._task_templates: Tuple[TaskTemplate, ...] = task_templates

    def _get_init_arg_values(self) -> Union[Tuple[()], Tuple[Any, ...]]:
        return self._job_func, *self._task_templates

    @property
    def task_templates(self) -> Tuple[TaskTemplate, ...]:
        return self._task_templates


class TaskTemplatesFlowTemplate(TaskTemplatesFlowBase, FlowTemplate[FlowT], Generic[FlowT], ABC):
    def refine(self: TaskTemplatesFlowTemplateT,
               *task_templates: TaskTemplate,
               update: bool = True,
               name: Optional[str] = None,
               fixed_params: Optional[Mapping[str, object]] = None,
               param_key_map: Optional[Mapping[str, str]] = None,
               result_key: Optional[str] = None,
               iterate_over_data_files: bool = False,
               persist_outputs: Optional[PersistOutputsOptions] = None,
               restore_outputs: Optional[RestoreOutputsOptions] = None,
               **kwargs: Any) -> TaskTemplatesFlowTemplateT:

        args = tuple([self._job_func] + list(*task_templates)) if task_templates else ()

        return JobTemplate.refine(
            self,
            *args,
            update=update,
            **remove_none_vals(
                name=name,
                fixed_params=fixed_params,
                param_key_map=param_key_map,
                result_key=result_key,
                iterate_over_data_files=iterate_over_data_files,
                persist_outputs=persist_outputs,
                restore_outputs=restore_outputs,
                **kwargs,
            ))


class TaskTemplatesFlow(TaskTemplatesFlowBase,
                        Flow[FlowBaseT, FlowTemplateT],
                        Generic[FlowBaseT, FlowTemplateT],
                        ABC):
    ...
