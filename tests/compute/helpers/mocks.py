from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType
from typing import Any, Callable, cast, Dict, List, Mapping, Optional, Tuple, Type, Union

from omnipy.compute.job import Job, JobBase, JobTemplate
from omnipy.compute.job_creator import JobBaseMeta
from omnipy.compute.job_types import IsFuncJobTemplateCallable
from omnipy.compute.private.flow import FlowContextJobMixin
from omnipy.compute.private.job import FuncArgJobBase
from omnipy.engine.job_runner import DagFlowRunnerEngine, LinearFlowRunnerEngine
from omnipy.engine.protocols import (IsDagFlow,
                                     IsEngineConfig,
                                     IsFuncFlow,
                                     IsJob,
                                     IsLinearFlow,
                                     IsRunStateRegistry,
                                     IsTask)
from omnipy.util.callable_decorator_cls import callable_decorator_cls
from omnipy.util.mixin import DynamicMixinAcceptor


class MockJobTemplateSubclass(JobTemplate, JobBase):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type['MockJobSubclass']:
        return MockJobSubclass

    @classmethod
    def _apply_engine_decorator(cls, job: IsJob) -> IsJob:
        return job


class MockJobSubclass(Job, JobBase):
    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[MockJobTemplateSubclass]:
        return MockJobTemplateSubclass

    def _call_job(self, *args: object, **kwargs: object) -> object:
        ...


#
# def mock_flow_template_callable_decorator_cls(
#         cls: Type['MockFlowTemplateSubclass']
# ) -> IsFuncJobTemplateCallable['MockFlowTemplateSubclass']:
#     return cast(IsFuncJobTemplateCallable['MockFlowTemplateSubclass'], callable_decorator_cls(cls))


# @callable_decorator_cls
class MockFlowTemplateSubclass(JobTemplate, JobBase):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type['MockFlowSubclass']:
        return MockFlowSubclass

    @classmethod
    def _apply_engine_decorator(cls, job: IsJob) -> IsJob:
        return job


class MockFlowSubclass(Job, JobBase):
    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[MockFlowTemplateSubclass]:
        return MockFlowTemplateSubclass


MockFlowSubclass.accept_mixin(FlowContextJobMixin)


class CommandMockInit:
    def __init__(self,
                 cmd_func: Callable,
                 command: str,
                 *,
                 name: Optional[str] = None,
                 id: str = '',
                 uppercase: bool = False,
                 params: Mapping[str, Union[int, str, bool]] = None,
                 **kwargs):

        super().__init__(name=name, **kwargs)
        self._cmd_func = cmd_func
        self._command = command
        self.engine_decorator_applied = False

    def _get_init_args(self) -> Tuple[object, ...]:
        return self._cmd_func, self._command


class CommandMockParamMixin:
    def __init__(self,
                 *,
                 id: str = '',
                 uppercase: bool = False,
                 params: Mapping[str, Union[int, str, bool]] = None):

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
class CommandMockJobTemplate(JobTemplate, CommandMockInit, JobBase):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type['CommandMockJob']:
        return CommandMockJob

    def _apply_engine_decorator(self, job: IsJob) -> IsJob:
        self.engine_decorator_applied = True
        return job


class CommandMockJob(Job, CommandMockInit, JobBase):
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
    def __init__(self, *, params: Optional[Mapping[str, Union[int, str, bool]]] = None):
        self._params = params if params is not None else {}

    @property
    def params(self) -> Dict[str, Any]:
        return self._params


class PublicPropertyErrorsMockJobTemplate(JobTemplate, JobBase):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type['PublicPropertyErrorsMockJob']:
        return PublicPropertyErrorsMockJob

    @classmethod
    def _apply_engine_decorator(cls, job: IsJob) -> IsJob:
        return job


class PublicPropertyErrorsMockJob(Job, JobBase):
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

    def set_registry(self, registry: Optional[IsRunStateRegistry]) -> None:
        ...

    def task_decorator(self, task: IsTask) -> IsTask:
        prev_call_func = task._call_func  # noqa

        def _call_func(*args: Any, **kwargs: Any) -> Any:
            result = prev_call_func(*args, **kwargs)
            self.finished = True
            return result

        setattr(task, '_call_func', _call_func)
        return task

    def linear_flow_decorator(self, flow: IsLinearFlow) -> IsLinearFlow:  # noqa
        setattr(flow, '_call_func', LinearFlowRunnerEngine.default_linear_flow_run_decorator(flow))
        return flow

    def dag_flow_decorator(self, flow: IsDagFlow) -> IsDagFlow:  # noqa
        setattr(flow, '_call_func', DagFlowRunnerEngine.default_dag_flow_run_decorator(flow))
        return flow

    def func_flow_decorator(self, flow: IsFuncFlow) -> IsFuncFlow:
        prev_call_func = flow._call_func  # noqa

        def _call_func(*args: Any, **kwargs: Any) -> Any:
            with flow.flow_context:
                result = prev_call_func(*args, **kwargs)

            self.finished = True
            return result

        setattr(flow, '_call_func', _call_func)
        return flow


@dataclass
class MockJobConfig:
    persist_outputs: bool = True
    restore_outputs: bool = False


class AssertSameTimeOfCurFlowRunJobBaseMixin:
    _persisted_time_of_cur_toplevel_flow_run: Optional[datetime] = []

    @property
    def persisted_time_of_cur_toplevel_flow_run(self) -> List[datetime]:
        return self._persisted_time_of_cur_toplevel_flow_run[0] \
            if self._persisted_time_of_cur_toplevel_flow_run else None

    @classmethod
    def reset_persisted_time_of_cur_toplevel_flow_run(cls) -> None:
        cls._persisted_time_of_cur_toplevel_flow_run.clear()

    def _call_func(self, *args: object, **kwargs: object) -> object:
        if self.persisted_time_of_cur_toplevel_flow_run:
            assert self.persisted_time_of_cur_toplevel_flow_run == self.time_of_cur_toplevel_flow_run
        else:
            self._persisted_time_of_cur_toplevel_flow_run.append(self.time_of_cur_toplevel_flow_run)

        return super()._call_func(*args, **kwargs)


# def mock_task_template_assert_same_time_of_cur_flow_run_callable_decorator_cls(
#     cls: Type['MockTaskTemplateAssertSameTimeOfCurFlowRun']
# ) -> IsFuncJobTemplateCallable['MockTaskTemplateAssertSameTimeOfCurFlowRun']:
#     return cast(IsFuncJobTemplateCallable['MockTaskTemplateAssertSameTimeOfCurFlowRun'],
#                 callable_decorator_cls(cls))


@callable_decorator_cls
class MockTaskTemplateAssertSameTimeOfCurFlowRun(JobTemplate, FuncArgJobBase):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type['MockTaskAssertSameTimeOfCurFlowRun']:
        return MockTaskAssertSameTimeOfCurFlowRun

    def _apply_engine_decorator(self, job: IsJob) -> IsJob:
        return job


class MockTaskAssertSameTimeOfCurFlowRun(Job, FuncArgJobBase):
    @classmethod
    def _get_job_template_subcls_for_revise(
            cls) -> Type['MockTaskTemplateAssertSameTimeOfCurFlowRun']:
        return MockTaskTemplateAssertSameTimeOfCurFlowRun


MockTaskTemplateAssertSameTimeOfCurFlowRun.accept_mixin(AssertSameTimeOfCurFlowRunJobBaseMixin)
MockTaskAssertSameTimeOfCurFlowRun.accept_mixin(AssertSameTimeOfCurFlowRunJobBaseMixin)
