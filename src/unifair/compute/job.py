from __future__ import annotations

from abc import ABCMeta, abstractmethod
from types import MappingProxyType
from typing import Any, Dict, Hashable, Mapping, Optional, Tuple, Type, Union

from unifair.engine.protocols import IsTaskRunnerEngine
from unifair.util.helpers import create_merged_dict


class JobCreator:
    def __init__(self):
        self._engine: Optional[IsTaskRunnerEngine] = None

    def set_engine(self, engine: IsTaskRunnerEngine) -> None:
        self._engine = engine

    @property
    def engine(self) -> Optional[IsTaskRunnerEngine]:
        return self._engine


class JobConfigMeta(ABCMeta):
    _job_creator: JobCreator = JobCreator()

    @property
    def job_creator(self) -> JobCreator:
        return self._job_creator


class JobTemplateMeta(JobConfigMeta):
    @property
    def engine(self) -> Optional[IsTaskRunnerEngine]:
        return self.job_creator.engine


class JobConfig(metaclass=JobConfigMeta):
    def __init__(self, *, name: Optional[str] = None, **kwargs: Any):
        super().__init__()

        if not isinstance(self, JobTemplate) and not isinstance(self, Job):
            raise RuntimeError('JobConfig and subclasses not inheriting from JobTemplate '
                               'or Job are not directly instantiatable')

        self._name: Optional[str] = name

        if self._name is not None:
            self._check_not_empty_string('name', self.name)

    @staticmethod
    def _check_not_empty_string(param_name: str, param: str) -> None:
        if len(param) == 0:
            raise ValueError('Empty strings not allowed for parameter "{}"'.format(param_name))

    @abstractmethod
    def _get_init_arg_values(self) -> Union[Tuple[()], Tuple[Any, ...]]:
        ...

    def _get_init_args(self) -> Union[Tuple[()], Tuple[Any, ...]]:
        return self._get_init_arg_values()

    @abstractmethod
    def _get_init_kwarg_public_property_keys(self) -> Tuple[str, ...]:
        ...

    def _get_init_kwargs(self) -> Dict[str, Any]:
        kwarg_keys = ['name']
        kwarg_keys += list(self._get_init_kwarg_public_property_keys())
        for key in kwarg_keys:
            attribute = getattr(self.__class__, key)

            if not isinstance(attribute, property):
                raise TypeError(f'{self.__class__.__name__} attribute "{key}" is not a property')

            if attribute.fset is not None:
                raise TypeError(f'{self.__class__.__name__} attribute "{key}" is not a property')

            value = getattr(self, key)
            if not isinstance(value, Hashable) and not isinstance(value, MappingProxyType):
                raise TypeError(f'Value of {self.__class__.__name__} attribute "{key}" is mutable')

        return {key: getattr(self, key) for key in kwarg_keys}

    @property
    def name(self) -> str:
        return self._name

    def __eq__(self, other: object):
        if not isinstance(other, JobConfig):
            return NotImplemented
        return self._get_init_args() == other._get_init_args() \
            and self._get_init_kwargs() == other._get_init_kwargs()


class JobTemplate(JobConfig, metaclass=JobTemplateMeta):
    @classmethod
    @abstractmethod
    def _get_job_subcls_for_apply(cls) -> Type[Job]:
        return Job

    @property
    def engine(self) -> Optional[IsTaskRunnerEngine]:
        return self.__class__.engine

    @classmethod
    @abstractmethod
    def _apply_engine_decorator(cls, job: Job) -> Job:
        ...

    def apply(self) -> Job:
        job = self._get_job_subcls_for_apply().from_job_template(self)
        return self._apply_engine_decorator(job)

    def refine(self, update: bool = True, **kwargs: Any) -> JobTemplate:
        if update:
            for key, cur_val in self._get_init_kwargs().items():
                if key in kwargs:
                    new_val = create_merged_dict(cur_val, kwargs[key]) \
                        if isinstance(cur_val, Mapping) else kwargs[key]
                else:
                    new_val = cur_val
                kwargs[key] = new_val

        return self.__class__(*self._get_init_args(), **kwargs)


class Job(JobConfig):
    @classmethod
    @abstractmethod
    def _get_job_config_subcls_for_init(cls) -> Type[JobConfig]:
        return JobConfig

    @classmethod
    @abstractmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[JobTemplate]:
        return JobTemplate

    def __init__(self, *args: Any, **kwargs: Any):  # noqa
        raise RuntimeError('Job should only be instantiated using the "apply()" method of '
                           'an instance of JobTemplate (or one of its subclasses)')

    @classmethod
    def from_job_template(cls, job_template: JobTemplate):
        init_args = job_template._get_init_args()
        init_kwargs = job_template._get_init_kwargs()
        job_obj = object.__new__(cls)
        job_config_cls = cls._get_job_config_subcls_for_init()
        job_config_cls.__init__(job_obj, *init_args, **init_kwargs)
        return job_obj

    def revise(self) -> JobTemplate:
        job_template_cls = self._get_job_template_subcls_for_revise()
        return job_template_cls(*self._get_init_args(), **self._get_init_kwargs())

    @abstractmethod
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @abstractmethod
    def _call_func(self, *args: Any, **kwargs: Any) -> Any:
        ...


# TODO: Change JobConfig and friends into Generics such as one can annotated with
#       e.g. 'TaskTemplate[[int], int]' instead of just 'TaskTemplate'
