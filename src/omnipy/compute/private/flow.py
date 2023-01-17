from abc import ABC
from datetime import datetime
from typing import Any, Callable, Generic, Mapping, Optional, Tuple, Union

from omnipy.compute.job import JobTemplate
from omnipy.compute.job_types import FlowBaseT, FlowT, FlowTemplateT, TaskTemplatesFlowTemplateT
from omnipy.compute.mixins.serialize import PersistOutputsOptions, RestoreOutputsOptions
from omnipy.compute.private.job import FuncJob, FuncJobBase, FuncJobTemplate
from omnipy.compute.task import TaskTemplate
from omnipy.engine.protocols import IsNestedContext
from omnipy.util.helpers import remove_none_vals


class FlowBase(FuncJobBase):
    def __init__(
        self,
        job_func: Callable,
        name: Optional[str] = None,
        iterate_over_data_files: bool = False,
        fixed_params: Optional[Mapping[str, object]] = None,
        param_key_map: Optional[Mapping[str, str]] = None,
        result_key: Optional[str] = None,
        persist_outputs: Optional[PersistOutputsOptions] = None,
        restore_outputs: Optional[RestoreOutputsOptions] = None,
        **kwargs: object,
    ):
        super().__init__(
            job_func,
            **remove_none_vals(
                name=name,
                iterate_over_data_files=iterate_over_data_files,
                fixed_params=fixed_params,
                param_key_map=param_key_map,
                result_key=result_key,
                persist_outputs=persist_outputs,
                restore_outputs=restore_outputs,
                **kwargs,
            ))

        self._time_of_last_run = None


class FlowTemplate(FuncJobTemplate[FlowT], Generic[FlowT], ABC):
    ...


class Flow(FuncJob[FlowBaseT, FlowTemplateT], Generic[FlowBaseT, FlowTemplateT], ABC):
    @property
    def flow_context(self) -> IsNestedContext:
        class FlowContext:
            @classmethod
            def __enter__(cls):
                self.__class__.job_creator.__enter__()
                self._time_of_last_run = self.time_of_cur_toplevel_flow_run

            @classmethod
            def __exit__(cls, exc_type, exc_val, exc_tb):
                self.__class__.job_creator.__exit__(exc_type, exc_val, exc_tb)

        return FlowContext()

    @property
    def time_of_last_run(self) -> datetime:
        return self._time_of_last_run


class TaskTemplatesFlowBase(FlowBase):
    def __init__(
        self,
        job_func: Callable,
        *task_templates: TaskTemplate,
        name: Optional[str] = None,
        iterate_over_data_files: bool = False,
        fixed_params: Optional[Mapping[str, object]] = None,
        param_key_map: Optional[Mapping[str, str]] = None,
        result_key: Optional[str] = None,
        persist_outputs: Optional[PersistOutputsOptions] = None,
        restore_outputs: Optional[RestoreOutputsOptions] = None,
        **kwargs: object,
    ):
        super().__init__(
            job_func,
            **remove_none_vals(
                name=name,
                iterate_over_data_files=iterate_over_data_files,
                fixed_params=fixed_params,
                param_key_map=param_key_map,
                result_key=result_key,
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
               iterate_over_data_files: bool = False,
               fixed_params: Optional[Mapping[str, object]] = None,
               param_key_map: Optional[Mapping[str, str]] = None,
               result_key: Optional[str] = None,
               persist_outputs: Optional[PersistOutputsOptions] = None,
               restore_outputs: Optional[RestoreOutputsOptions] = None,
               **kwargs: object) -> TaskTemplatesFlowTemplateT:

        args = tuple([self._job_func] + list(*task_templates)) if task_templates else ()

        return JobTemplate.refine(
            self,
            *args,
            update=update,
            **remove_none_vals(
                name=name,
                iterate_over_data_files=iterate_over_data_files,
                fixed_params=fixed_params,
                param_key_map=param_key_map,
                result_key=result_key,
                persist_outputs=persist_outputs,
                restore_outputs=restore_outputs,
                **kwargs,
            ))


class TaskTemplatesFlow(TaskTemplatesFlowBase,
                        Flow[FlowBaseT, FlowTemplateT],
                        Generic[FlowBaseT, FlowTemplateT],
                        ABC):
    ...
