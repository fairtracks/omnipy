from __future__ import annotations

from abc import ABCMeta, abstractmethod
from datetime import datetime
from functools import update_wrapper
from types import MappingProxyType
from typing import Any, Dict, Generic, Hashable, Optional, Tuple, Type, Union

from omnipy.compute.job_types import JobBaseT, JobT, JobTemplateT
from omnipy.compute.mixins.name import NameJobBaseMixin, NameJobMixin
from omnipy.config.job import JobConfig
from omnipy.engine.protocols import IsJob, IsJobConfig, IsJobCreator, IsTaskRunnerEngine
from omnipy.util.helpers import create_merged_dict
from omnipy.util.mixin import DynamicMixinAcceptor, DynamicMixinAcceptorFactory


class JobCreator:
    def __init__(self) -> None:
        self._engine: Optional[IsTaskRunnerEngine] = None
        self._config: Optional[IsJobConfig] = None
        self._nested_context_level: int = 0
        self._datetime_of_nested_context_run: Optional[datetime] = None

    def set_engine(self, engine: IsTaskRunnerEngine) -> None:
        self._engine = engine

    def set_config(self, config: IsJobConfig) -> None:
        self._config = config

    def __enter__(self):
        if self._nested_context_level == 0:
            self._datetime_of_nested_context_run = datetime.now()

        self._nested_context_level += 1

    def __exit__(self, exc_type, exc_value, traceback):
        self._nested_context_level -= 1

        if self._nested_context_level == 0:
            self._datetime_of_nested_context_run = None

    @property
    def engine(self) -> Optional[IsTaskRunnerEngine]:
        return self._engine

    @property
    def config(self) -> Optional[IsJobConfig]:
        return self._config

    @property
    def nested_context_level(self) -> int:
        return self._nested_context_level

    @property
    def datetime_of_nested_context_run(self) -> datetime:
        return self._datetime_of_nested_context_run


# TODO: test datetime_of_nested_context_run


class JobBaseMeta(ABCMeta):
    _job_creator: IsJobCreator = JobCreator()

    @property
    def job_creator(self) -> IsJobCreator:
        return self._job_creator

    @property
    def config(self) -> Optional[IsJobConfig]:
        return self.job_creator.config


class JobTemplateMeta(JobBaseMeta):
    @property
    def engine(self) -> Optional[IsTaskRunnerEngine]:
        return self.job_creator.engine

    @property
    def nested_context_level(self) -> int:
        return self.job_creator.nested_context_level


class JobBaseAndMixinAcceptorMeta(JobBaseMeta, DynamicMixinAcceptorFactory):
    ...


class JobTemplateAndMixinAcceptorMeta(JobTemplateMeta, JobBaseAndMixinAcceptorMeta):
    ...


class JobBase(DynamicMixinAcceptor, metaclass=JobBaseAndMixinAcceptorMeta):
    def __init__(self, *args: object, name: Optional[str] = None, **kwargs: object):
        super().__init__(*args, **kwargs)

        if not isinstance(self, JobTemplate) and not isinstance(self, Job):
            raise RuntimeError('JobBase and subclasses not inheriting from JobTemplate '
                               'or Job are not directly instantiatable')

    @abstractmethod
    def _get_init_arg_values(self) -> Union[Tuple[()], Tuple[Any, ...]]:
        ...

    def _get_init_args(self) -> Union[Tuple[()], Tuple[Any, ...]]:
        return self._get_init_arg_values()

    @abstractmethod
    def _get_init_kwarg_public_property_keys(self) -> Tuple[str, ...]:
        ...

    def _get_init_kwargs(self) -> Dict[str, Any]:
        kwarg_keys = list(self._mixin_init_kwarg_params.keys())
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

    def __eq__(self, other: object):
        if not isinstance(other, JobBase):
            return NotImplemented
        return self._get_init_args() == other._get_init_args() \
            and self._get_init_kwargs() == other._get_init_kwargs()

    @property
    def config(self) -> Optional[IsJobConfig]:
        return self.__class__.job_creator.config

    @property
    def in_flow_context(self) -> bool:
        return self.__class__.job_creator.nested_context_level > 0


JobBase.accept_mixin(NameJobBaseMixin)


class JobTemplate(JobBase, Generic[JobT], metaclass=JobTemplateAndMixinAcceptorMeta):
    @classmethod
    @abstractmethod
    def _get_job_subcls_for_apply(cls) -> Type[JobT]:
        return Job

    @property
    def engine(self) -> Optional[IsTaskRunnerEngine]:
        return self.__class__.engine

    @abstractmethod
    def _apply_engine_decorator(self, job: IsJob) -> IsJob:
        ...

    @classmethod
    def create(cls: Type[JobTemplateT], *init_args: object, **init_kwargs: object) -> JobTemplateT:
        return cls(*init_args, **init_kwargs)

    def run(self, *args: object, **kwargs: object):
        return self.apply()(*args, **kwargs)

    def apply(self) -> JobT:
        job_cls = self._get_job_subcls_for_apply()
        job = job_cls.create(*self._get_init_args(), **self._get_init_kwargs())
        update_wrapper(job, self, updated=[])
        return self._apply_engine_decorator(job)

    def refine(self: JobTemplateT,
               *args: object,
               update: bool = True,
               **kwargs: object) -> JobTemplateT:
        if update:
            for key, cur_val in self._get_init_kwargs().items():
                if key in kwargs:
                    try:
                        new_val = create_merged_dict(cur_val, kwargs[key])
                    except (TypeError, ValueError):
                        new_val = kwargs[key]
                else:
                    new_val = cur_val
                kwargs[key] = new_val

        return self.create(*args or self._get_init_args(), **kwargs)

    def __call__(self, *args, **kwargs):
        if self.in_flow_context:
            job = self.apply()
            return job(*args, **kwargs)
        raise TypeError(f"'{self.__class__.__name__}' object is not callable")


class CallableDecoratingJobTemplateMixin:
    @classmethod
    def create(cls: Type[JobTemplateT], *init_args: object, **init_kwargs: object) -> JobTemplateT:
        return cls(*(init_args[1:]), **init_kwargs)(init_args[0])


class Job(JobBase, DynamicMixinAcceptor, Generic[JobBaseT, JobTemplateT]):
    @property
    def flow_context(self) -> IsJobCreator:
        return self.__class__.job_creator

    @property
    def datetime_of_flow_run(self) -> datetime:
        return self.__class__.job_creator.datetime_of_nested_context_run

    @classmethod
    @abstractmethod
    def _get_job_base_subcls_for_init(cls) -> Type[JobBaseT]:
        return JobBase

    @classmethod
    @abstractmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[JobTemplateT]:
        return JobTemplate

    def __new__(cls, *args: Any, **kwargs: Any):
        super().__new__(cls, *args, **kwargs)
        raise RuntimeError('Job should only be instantiated using the "apply()" method of '
                           'an instance of JobTemplate (or one of its subclasses)')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def create(cls, *init_args: object, **init_kwargs: object) -> Job[JobBaseT, JobTemplateT]:
        job_base_cls = cls._get_job_base_subcls_for_init()
        if job_base_cls.__new__ is object.__new__:
            job_obj = job_base_cls.__new__(cls)
        else:
            job_obj = job_base_cls.__new__(cls, *init_args, **init_kwargs)
        job_obj.__init__(*init_args, **init_kwargs)
        return job_obj

    def revise(self) -> JobTemplateT:
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


Job.accept_mixin(NameJobMixin)

# TODO: Change JobBase and friends into Generics such as one can annotated with
#       e.g. 'TaskTemplate[[int], int]' instead of just 'TaskTemplate'
