from __future__ import annotations

from typing import cast, Type

from omnipy.api.protocols import IsEngine, IsFuncJobTemplateCallable, IsTaskRunnerEngine
from omnipy.compute.func_job import FuncArgJobBase
from omnipy.compute.job import Job, JobTemplate
from omnipy.util.callable_decorator_cls import callable_decorator_cls

# class TaskInit(FuncArgJobBase):
#     def __init__(
#         self,
#         job_func: Callable,
#         name: Optional[str] = None,
#         iterate_over_data_files: bool = False,
#         fixed_params: Optional[Mapping[str, object]] = None,
#         param_key_map: Optional[Mapping[str, str]] = None,
#         result_key: Optional[str] = None,
#         persist_outputs: Optional[PersistOutputsOptions] = None,
#         restore_outputs: Optional[RestoreOutputsOptions] = None,
#         **kwargs: object,
#     ):
#         ...
#
#     #     super().__init__(
#     #         job_func,
#     #         **remove_none_vals(
#     #             name=name,
#     #             iterate_over_data_files=iterate_over_data_files,
#     #             fixed_params=fixed_params,
#     #             param_key_map=param_key_map,
#     #             result_key=result_key,
#     #             persist_outputs=persist_outputs,
#     #             restore_outputs=restore_outputs,
#     #             **kwargs,
#     #         ))


def task_template_callable_decorator_cls(
        cls: Type['TaskTemplate']) -> IsFuncJobTemplateCallable['TaskTemplate']:
    return cast(IsFuncJobTemplateCallable['TaskTemplate'], callable_decorator_cls(cls))


class TaskBase:
    ...


@task_template_callable_decorator_cls
class TaskTemplate(JobTemplate, TaskBase, FuncArgJobBase):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type[Task]:
        return Task


class Task(Job, TaskBase, FuncArgJobBase):
    def _apply_engine_decorator(self, engine: IsEngine) -> None:
        # self._check_engine(IsTaskRunnerEngine)
        if self.engine:
            engine = cast(IsTaskRunnerEngine, self.engine)
            engine.apply_task_decorator(self, self._accept_call_func_decorator)

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[TaskTemplate]:
        return TaskTemplate


# TODO: Would we need the possibility to refine task templates by adding new task parameters?
