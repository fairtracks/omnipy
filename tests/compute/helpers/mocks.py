from types import MappingProxyType
from typing import Any, Callable, Dict, Mapping, Optional, Tuple, Type, Union

from omnipy.compute.job import (CallableDecoratingJobTemplateMixin,
                                Job,
                                JobBase,
                                JobBaseAndMixinAcceptorMeta,
                                JobTemplate)
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


class MockJobBaseSubclass(
        JobBase,
        DynamicMixinAcceptor,
        metaclass=JobBaseAndMixinAcceptorMeta,
):
    def __init__(self, *args, **kwargs):
        super().__init__()

    def _get_init_arg_values(self) -> Union[Tuple[()], Tuple[Any, ...]]:
        return ()

    def _get_init_kwarg_public_property_keys(self) -> Tuple[str, ...]:
        return ()


class MockJobTemplateSubclass(MockJobBaseSubclass, JobTemplate['MockJobSubclass']):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type['MockJobSubclass']:
        return MockJobSubclass

    @classmethod
    def _apply_engine_decorator(cls, job: IsJob) -> IsJob:
        return job


class MockJobSubclass(MockJobBaseSubclass, Job[MockJobBaseSubclass, MockJobTemplateSubclass]):
    @classmethod
    def _get_job_base_subcls_for_init(cls) -> Type[MockJobBaseSubclass]:
        return MockJobBaseSubclass

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[MockJobTemplateSubclass]:
        return MockJobTemplateSubclass

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def _call_func(self, *args: Any, **kwargs: Any) -> Any:
        ...


class PublicPropertyErrorsMockJobBase(
        JobBase,
        DynamicMixinAcceptor,
        metaclass=JobBaseAndMixinAcceptorMeta,
):
    strength = 1

    def __init__(self,
                 *,
                 name: Optional[str] = None,
                 property_index: int = None,
                 verbose: bool = True,
                 cost: int = 1,
                 strength: int = 1,
                 power: int = 1,
                 speed: int = 1,
                 params: Mapping[str, Union[int, str, bool]] = None,
                 **kwargs):

        super().__init__()
        self._property_index = property_index
        self._verbose = verbose
        self.cost = cost
        self.strength = strength
        self._power = power
        self._speed = speed
        self._params = params if params is not None else {}

    def _get_init_arg_values(self) -> Union[Tuple[()], Tuple[Any, ...]]:
        return ()

    def _get_init_kwarg_public_property_keys(self) -> Tuple[str, ...]:
        if self._property_index is not None:
            index = self._property_index
            return ('verbose', 'cost', 'strength', 'power', 'speed', 'params')[index:index + 1]
        else:
            return ()

    def power(self) -> int:
        return self._power

    @property
    def speed(self) -> int:
        return self._speed

    @speed.setter
    def speed(self, speed: int):
        self._speed = speed

    @property
    def params(self) -> Dict[str, Any]:
        return self._params


class PublicPropertyErrorsMockJobTemplate(PublicPropertyErrorsMockJobBase,
                                          JobTemplate['PublicPropertyErrorsMockJob']):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type['PublicPropertyErrorsMockJob']:
        return PublicPropertyErrorsMockJob

    @classmethod
    def _apply_engine_decorator(cls, job: IsJob) -> IsJob:
        return job


class PublicPropertyErrorsMockJob(PublicPropertyErrorsMockJobBase,
                                  Job[PublicPropertyErrorsMockJobBase,
                                      PublicPropertyErrorsMockJobTemplate]):
    @classmethod
    def _get_job_base_subcls_for_init(cls) -> Type[PublicPropertyErrorsMockJobBase]:
        return PublicPropertyErrorsMockJobBase

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[PublicPropertyErrorsMockJobTemplate]:
        return PublicPropertyErrorsMockJobTemplate

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def _call_func(self, *args: Any, **kwargs: Any) -> Any:
        ...


class CommandMockJobBase(
        JobBase,
        DynamicMixinAcceptor,
        metaclass=JobBaseAndMixinAcceptorMeta,
):
    def __init__(self,
                 cmd_func: Callable,
                 command: str,
                 *,
                 name: Optional[str] = None,
                 id: str = '',
                 uppercase: bool = False,
                 params: Mapping[str, Union[int, str, bool]] = None,
                 **kwargs):

        super().__init__()
        self._cmd_func = cmd_func
        self._command = command
        self._id = id
        self._uppercase = uppercase
        self._params = dict(params) if params is not None else {}
        self.engine_decorator_applied = False

    def _get_init_arg_values(self) -> Union[Tuple[()], Tuple[Any, ...]]:
        return self._cmd_func, self._command

    def _get_init_kwarg_public_property_keys(self) -> Tuple[str, ...]:
        return 'id', 'uppercase', 'params'

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
class CommandMockJobTemplate(CallableDecoratingJobTemplateMixin['CommandMockJobTemplate'],
                             CommandMockJobBase,
                             JobTemplate['CommandMockJob']):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type['CommandMockJob']:
        return CommandMockJob

    def _apply_engine_decorator(self, job: IsJob) -> IsJob:
        self.engine_decorator_applied = True
        return job


class CommandMockJob(CommandMockJobBase, Job[CommandMockJobBase, CommandMockJobTemplate]):
    @classmethod
    def _get_job_base_subcls_for_init(cls) -> Type[CommandMockJobBase]:
        return CommandMockJobBase

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[CommandMockJobTemplate]:
        return CommandMockJobTemplate

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self._call_func(*args, **kwargs)

    def _call_func(self, *args: Any, **kwargs: Any) -> Any:
        if self._command in ['erase', 'restore']:
            if 'what' in self.params:
                log = f"{self.params['what']} has been {self._command}d" \
                      f"{', ' + self.params['where'] if 'where' in self.params else ''}"
            else:
                log = 'I know nothing'
            return log.upper() if self._uppercase else log


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
