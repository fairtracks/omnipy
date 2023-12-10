from abc import abstractmethod
from datetime import datetime
from functools import update_wrapper
import logging
from types import MappingProxyType
from typing import Any, cast, Hashable, Type

from omnipy.api.exceptions import JobStateException
from omnipy.api.protocols.private.compute.job import IsJob, IsJobBase, IsJobTemplate
from omnipy.api.protocols.private.compute.job_creator import IsJobCreator
from omnipy.api.protocols.private.engine import IsEngine
from omnipy.api.protocols.private.util import IsCallableClass
from omnipy.api.protocols.public.config import IsJobConfig
from omnipy.compute.job_creator import JobBaseMeta
from omnipy.compute.mixins.name import NameJobBaseMixin, NameJobMixin
from omnipy.log.mixin import LogMixin
from omnipy.util.helpers import as_dictable, create_merged_dict
from omnipy.util.mixin import DynamicMixinAcceptor


class JobBase(LogMixin, DynamicMixinAcceptor, metaclass=JobBaseMeta):
    @property
    def _job_creator(self) -> IsJobCreator:
        return self.__class__.job_creator

    @property
    def config(self) -> IsJobConfig | None:
        return self.__class__.job_creator.config

    @property
    def engine(self) -> IsEngine | None:
        return self.__class__.job_creator.engine

    @property
    def in_flow_context(self) -> bool:
        return self.__class__.nested_context_level > 0

    def __init__(self, *args: object, **kwargs: object):
        # super().__init__()

        # TODO: refactor using state machine

        if not isinstance(self, JobTemplateMixin) and not isinstance(self, JobMixin):
            raise JobStateException('JobBase and subclasses not inheriting from JobTemplateMixin '
                                    'or JobMixin are not directly instantiatable')

        from_apply = hasattr(self, '_from_apply') and self._from_apply is True
        if isinstance(self, JobMixin) and not from_apply:
            raise JobStateException(
                'JobMixin should only be instantiated using the "apply()" method of '
                'an instance of JobTemplateMixin (or one of its subclasses)')

    @classmethod
    def _create_job_template(cls, *args: object, **kwargs: object) -> IsJobTemplate:
        if len(args) >= 1:
            cls_as_callable_class = cast(Type[IsCallableClass], cls)

            if not callable(args[0]):
                raise TypeError(f'First argument of a job is assumed to be a callable, '
                                f'not: {args[0]}')
            job_func = args[0]
            args = args[1:]
            obj_1 = cls_as_callable_class(*args, **kwargs)(job_func)
            return cast(IsJobTemplate, obj_1)
        else:
            obj_2 = cls(*args, **kwargs)
            return cast(IsJobTemplate, obj_2)

    @classmethod
    def _create_job(cls, *args: object, **kwargs: object) -> IsJob:
        if cls.__new__ is object.__new__:
            obj = cls.__new__(cls)
        else:
            obj = cls.__new__(cls, *args, **kwargs)

        # TODO: refactor using state machine

        obj._from_apply = True
        obj.__init__(*args, **kwargs)
        obj._from_apply = False

        return cast(IsJob, obj)

    def _apply(self) -> IsJob:
        job_cls = self._get_job_subcls_for_apply()
        job = job_cls.create_job(*self._get_init_args(), **self._get_init_kwargs())

        if self.engine:
            job._apply_engine_decorator(self.engine)

        return job

    def _refine(self, *args: Any, update: bool = True, **kwargs: object) -> IsJobTemplate:
        self_as_job_template = cast(IsJobTemplate, self)

        refine_kwargs = kwargs.copy()

        if update:
            for key, cur_val in self._get_init_kwargs().items():
                if key in refine_kwargs:
                    refine_val = refine_kwargs[key]
                    cur_val_dictable = as_dictable(cur_val)
                    refine_val_dictable = as_dictable(refine_val)
                    if cur_val_dictable is not None and refine_val_dictable is not None:
                        new_val: object | dict = create_merged_dict(cur_val_dictable,
                                                                    refine_val_dictable)
                    else:
                        new_val = refine_kwargs[key]
                else:
                    new_val = cur_val
                refine_kwargs[key] = new_val

        init_args = self._get_init_args()
        refine_args = [init_args[0]] if len(init_args) >= 1 else []
        refine_args += args if args else init_args[1:]

        return self_as_job_template.create_job_template(*refine_args, **refine_kwargs)

    def _revise(self) -> IsJobTemplate:
        job_template_cls = self._get_job_template_subcls_for_revise()
        job_template = job_template_cls.create_job_template(*self._get_init_args(),
                                                            **self._get_init_kwargs())
        return job_template

    def _get_init_args(self) -> tuple[object, ...]:
        return ()

    def _get_init_kwargs(self) -> dict[str, object]:
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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, JobBase):
            return NotImplemented
        return self._get_init_args() == other._get_init_args() \
            and self._get_init_kwargs() == other._get_init_kwargs()

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[IsJobTemplate]:
        return IsJobTemplate

    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type[IsJob]:
        return IsJob

    def _call_job_template(self, *args: object, **kwargs: object) -> object:
        self_as_job_template = cast(IsJobTemplate, self)

        if self.in_flow_context:
            return self_as_job_template.run(*args, **kwargs)

        raise TypeError(f"'{self.__class__.__name__}' object is not callable")

    def _call_job(self, *args: object, **kwargs: object) -> object:
        pass

    def _check_engine(self, engine_protocol: Type):
        if self.engine is None or not isinstance(self.engine, engine_protocol):
            raise RuntimeError(f'Engine "{self.engine}" does not support '
                               f'job runner protocol: {engine_protocol.__name__}')


class JobTemplateMixin:
    def __init__(self, *args, **kwargs):
        if JobBase not in self.__class__.__mro__:
            raise TypeError('JobTemplateMixin is not meant to be instantiated outside the context '
                            'of a JobBase subclass.')

    @classmethod
    def create_job_template(cls: Type[IsJobBase], *args: object, **kwargs: object) -> IsJobTemplate:
        return cls._create_job_template(*args, **kwargs)

    def run(self, *args: object, **kwargs: object) -> object:
        # TODO: Using JobTemplateMixin.run() inside flows should give error message

        return self.apply()(*args, **kwargs)

    def apply(self) -> IsJob:
        self_as_job_base = cast(IsJobBase, self)
        job = self_as_job_base._apply()
        update_wrapper(job, self, updated=[])
        return job

    def refine(self, *args: Any, update: bool = True, **kwargs: object) -> IsJobTemplate:
        self_as_job_base = cast(IsJobBase, self)
        return self_as_job_base._refine(*args, update=update, **kwargs)

    def __call__(self, *args: object, **kwargs: object) -> object:
        self_as_job_base = cast(IsJobBase, self)
        return self_as_job_base._call_job_template(*args, **kwargs)


class JobMixin(DynamicMixinAcceptor):
    def __init__(self, *args, **kwargs):
        if JobBase not in self.__class__.__mro__:
            raise TypeError('JobMixin is not meant to be instantiated outside the context '
                            'of a JobBase subclass.')

    @abstractmethod
    def _apply_engine_decorator(self, engine: IsEngine) -> None:
        ...

    @property
    def time_of_cur_toplevel_flow_run(self) -> datetime | None:
        self_as_job_base = cast(IsJobBase, self)
        return self_as_job_base._job_creator.time_of_cur_toplevel_nested_context_run

    @classmethod
    def create_job(cls, *args: object, **kwargs: object) -> IsJob:
        cls_as_job_base = cast(IsJobBase, cls)
        return cls_as_job_base._create_job(*args, **kwargs)

    def revise(self) -> IsJobTemplate:
        self_as_job_base = cast(IsJobBase, self)
        job_template = self_as_job_base._revise()
        update_wrapper(job_template, self, updated=[])
        return job_template

    def __call__(self, *args: object, **kwargs: object) -> object:
        self_as_job_base = cast(IsJobBase, self)

        try:
            return self_as_job_base._call_job(*args, **kwargs)
        except Exception as e:
            self_as_job_base.log(str(e), level=logging.ERROR)
            raise


# TODO: Change JobBase and friends into Generics such as one can annotated with
#       e.g. 'TaskTemplate[[int], int]' instead of just 'TaskTemplate'

JobBase.accept_mixin(NameJobBaseMixin)
JobMixin.accept_mixin(NameJobMixin)
