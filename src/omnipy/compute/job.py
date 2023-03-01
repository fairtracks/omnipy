from __future__ import annotations

from abc import abstractmethod
from datetime import datetime
from functools import update_wrapper
import logging
from types import MappingProxyType
from typing import Any, Dict, Hashable, Optional, Tuple

from omnipy.api.exceptions import JobStateException
from omnipy.api.protocols import IsEngine, IsJobConfig
from omnipy.compute.job_creator import JobBaseMeta
from omnipy.compute.mixins.name import NameJobBaseMixin, NameJobMixin
from omnipy.log.mixin import LogMixin
from omnipy.util.helpers import create_merged_dict
from omnipy.util.mixin import DynamicMixinAcceptor


class JobBase(LogMixin, DynamicMixinAcceptor, metaclass=JobBaseMeta):
    def __init__(self, *args: object, name: Optional[str] = None, **kwargs: object):
        # super().__init__()

        # TODO: refactor using state machine

        if not isinstance(self, JobTemplate) and not isinstance(self, Job):
            raise JobStateException('JobBase and subclasses not inheriting from JobTemplate '
                                    'or Job are not directly instantiatable')

        from_apply = hasattr(self, '_from_apply') and self._from_apply is True
        if isinstance(self, Job) and not from_apply:
            raise JobStateException('Job should only be instantiated using the "apply()" method of '
                                    'an instance of JobTemplate (or one of its subclasses)')

    @classmethod
    def _create_job_template(cls, *args: object, **kwargs: object):  # -> JobTemplateT:
        if len(args) >= 1:
            if not callable(args[0]):
                raise TypeError(f'First argument of a job is assumed to be a callable, '
                                f'not: {args[0]}')
            job_func = args[0]
            args = args[1:]
            return cls(*args, **kwargs)(job_func)
        else:
            return cls(*args, **kwargs)

    @classmethod
    def _create_job(cls, *args: object, **kwargs: object):  # -> Job[JobBaseT, JobTemplateT]:
        if cls.__new__ is object.__new__:
            job_obj = cls.__new__(cls)
        else:
            job_obj = cls.__new__(cls, *args, **kwargs)

        # TODO: refactor using state machine
        job_obj._from_apply = True
        job_obj.__init__(*args, **kwargs)
        job_obj._from_apply = False

        return job_obj

    def _apply(self):  # -> JobT:
        job_cls = self._get_job_subcls_for_apply()
        job = job_cls.create_job(*self._get_init_args(), **self._get_init_kwargs())
        update_wrapper(job, self, updated=[])
        job._apply_engine_decorator(self.engine)
        return job

    def _refine(self, *args: object, update: bool = True, **kwargs: object):  # -> JobTemplateT:
        refine_kwargs = kwargs.copy()

        if update:
            for key, cur_val in self._get_init_kwargs().items():
                if key in refine_kwargs:
                    try:
                        new_val = create_merged_dict(cur_val, refine_kwargs[key])
                    except (TypeError, ValueError):
                        new_val = refine_kwargs[key]
                else:
                    new_val = cur_val
                refine_kwargs[key] = new_val

        init_args = self._get_init_args()
        refine_args = [init_args[0]] if len(init_args) >= 1 else []
        refine_args += args if args else init_args[1:]

        return self.create_job_template(*refine_args, **refine_kwargs)

    def _revise(self):  # -> JobTemplateT:
        job_template_cls = self._get_job_template_subcls_for_revise()
        job_template = job_template_cls.create_job_template(*self._get_init_args(),
                                                            **self._get_init_kwargs())
        update_wrapper(job_template, self, updated=[])
        return job_template

    def _get_init_args(self) -> Tuple[object, ...]:
        return ()

    def _get_init_kwargs(self) -> Dict[str, Any]:
        kwarg_keys = list(self._mixin_init_kwarg_params_including_bases.keys())
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

    @classmethod
    # @abstractmethod
    def _get_job_template_subcls_for_revise(cls):  # -> Type[JobTemplateT]:
        return JobTemplate

    @classmethod
    # @abstractmethod
    def _get_job_subcls_for_apply(cls):  # -> Type[JobT]:
        return Job

    def _call_job_template(self, *args: object, **kwargs: object) -> object:
        if self.in_flow_context:
            return self.run(*args, **kwargs)
        raise TypeError(f"'{self.__class__.__name__}' object is not callable")

    def _call_job(self, *args: object, **kwargs: object) -> object:
        pass

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, JobBase):
            return NotImplemented
        return self._get_init_args() == other._get_init_args() \
            and self._get_init_kwargs() == other._get_init_kwargs()

    def _check_engine(self, engine_protocol: IsEngine):
        if self.engine is None or not isinstance(self.engine, engine_protocol):
            raise RuntimeError(f'Engine "{self.engine}" does not support '
                               f'job runner protocol: {engine_protocol.__name__}')

    @property
    def config(self) -> Optional[IsJobConfig]:
        return self.__class__.job_creator.config

    @property
    def engine(self) -> Optional[IsEngine]:
        return self.__class__.engine

    @property
    def in_flow_context(self) -> bool:
        return self.__class__.job_creator.nested_context_level > 0


class JobTemplate:
    def __init__(self, *args, **kwargs):
        if JobBase not in self.__class__.__mro__:
            raise TypeError('JobTemplate is not meant to be instantiated outside the context '
                            'of a JobBase subclass.')

    @classmethod
    def create_job_template(cls, *args: object, **kwargs: object):  # -> JobTemplateT:
        return cls._create_job_template(*args, **kwargs)

    def run(self, *args: object, **kwargs: object) -> object:
        return self.apply()(*args, **kwargs)

    def apply(self):  # -> JobT:
        return self._apply()

    def refine(self, *args: object, update: bool = True, **kwargs: object):  # -> JobTemplateT:
        return self._refine(*args, update=update, **kwargs)

    def __call__(self, *args: object, **kwargs: object) -> object:
        return self._call_job_template(*args, **kwargs)


class Job(DynamicMixinAcceptor):
    def __init__(self, *args, **kwargs):
        if JobBase not in self.__class__.__mro__:
            raise TypeError('Job is not meant to be instantiated outside the context '
                            'of a JobBase subclass.')

    @abstractmethod
    def _apply_engine_decorator(self, engine: IsEngine) -> None:
        ...

    @property
    def time_of_cur_toplevel_flow_run(self) -> datetime:
        return self.__class__.job_creator.time_of_cur_toplevel_nested_context_run

    # def __new__(cls, *args: Any, **kwargs: Any):
    #     super().__new__(cls, *args, **kwargs)
    #     raise RuntimeError('Job should only be instantiated using the "apply()" method of '
    #                        'an instance of JobTemplate (or one of its subclasses)')

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    @classmethod
    def create_job(cls, *args: object, **kwargs: object):
        return cls._create_job(*args, **kwargs)

    def revise(self):  # -> JobTemplateT:
        return self._revise()

    def __call__(self, *args: object, **kwargs: object) -> object:
        try:
            return self._call_job(*args, **kwargs)
        except Exception as e:
            self.log(e, level=logging.ERROR)
            raise


# TODO: Change JobBase and friends into Generics such as one can annotated with
#       e.g. 'TaskTemplate[[int], int]' instead of just 'TaskTemplate'

JobBase.accept_mixin(NameJobBaseMixin)
# JobBase.accept_mixin(LogMixin)
Job.accept_mixin(NameJobMixin)
