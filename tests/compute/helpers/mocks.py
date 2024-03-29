from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType
from typing import Any, Callable, cast, Mapping, Protocol, Type

from omnipy.api.protocols.private.compute.job import (IsFuncArgJob,
                                                      IsFuncArgJobTemplate,
                                                      IsJob,
                                                      IsJobTemplate)
from omnipy.api.protocols.private.engine import IsEngine
from omnipy.api.protocols.private.log import IsRunStateRegistry
from omnipy.api.protocols.public.compute import IsDagFlow, IsFuncFlow, IsLinearFlow, IsTask
from omnipy.api.protocols.public.config import IsEngineConfig
from omnipy.api.protocols.public.engine import IsTaskRunnerEngine
from omnipy.compute.func_job import FuncArgJobBase
from omnipy.compute.job import JobBase, JobMixin, JobTemplateMixin
from omnipy.compute.mixins.flow_context import FlowContextJobMixin
from omnipy.engine.job_runner import DagFlowRunnerEngine, LinearFlowRunnerEngine
from omnipy.util.callable_decorator import callable_decorator_cls


class MockJobTemplateSubclass(JobTemplateMixin, JobBase):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type['MockJobSubclass']:
        return MockJobSubclass

    @classmethod
    def _apply_engine_decorator(cls, engine: IsEngine) -> None:
        ...


class MockJobSubclass(JobMixin, JobBase):
    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[MockJobTemplateSubclass]:
        return MockJobTemplateSubclass

    def _call_job(self, *args: object, **kwargs: object) -> object:
        ...


# @callable_decorator_cls
class MockFlowTemplateSubclass(JobTemplateMixin, JobBase):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type['MockFlowSubclass']:
        return MockFlowSubclass

    @classmethod
    def _apply_engine_decorator(cls, engine: IsEngine) -> None:
        ...


class MockFlowSubclass(JobMixin, JobBase):
    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[MockFlowTemplateSubclass]:
        return MockFlowTemplateSubclass


MockFlowSubclass.accept_mixin(FlowContextJobMixin)


class CommandMockInit:
    def __init__(self,
                 cmd_func: Callable,
                 command: str,
                 *,
                 name: str | None = None,
                 id: str = '',
                 uppercase: bool = False,
                 params: Mapping[str, int | str | bool] = None,
                 **kwargs):

        super().__init__(name=name, **kwargs)
        self._cmd_func = cmd_func
        self._command = command
        self.engine_decorator_applied = False

    def _get_init_args(self) -> tuple[object, ...]:
        return self._cmd_func, self._command


class CommandMockParamMixin:
    def __init__(self,
                 *,
                 id: str = '',
                 uppercase: bool = False,
                 params: Mapping[str, int | str | bool] = None):

        self._id = id
        self._uppercase = uppercase
        self._params = dict(params) if params is not None else {}

    @property
    def id(self) -> str:
        return self._id

    @property
    def uppercase(self) -> bool:
        return self._uppercase

    @property
    def params(self) -> MappingProxyType[str, Any]:
        return MappingProxyType(self._params)


@callable_decorator_cls
class CommandMockJobTemplate(JobTemplateMixin, CommandMockInit, JobBase):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type['CommandMockJob']:
        return CommandMockJob


class CommandMockJob(JobMixin, CommandMockInit, JobBase):
    def _apply_engine_decorator(self, engine: IsEngine) -> None:
        self.engine_decorator_applied = True

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[CommandMockJobTemplate]:
        return CommandMockJobTemplate

    def _call_job(self, *args: object, **kwargs: object) -> object:
        if self._command in ['erase', 'restore']:
            if 'what' in self.params:
                log = f"{self.params['what']} has been {self._command}d" \
                      f"{', ' + self.params['where'] if 'where' in self.params else ''}"
            else:
                log = 'I know nothing'
            return log.upper() if self._uppercase else log


CommandMockJobTemplate.accept_mixin(CommandMockParamMixin)
CommandMockJob.accept_mixin(CommandMockParamMixin)


class PublicPropertyErrorsMockVerboseMixin:
    """  Error: no attribute 'verbose' """
    def __init__(self, *, verbose: bool = True):
        self._verbose = verbose


class PublicPropertyErrorsMockCostMixin:
    """  Error: 'cost' is object attribute """
    def __init__(self, *, cost: int = 1):
        self.cost = cost


class PublicPropertyErrorsMockStrengthMixin:
    """  Error: 'strength' is class attribute """
    strength = 1

    def __init__(self, *, strength: int = 1):
        self.strength = strength


class PublicPropertyErrorsMockPowerMixin:
    """  Error: 'power' is method """
    def __init__(self, *, power: int = 1):
        self._power = power

    def power(self) -> int:
        return self._power


class PublicPropertyErrorsMockSpeedMixin:
    """  Error: 'speed' property is writable """
    def __init__(self, *, speed: int = 1):
        self._speed = speed

    @property
    def speed(self) -> int:
        return self._speed

    @speed.setter
    def speed(self, speed: int):
        self._speed = speed


class PublicPropertyErrorsMockParamsMixin:
    """  Error: 'params' property value is mutable """
    def __init__(self, *, params: Mapping[str, int | str | bool] | None = None):
        self._params = params if params is not None else {}

    @property
    def params(self) -> dict[str, Any]:
        return self._params


class PublicPropertyErrorsMockJobTemplate(JobTemplateMixin, JobBase):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type['PublicPropertyErrorsMockJob']:
        return PublicPropertyErrorsMockJob

    @classmethod
    def _apply_engine_decorator(cls, engine: IsEngine) -> None:
        ...


class PublicPropertyErrorsMockJob(JobMixin, JobBase):
    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[PublicPropertyErrorsMockJobTemplate]:
        return PublicPropertyErrorsMockJobTemplate

    def _call_job(self, *args: object, **kwargs: object) -> object:
        ...


def mock_cmd_func(**params: bool) -> Any:  # noqa
    pass


class MockLocalRunner:
    def __init__(self) -> None:
        self.finished = False

    @classmethod
    def get_config_cls(cls) -> Type[IsEngineConfig]:
        ...

    def set_config(self, config: IsEngineConfig) -> None:
        ...

    def set_registry(self, registry: IsRunStateRegistry | None) -> None:
        ...

    def apply_task_decorator(self, task: IsTask, job_callback_accept_decorator: Callable) -> None:
        def _task_decorator(call_func: Callable) -> Callable:
            def _call_func(*args: object, **kwargs: object) -> Any:
                result = call_func(*args, **kwargs)
                self.finished = True
                return result

            return _call_func

        job_callback_accept_decorator(_task_decorator)

    def apply_linear_flow_decorator(self,
                                    linear_flow: IsLinearFlow,
                                    job_callback_accept_decorator: Callable) -> None:
        def _default_linear_flow_decorator(call_func: Callable) -> Callable:
            return LinearFlowRunnerEngine.default_linear_flow_run_decorator(linear_flow)

        job_callback_accept_decorator(_default_linear_flow_decorator)

    def apply_dag_flow_decorator(self, dag_flow: IsDagFlow,
                                 job_callback_accept_decorator: Callable) -> None:
        def _default_dag_flow_decorator(call_func: Callable) -> Callable:
            return DagFlowRunnerEngine.default_dag_flow_run_decorator(dag_flow)

        job_callback_accept_decorator(_default_dag_flow_decorator)

    def apply_func_flow_decorator(self,
                                  func_flow: IsFuncFlow,
                                  job_callback_accept_decorator: Callable) -> None:
        def _func_flow_decorator(call_func: Callable) -> Callable:
            def _call_func(*args: object, **kwargs: object) -> Any:
                with func_flow.flow_context:
                    result = call_func(*args, **kwargs)

                self.finished = True
                return result

            return _call_func

        job_callback_accept_decorator(_func_flow_decorator)


@dataclass
class MockJobConfig:
    persist_outputs: bool = True
    restore_outputs: bool = False


class AssertSameTimeOfCurFlowRunJobBaseMixin:
    _persisted_time_of_cur_toplevel_flow_run: datetime | None = []

    @property
    def persisted_time_of_cur_toplevel_flow_run(self) -> list[datetime]:
        return self._persisted_time_of_cur_toplevel_flow_run[0] \
            if self._persisted_time_of_cur_toplevel_flow_run else None

    @classmethod
    def reset_persisted_time_of_cur_toplevel_flow_run(cls) -> None:
        cls._persisted_time_of_cur_toplevel_flow_run.clear()

    def _call_func(self, *args: object, **kwargs: object) -> object:
        if self.persisted_time_of_cur_toplevel_flow_run:
            assert self.persisted_time_of_cur_toplevel_flow_run == \
                   self.time_of_cur_toplevel_flow_run
        else:
            self._persisted_time_of_cur_toplevel_flow_run.append(self.time_of_cur_toplevel_flow_run)

        return super()._call_func(*args, **kwargs)


class IsMockTaskTemplateAssertSameTimeOfCurFlowRun(
        IsFuncArgJobTemplate['IsMockTaskTemplateAssertSameTimeOfCurFlowRun',
                             'IsMockTaskAssertSameTimeOfCurFlowRun'],
        Protocol):
    """"""
    ...


class IsMockTaskAssertSameTimeOfCurFlowRun(
        IsFuncArgJob[IsMockTaskTemplateAssertSameTimeOfCurFlowRun], Protocol):
    """"""


@callable_decorator_cls
class MockTaskTemplateAssertSameTimeOfCurFlowRun(JobTemplateMixin, FuncArgJobBase):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type[IsJob]:
        return cast(Type[IsMockTaskAssertSameTimeOfCurFlowRun], MockTaskAssertSameTimeOfCurFlowRun)


class MockTaskAssertSameTimeOfCurFlowRun(JobMixin, FuncArgJobBase):
    def _apply_engine_decorator(self, engine: IsEngine) -> None:
        if self.engine:
            engine = cast(IsTaskRunnerEngine, self.engine)
            self_with_mixins = cast(IsTask, self)
            engine.apply_task_decorator(self_with_mixins, self._accept_call_func_decorator)

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[IsJobTemplate]:
        return cast(Type[IsMockTaskTemplateAssertSameTimeOfCurFlowRun],
                    MockTaskTemplateAssertSameTimeOfCurFlowRun)


MockTaskTemplateAssertSameTimeOfCurFlowRun.accept_mixin(AssertSameTimeOfCurFlowRunJobBaseMixin)
MockTaskAssertSameTimeOfCurFlowRun.accept_mixin(AssertSameTimeOfCurFlowRunJobBaseMixin)
