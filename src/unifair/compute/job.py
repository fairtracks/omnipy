from __future__ import annotations

from abc import ABCMeta, abstractmethod
from functools import update_wrapper
from types import MappingProxyType
from typing import Any, Dict, Generic, Hashable, Mapping, Optional, Tuple, Type, TypeVar, Union

from inflection import underscore
from prefect.utilities.names import generate_slug
from slugify import slugify

from unifair.engine.protocols import IsJobCreator, IsTaskRunnerEngine
from unifair.util.helpers import create_merged_dict


class JobCreator:
    def __init__(self) -> None:
        self._engine: Optional[IsTaskRunnerEngine] = None
        self._nested_context_level = 0

    def set_engine(self, engine: IsTaskRunnerEngine) -> None:
        self._engine = engine

    def __enter__(self):
        self._nested_context_level += 1

    def __exit__(self, exc_type, exc_value, traceback):
        self._nested_context_level -= 1

    @property
    def engine(self) -> Optional[IsTaskRunnerEngine]:
        return self._engine

    @property
    def nested_context_level(self) -> int:
        return self._nested_context_level


class JobConfigMeta(ABCMeta):
    _job_creator: JobCreator = JobCreator()

    @property
    def job_creator(self) -> JobCreator:
        return self._job_creator


class JobTemplateMeta(JobConfigMeta):
    @property
    def engine(self) -> Optional[IsTaskRunnerEngine]:
        return self.job_creator.engine

    @property
    def nested_context_level(self) -> int:
        return self.job_creator.nested_context_level


class JobConfig(metaclass=JobConfigMeta):
    def __init__(self, *, name: Optional[str] = None, **kwargs: Any):
        super().__init__()

        if not isinstance(self, JobTemplate) and not isinstance(self, Job):
            raise RuntimeError('JobConfig and subclasses not inheriting from JobTemplate '
                               'or Job are not directly instantiatable')

        self._name: Optional[str] = name

        if self._name is not None:
            self._check_not_empty_string('name', self.name)

        self._unique_name = None

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

    @property
    def unique_name(self) -> str:
        return self._unique_name

    def __eq__(self, other: object):
        if not isinstance(other, JobConfig):
            return NotImplemented
        return self._get_init_args() == other._get_init_args() \
            and self._get_init_kwargs() == other._get_init_kwargs()

    @property
    def in_flow_context(self) -> bool:
        return self.__class__.job_creator.nested_context_level > 0


class JobTemplate(JobConfig, metaclass=JobTemplateMeta):
    @classmethod
    @abstractmethod
    def _get_job_subcls_for_apply(cls) -> Type[Job]:
        return Job

    @property
    def engine(self) -> Optional[IsTaskRunnerEngine]:
        return self.__class__.engine

    @abstractmethod
    def _apply_engine_decorator(self, job: Job) -> Job:
        ...

    @classmethod
    def create(cls, *init_args: object, **init_kwargs: object) -> JobTemplate:
        return cls(*init_args, **init_kwargs)

    def run(self, *args: object, **kwargs: object):
        return self.apply()(*args, **kwargs)

    def apply(self) -> Job:
        job_cls = self._get_job_subcls_for_apply()
        job = job_cls.create(*self._get_init_args(), **self._get_init_kwargs())
        update_wrapper(job, self, updated=[])
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

        return self.create(*self._get_init_args(), **kwargs)

    def __call__(self, *args, **kwargs):
        if self.in_flow_context:
            job = self.apply()
            return job(*args, **kwargs)
        raise TypeError("'{}' object is not callable".format(self.__class__.__name__))


JobTemplateT = TypeVar('JobTemplateT', bound=JobTemplate)


class CallableDecoratingJobTemplateMixin(Generic[JobTemplateT]):
    @classmethod
    def create(cls: Type[JobTemplateT], *init_args: object, **init_kwargs: object) -> JobTemplateT:
        return cls(*(init_args[1:]), **init_kwargs)(init_args[0])


class Job(JobConfig):
    def _generate_unique_name(self):
        if self._name is None:
            return None
        class_name_snake_case = underscore(self.__class__.__name__)
        self._unique_name = slugify(f'{class_name_snake_case}-{self._name}-{generate_slug(2)}')

    def regenerate_unique_name(self) -> None:
        self._generate_unique_name()

    @property
    def flow_context(self) -> IsJobCreator:
        return self.__class__.job_creator

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
    def create(cls, *init_args: object, **init_kwargs: object) -> Job:
        job_obj = object.__new__(cls)
        job_config_cls = cls._get_job_config_subcls_for_init()
        job_config_cls.__init__(job_obj, *init_args, **init_kwargs)
        job_obj._generate_unique_name()
        return job_obj

    def revise(self) -> JobTemplate:
        job_template_cls = self._get_job_template_subcls_for_revise()
        job_template = job_template_cls.create(*self._get_init_args(), **self._get_init_kwargs())
        update_wrapper(job_template, self, updated=[])
        return job_template

    @abstractmethod
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @abstractmethod
    def _call_func(self, *args: Any, **kwargs: Any) -> Any:
        ...


# TODO: Change JobConfig and friends into Generics such as one can annotated with
#       e.g. 'TaskTemplate[[int], int]' instead of just 'TaskTemplate'
