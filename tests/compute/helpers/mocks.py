from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType
from typing import (Any,
                    Callable,
                    cast,
                    Concatenate,
                    Generic,
                    Mapping,
                    ParamSpec,
                    Protocol,
                    runtime_checkable,
                    Type,
                    TypeAlias)

from typing_extensions import TypeVar

from omnipy.api.protocols.private.compute.job import (HasFuncArgJobTemplateInit,
                                                      IsFuncArgJob,
                                                      IsFuncArgJobTemplate,
                                                      IsJob,
                                                      IsJobTemplate)
from omnipy.api.protocols.private.engine import IsEngine
from omnipy.api.protocols.private.log import IsRunStateRegistry
from omnipy.api.protocols.public.compute import (IsDagFlow,
                                                 IsFlow,
                                                 IsFlowTemplate,
                                                 IsFuncFlow,
                                                 IsLinearFlow,
                                                 IsTask)
from omnipy.api.protocols.public.config import IsEngineConfig
from omnipy.api.protocols.public.engine import IsTaskRunnerEngine
from omnipy.compute.func_job import FuncArgJobBase
from omnipy.compute.job import JobBase, JobMixin, JobTemplateMixin
from omnipy.compute.mixins.flow_context import FlowContextJobMixin
from omnipy.engine.job_runner import DagFlowRunnerEngine, LinearFlowRunnerEngine
from omnipy.util.callable_decorator import callable_decorator_cls

JobTemplateT = TypeVar('JobTemplateT', covariant=True)
JobT = TypeVar('JobT', covariant=True)
InitP = ParamSpec('InitP')
CallP = ParamSpec('CallP')
CallP2 = ParamSpec('CallP2')
CallableT = TypeVar('CallableT')
RetT = TypeVar('RetT')
RetT2 = TypeVar('RetT2')
RetCovT = TypeVar('RetCovT', covariant=True)
RetContraT = TypeVar('RetContraT', contravariant=True)


@runtime_checkable
class IsMockJobTemplate(IsJobTemplate['IsMockJobTemplate[CallP, RetT]',
                                      'IsMockJob[CallP, RetT]',
                                      CallP,
                                      RetT],
                        Protocol[CallP, RetT]):
    """"""


@runtime_checkable
class IsMockJob(IsJob['IsMockJobTemplate[CallP, RetT]', 'IsMockJob[CallP, RetT]', CallP, RetT],
                Protocol[CallP, RetT]):
    """"""


class MockJobTemplateSubclass(JobTemplateMixin[IsMockJobTemplate[CallP, RetT],
                                               IsMockJob[CallP, RetT],
                                               CallP,
                                               RetT],
                              JobBase[IsMockJobTemplate[CallP, RetT],
                                      IsMockJob[CallP, RetT],
                                      CallP,
                                      RetT],
                              Generic[CallP, RetT]):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> type[IsMockJob[CallP, RetT]]:
        return cast(type[IsMockJob[CallP, RetT]], MockJobSubclass)


class MockJobSubclass(JobMixin[IsMockJobTemplate[CallP, RetT], IsMockJob[CallP, RetT], CallP, RetT],
                      JobBase,
                      Generic[CallP, RetT]):
    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> type[IsMockJobTemplate[CallP, RetT]]:
        return cast(type[IsMockJobTemplate[CallP, RetT]], MockJobTemplateSubclass)

    def _apply_engine_decorator(self, engine: IsEngine) -> None:
        ...

    def _call_job(self, *args: object, **kwargs: object) -> object:
        ...


class IsMockFlowTemplate(IsJobTemplate['IsMockFlowTemplate[CallP, RetT]',
                                       'IsMockFlow[CallP, RetT]',
                                       CallP,
                                       RetT],
                         IsFlowTemplate,
                         Protocol[CallP, RetT]):
    """"""


class IsMockFlow(IsJob['IsMockFlowTemplate[CallP, RetT]', 'IsMockFlow[CallP, RetT]', CallP, RetT],
                 IsFlow,
                 Protocol[CallP, RetT]):
    """"""


class MockFlowTemplateSubclass(JobTemplateMixin['IsMockFlowTemplate[CallP, RetT]',
                                                'IsMockFlow[CallP, RetT]',
                                                CallP,
                                                RetT],
                               JobBase[IsMockFlowTemplate[CallP, RetT],
                                       IsMockFlow[CallP, RetT],
                                       CallP,
                                       RetT],
                               Generic[CallP, RetT]):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> type[IsMockFlow[CallP, RetT]]:
        return cast(type[IsMockFlow[CallP, RetT]], MockFlowSubclass)


class MockFlowSubclass(JobMixin[IsMockFlowTemplate[CallP, RetT],
                                IsMockFlow[CallP, RetT],
                                CallP,
                                RetT],
                       JobBase[IsMockFlowTemplate[CallP, RetT],
                               IsMockFlow[CallP, RetT],
                               CallP,
                               RetT],
                       Generic[CallP, RetT]):
    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> type[IsMockFlowTemplate[CallP, RetT]]:
        return cast(type[IsMockFlowTemplate[CallP, RetT]], MockFlowTemplateSubclass)

    def _apply_engine_decorator(self, engine: IsEngine) -> None:
        ...


MockFlowSubclass.accept_mixin(FlowContextJobMixin)

ParamsType: TypeAlias = Mapping[str, int | str | bool] | list[tuple[str, str | int | bool]] | None


class CommandMockInit(JobBase, Generic[CallP, RetT]):
    def __init__(self,
                 cmd_func: Callable[CallP, RetT],
                 /,
                 command: str,
                 *,
                 name: str | None = None,
                 id: str = '',
                 uppercase: bool = False,
                 params: ParamsType = None,
                 **kwargs):

        super().__init__(name=name, **kwargs)
        self._cmd_func = cmd_func
        self._command = command
        self.engine_decorator_applied = False

    def _get_init_args(self) -> tuple[object, ...]:
        return self._cmd_func, self._command


class CommandMockParamMixin:
    def __init__(self, *, id: str = '', uppercase: bool = False, params: ParamsType = None):

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


class HasCommandMockJobTemplateInit(Generic[JobTemplateT, CallP, RetContraT]):
    def __call__(self,
                 cmd_func: Callable[CallP, RetContraT],
                 /,
                 command: str,
                 *,
                 name: str | None = None,
                 id: str = '',
                 uppercase: bool = False,
                 params: ParamsType = None,
                 **kwargs: object) -> JobTemplateT:
        ...


class IsCommandMockJobBase(Protocol):
    @property
    def id(self) -> str:
        ...

    @property
    def uppercase(self) -> bool:
        ...

    @property
    def params(self) -> MappingProxyType[str, Any]:
        ...

    @property
    def engine_decorator_applied(self) -> bool:
        ...


@runtime_checkable
class IsCommandMockJobTemplate(IsCommandMockJobBase,
                               IsJobTemplate['IsCommandMockJobTemplate[CallP, RetT]',
                                             'IsCommandMockJob[CallP, RetT]',
                                             CallP,
                                             RetT],
                               Protocol[CallP, RetT]):
    """"""
    def refine(self,
               update: bool = True,
               name: str | None = None,
               id: str = '',
               uppercase: bool = False,
               params: ParamsType = None,
               **kwargs: object) -> 'IsCommandMockJobTemplate[CallP, RetT]':
        ...

    def apply(self) -> 'IsCommandMockJob[CallP, RetT]':
        ...


class IsCommandMockJob(IsCommandMockJobBase,
                       IsJob['IsCommandMockJobTemplate[CallP, RetT]',
                             'IsCommandMockJob[CallP, RetT]',
                             CallP,
                             RetT],
                       Protocol[CallP, RetT]):
    """"""
    def revise(self) -> 'IsCommandMockJobTemplate[CallP, RetT]':
        ...


class CommandMockJobTemplateCore(CommandMockInit[CallP, RetT],
                                 JobTemplateMixin[IsCommandMockJobTemplate[CallP, RetT],
                                                  IsCommandMockJob[CallP, RetT],
                                                  CallP,
                                                  RetT],
                                 Generic[CallP, RetT]):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> type[IsCommandMockJob[CallP, RetT]]:
        return cast(type[IsCommandMockJob[CallP, RetT]], CommandMockJob[CallP, RetT])


# Needed for pyright and PyCharm
def command_mock_job_template_as_callable_decorator(
    decorated_cls: Callable[Concatenate[CallableT, InitP], IsCommandMockJobTemplate]) -> \
        Callable[InitP, Callable[[Callable[CallP, RetT]], IsCommandMockJobTemplate[CallP, RetT]]]:
    return callable_decorator_cls(
        cast(
            Callable[Concatenate[Callable[CallP, RetT], InitP],
                     IsCommandMockJobTemplate[CallP, RetT]],
            decorated_cls))


def to_command_mock_task_template_init_protocol(
    decorated_cls: Callable[Concatenate[Callable[CallP, RetT], InitP], CommandMockJobTemplateCore]
) -> HasCommandMockJobTemplateInit[IsCommandMockJobTemplate[CallP, RetT], CallP, RetT]:
    return cast(HasCommandMockJobTemplateInit[IsCommandMockJobTemplate[CallP, RetT], CallP, RetT],
                decorated_cls)


CommandMockJobTemplateCore.accept_mixin(CommandMockParamMixin)

CommandMockJobTemplate = command_mock_job_template_as_callable_decorator(
    to_command_mock_task_template_init_protocol(CommandMockJobTemplateCore))


class CommandMockJob(CommandMockInit[CallP, RetT],
                     JobMixin[IsCommandMockJobTemplate[CallP, RetT],
                              IsCommandMockJob[CallP, RetT],
                              CallP,
                              RetT],
                     Generic[CallP, RetT]):
    def _apply_engine_decorator(self, engine: IsEngine) -> None:
        self.engine_decorator_applied = True

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> type[IsCommandMockJobTemplate[CallP, RetT]]:
        return cast(type[IsCommandMockJobTemplate[CallP, RetT]], CommandMockJobTemplate)

    def _call_job(self, *args: object, **kwargs: object) -> object:
        param_self = cast(CommandMockParamMixin, self)
        if self._command in ['erase', 'restore']:
            if param_self._params and 'what' in param_self._params:
                log = f"{param_self._params['what']} has been {self._command}d" + (
                    f", {param_self._params['where']}" if 'where' in param_self._params else '')
            else:
                log = 'I know nothing'
            return log.upper() if param_self._uppercase else log


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
    def params(self) -> Mapping[str, Any]:
        return self._params


class PublicPropertyErrorsMockJobTemplate(JobBase[IsJobTemplate, IsJob, CallP, RetT],
                                          JobTemplateMixin[IsJobTemplate, IsJob, CallP, RetT]):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> type[IsJob]:
        return cast(type[IsJob], PublicPropertyErrorsMockJob)


class PublicPropertyErrorsMockJob(JobBase[IsJobTemplate, IsJob, CallP, RetT],
                                  JobMixin[IsJobTemplate, IsJob, CallP, RetT]):
    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[IsJobTemplate]:
        return cast(type[IsJobTemplate], PublicPropertyErrorsMockJobTemplate)

    def _apply_engine_decorator(self, engine: IsEngine) -> None:
        ...

    def _call_job(self, *args: CallP.args, **kwargs: CallP.kwargs) -> RetT:
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
    _persisted_time_of_cur_toplevel_flow_run: list[datetime] = []

    @property
    def persisted_time_of_cur_toplevel_flow_run(self) -> datetime | None:
        return self._persisted_time_of_cur_toplevel_flow_run[0] \
            if self._persisted_time_of_cur_toplevel_flow_run else None

    @classmethod
    def reset_persisted_time_of_cur_toplevel_flow_run(cls) -> None:
        cls._persisted_time_of_cur_toplevel_flow_run.clear()

    def _call_func(self, *args: object, **kwargs: object) -> object:
        self_as_job = cast(IsJob, self)
        if self.persisted_time_of_cur_toplevel_flow_run:
            assert self.persisted_time_of_cur_toplevel_flow_run == \
                   self_as_job.time_of_cur_toplevel_flow_run
        elif self_as_job.time_of_cur_toplevel_flow_run:
            self._persisted_time_of_cur_toplevel_flow_run.append(
                self_as_job.time_of_cur_toplevel_flow_run)

        super_as_func_arg_job = cast(FuncArgJobBase, super())
        return super_as_func_arg_job._call_func(*args, **kwargs)


class AssertsSameTimeOfCurFlowRun(Protocol):
    @property
    def persisted_time_of_cur_toplevel_flow_run(self) -> datetime | None:
        ...

    @classmethod
    def reset_persisted_time_of_cur_toplevel_flow_run(cls) -> None:
        ...


class IsMockTaskTemplateAssertSameTimeOfCurFlowRun(
        IsFuncArgJobTemplate['IsMockTaskTemplateAssertSameTimeOfCurFlowRun[CallP, RetT]',
                             'IsMockTaskAssertSameTimeOfCurFlowRun[CallP, RetT]',
                             CallP,
                             RetT],
        AssertsSameTimeOfCurFlowRun,
        Protocol[CallP, RetT]):
    """"""
    ...


class IsMockTaskAssertSameTimeOfCurFlowRun(
        IsFuncArgJob['IsMockTaskTemplateAssertSameTimeOfCurFlowRun[CallP, RetT]',
                     'IsMockTaskAssertSameTimeOfCurFlowRun[CallP, RetT]',
                     CallP,
                     RetT],
        AssertsSameTimeOfCurFlowRun,
        Protocol[CallP, RetT]):
    """"""


class MockTaskTemplateAssertSameTimeOfCurFlowRunCore(
        FuncArgJobBase[IsMockTaskTemplateAssertSameTimeOfCurFlowRun[CallP, RetT],
                       IsMockTaskAssertSameTimeOfCurFlowRun[CallP, RetT],
                       CallP,
                       RetT],
        JobTemplateMixin[IsMockTaskTemplateAssertSameTimeOfCurFlowRun[CallP, RetT],
                         IsMockTaskAssertSameTimeOfCurFlowRun[CallP, RetT],
                         CallP,
                         RetT],
        Generic[CallP, RetT]):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> type[IsMockTaskAssertSameTimeOfCurFlowRun[CallP, RetT]]:
        return cast(type[IsMockTaskAssertSameTimeOfCurFlowRun[CallP, RetT]],
                    MockTaskAssertSameTimeOfCurFlowRun[CallP, RetT])


# Needed for pyright and PyCharm
def mock_task_template_as_callable_decorator(
    decorated_cls: Callable[Concatenate[CallableT, InitP],
                            IsMockTaskTemplateAssertSameTimeOfCurFlowRun]
) -> Callable[InitP,
              Callable[[Callable[CallP, RetT]],
                       IsMockTaskTemplateAssertSameTimeOfCurFlowRun[CallP, RetT]]]:
    return callable_decorator_cls(
        cast(
            Callable[Concatenate[Callable[CallP, RetT], InitP],
                     IsMockTaskTemplateAssertSameTimeOfCurFlowRun[CallP, RetT]],
            decorated_cls))


def to_mock_task_template_init_protocol(
    decorated_cls: Callable[Concatenate[Callable[CallP, RetT], InitP],
                            MockTaskTemplateAssertSameTimeOfCurFlowRunCore[CallP, RetT]]
) -> HasFuncArgJobTemplateInit[
        IsMockTaskTemplateAssertSameTimeOfCurFlowRun[CallP, RetT], CallP, RetT]:
    return cast(
        HasFuncArgJobTemplateInit[
            IsMockTaskTemplateAssertSameTimeOfCurFlowRun[CallP, RetT],
            CallP,
            RetT,
        ],
        decorated_cls)


MockTaskTemplateAssertSameTimeOfCurFlowRunCore.accept_mixin(AssertSameTimeOfCurFlowRunJobBaseMixin)

MockTaskTemplateAssertSameTimeOfCurFlowRun = mock_task_template_as_callable_decorator(
    to_mock_task_template_init_protocol(MockTaskTemplateAssertSameTimeOfCurFlowRunCore))


class MockTaskAssertSameTimeOfCurFlowRun(
        JobMixin[IsMockTaskTemplateAssertSameTimeOfCurFlowRun[CallP, RetT],
                 IsMockTaskAssertSameTimeOfCurFlowRun[CallP, RetT],
                 CallP,
                 RetT],
        FuncArgJobBase[IsMockTaskTemplateAssertSameTimeOfCurFlowRun[CallP, RetT],
                       IsMockTaskAssertSameTimeOfCurFlowRun[CallP, RetT],
                       CallP,
                       RetT],
        Generic[CallP, RetT]):
    def _apply_engine_decorator(self, engine: IsEngine) -> None:
        if self.engine:
            engine = cast(IsTaskRunnerEngine, self.engine)
            self_with_mixins = cast(IsTask, self)
            engine.apply_task_decorator(self_with_mixins, self._accept_call_func_decorator)

    @classmethod
    def _get_job_template_subcls_for_revise(
            cls) -> type[IsMockTaskTemplateAssertSameTimeOfCurFlowRun[CallP, RetT]]:
        return cast(type[IsMockTaskTemplateAssertSameTimeOfCurFlowRun[CallP, RetT]],
                    MockTaskTemplateAssertSameTimeOfCurFlowRun)


MockTaskAssertSameTimeOfCurFlowRun.accept_mixin(AssertSameTimeOfCurFlowRunJobBaseMixin)
