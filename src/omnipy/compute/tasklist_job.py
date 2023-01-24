from typing import Callable, Tuple

from omnipy.compute.func_job import FuncArgJobBase
from omnipy.compute.task import TaskTemplate

# class FlowInit(FuncArgJobBase):
#     def __init__(
#         self,
#         job_func: Callable,
#         *args: object,
#         name: Optional[str] = None,
#         iterate_over_data_files: bool = False,
#         fixed_params: Optional[Mapping[str, object]] = None,
#         param_key_map: Optional[Mapping[str, str]] = None,
#         result_key: Optional[str] = None,
#         persist_outputs: Optional[PersistOutputsOptions] = None,
#         restore_outputs: Optional[RestoreOutputsOptions] = None,
#         **kwargs: object,
#     ):
#         # super().__init__(
#         #     job_func,
#         #     **remove_none_vals(
#         #         name=name,
#         #         iterate_over_data_files=iterate_over_data_files,
#         #         fixed_params=fixed_params,
#         #         param_key_map=param_key_map,
#         #         result_key=result_key,
#         #         persist_outputs=persist_outputs,
#         #         restore_outputs=restore_outputs,
#         #         **kwargs,
#         #     ))
#
#         self._time_of_last_run = None

# class FlowTemplate(FuncJobTemplate, ABC):
#     ...

# class TaskTemplatesFlowBase(FlowInit):
#     def __init__(
#         self,
#         job_func: Callable,
#         *task_templates: TaskTemplate,
#         name: Optional[str] = None,
#         iterate_over_data_files: bool = False,
#         fixed_params: Optional[Mapping[str, object]] = None,
#         param_key_map: Optional[Mapping[str, str]] = None,
#         result_key: Optional[str] = None,
#         persist_outputs: Optional[PersistOutputsOptions] = None,
#         restore_outputs: Optional[RestoreOutputsOptions] = None,
#         **kwargs: object,
#     ):
#         # super().__init__(
#         #     job_func,
#         #     **remove_none_vals(
#         #         name=name,
#         #         iterate_over_data_files=iterate_over_data_files,
#         #         fixed_params=fixed_params,
#         #         param_key_map=param_key_map,
#         #         result_key=result_key,
#         #         persist_outputs=persist_outputs,
#         #         restore_outputs=restore_outputs,
#         #         **kwargs,
#         #     ))


class TaskTemplateArgsJobBase(FuncArgJobBase):
    def __init__(self, job_func: Callable, *task_templates: TaskTemplate, **kwargs: object) -> None:
        # FuncArgJobBase.__init__(self, job_func, *task_templates, **kwargs)

        self._task_templates: Tuple[TaskTemplate, ...] = task_templates

    def _get_init_args(self) -> Tuple[object, ...]:
        return self._job_func, *self._task_templates

    @property
    def task_templates(self) -> Tuple[TaskTemplate, ...]:
        return self._task_templates

    def _refine(self,
                *task_templates: TaskTemplate,
                update: bool = True,
                **kwargs: object):  # -> TaskTemplatesFlowTemplateT:

        return super()._refine(
            *task_templates,
            update=update,
            **kwargs,
        )


#
# class TaskTemplatesFlowTemplate(TaskTemplatesFlowBase, ABC):
#     def refine(self,
#                *task_templates: TaskTemplate,
#                update: bool = True,
#                name: Optional[str] = None,
#                iterate_over_data_files: bool = False,
#                fixed_params: Optional[Mapping[str, object]] = None,
#                param_key_map: Optional[Mapping[str, str]] = None,
#                result_key: Optional[str] = None,
#                persist_outputs: Optional[PersistOutputsOptions] = None,
#                restore_outputs: Optional[RestoreOutputsOptions] = None,
#                **kwargs: object):  # -> TaskTemplatesFlowTemplateT:
#
#         return self._refine(
#             self,
#             *task_templates,
#             update=update,
#             **remove_none_vals(
#                 name=name,
#                 iterate_over_data_files=iterate_over_data_files,
#                 fixed_params=fixed_params,
#                 param_key_map=param_key_map,
#                 result_key=result_key,
#                 persist_outputs=persist_outputs,
#                 restore_outputs=restore_outputs,
#                 **kwargs,
#             ))
#
#
# class TaskTemplatesFlow(TaskTemplatesFlowBase, Flow, ABC):
#     ...
