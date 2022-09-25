from types import MappingProxyType
from typing import Any, Dict, Mapping, Optional, Tuple, Type, Union

from unifair.compute.job import Job, JobConfig, JobTemplate


class MockJobConfigSubclass(JobConfig):
    def _get_init_arg_values(self) -> Union[Tuple[()], Tuple[Any, ...]]:
        return ()

    def _get_init_kwarg_public_property_keys(self) -> Tuple[str, ...]:
        return ()


class MockJobTemplateSubclass(JobTemplate, MockJobConfigSubclass):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type[Job]:
        return MockJobSubclass


class MockJobSubclass(Job, MockJobConfigSubclass):
    @classmethod
    def _get_job_config_subcls_for_init(cls) -> Type[JobConfig]:
        return MockJobConfigSubclass

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[JobTemplate]:
        return MockJobTemplateSubclass

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        ...


class PublicPropertyErrorsMockJobConfig(JobConfig):
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
                 params: Mapping[str, Union[int, str, bool]] = None):
        JobConfig.__init__(self, name=name)
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


class PublicPropertyErrorsMockJobTemplate(JobTemplate, PublicPropertyErrorsMockJobConfig):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type[Job]:
        return PublicPropertyErrorsMockJob


class PublicPropertyErrorsMockJob(Job, PublicPropertyErrorsMockJobConfig):
    @classmethod
    def _get_job_config_subcls_for_init(cls) -> Type[JobConfig]:
        return PublicPropertyErrorsMockJobConfig

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[JobTemplate]:
        return PublicPropertyErrorsMockJobTemplate

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        ...


class CommandMockJobConfig(JobConfig):
    def __init__(self,
                 command: str,
                 *,
                 name: Optional[str] = None,
                 uppercase: bool = False,
                 params: Mapping[str, Union[int, str, bool]] = None):
        JobConfig.__init__(self, name=name)
        self._command = command
        self._uppercase = uppercase
        self._params = dict(params) if params is not None else {}

    def _get_init_arg_values(self) -> Union[Tuple[()], Tuple[Any, ...]]:
        return self._command,

    def _get_init_kwarg_public_property_keys(self) -> Tuple[str, ...]:
        return 'uppercase', 'params'

    @property
    def uppercase(self) -> bool:
        return self._uppercase

    @property
    def params(self) -> MappingProxyType[str, Any]:
        return MappingProxyType(self._params)


class CommandMockJobTemplate(JobTemplate, CommandMockJobConfig):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type[Job]:
        return CommandMockJob


class CommandMockJob(Job, CommandMockJobConfig):
    @classmethod
    def _get_job_config_subcls_for_init(cls) -> Type[JobConfig]:
        return CommandMockJobConfig

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[JobTemplate]:
        return CommandMockJobTemplate

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if self._command in ['erase', 'restore']:
            if 'what' in self.params:
                log = f"{self.params['what']} has been {self._command}d" \
                      f"{', ' + self.params['where'] if 'where' in self.params else ''}"
            else:
                log = 'I know nothing'
            return log.upper() if self._uppercase else log