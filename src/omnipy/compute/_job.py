from abc import abstractmethod
from datetime import datetime
from functools import update_wrapper
import logging
from types import MappingProxyType
from typing import Any, Callable, cast, Generic, Hashable, ParamSpec, Type, TypeVar

from omnipy.compute._job_creator import JobBaseMeta
from omnipy.compute._mixins.name import NameJobBaseMixin, NameJobMixin
from omnipy.hub.log.mixin import LogMixin
from omnipy.shared._typedefs import _JobT, _JobTemplateT
from omnipy.shared.exceptions import JobStateException, ShouldNotOccurException
from omnipy.shared.protocols.compute._job import IsJob, IsJobBase, IsJobTemplate
from omnipy.shared.protocols.compute.job_creator import IsJobCreator
from omnipy.shared.protocols.config import IsJobConfig
from omnipy.shared.protocols.engine.base import IsEngine
from omnipy.util.helpers import as_dictable, create_merged_dict
from omnipy.util.mixin import DynamicMixinAcceptor

_CallP = ParamSpec('_CallP')
_RetT = TypeVar('_RetT')


class JobBase(
        LogMixin,
        DynamicMixinAcceptor,
        Generic[_JobTemplateT, _JobT, _CallP, _RetT],
        metaclass=JobBaseMeta):
    @property
    def _job_creator(self) -> IsJobCreator:
        return self.__class__.job_creator

    @property
    def config(self) -> IsJobConfig:
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

        self._from_apply: bool
        from_apply: bool = hasattr(self, '_from_apply') and self._from_apply is True
        if isinstance(self, JobMixin) and not from_apply:
            raise JobStateException(
                'JobMixin should only be instantiated using the "apply()" method of '
                'an instance of JobTemplateMixin (or one of its subclasses)')

    @classmethod
    def _create_job_template(cls, *args: object, **kwargs: object) -> _JobTemplateT:
        if len(args) >= 1:
            cls_as_doubly_callable = cast(Callable[..., Callable[[Callable], _JobTemplateT]], cls)

            if not callable(args[0]):
                raise TypeError(f'First argument of a job is assumed to be a callable, '
                                f'not: {args[0]}')
            job_func = args[0]
            args = args[1:]
            return cls_as_doubly_callable(*args, **kwargs)(job_func)
        else:
            cls_as_callable = cast(Callable[..., _JobTemplateT], cls)
            return cls_as_callable(*args, **kwargs)

    @classmethod
    def _create_job(cls, *args: object, **kwargs: object) -> _JobT:
        if cls.__new__ is object.__new__:
            obj = cls.__new__(cls)
        else:
            obj = cls.__new__(cls, *args, **kwargs)

        # TODO: refactor using state machine

        obj._from_apply = True
        obj.__init__(*args, **kwargs)
        obj._from_apply = False

        return cast(_JobT, obj)

    def _apply(self) -> _JobT:
        job_cls = self._get_job_subcls_for_apply()
        job = job_cls.create_job(*self._get_init_args(), **self._get_init_kwargs())
        if self.engine:
            job._apply_engine_decorator(self.engine)

        return cast(_JobT, job)

    def _refine(self, *args: Any, update: bool = True, **kwargs: object) -> _JobTemplateT:
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

    def _revise(self) -> _JobTemplateT:
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
    def _get_job_template_subcls_for_revise(
            cls) -> type[IsJobTemplate[_JobTemplateT, _JobT, _CallP, _RetT]]:
        raise ShouldNotOccurException()

    @classmethod
    def _get_job_subcls_for_apply(
        cls
    ) -> type[IsJob[_JobTemplateT, IsJob[_JobTemplateT, _JobT, _CallP, _RetT], _CallP, _RetT]]:
        raise ShouldNotOccurException()

    def _call_job_template(self, *args: _CallP.args, **kwargs: _CallP.kwargs) -> _RetT:
        self_as_job_template = cast(IsJobTemplate[_JobTemplateT, _JobT, _CallP, _RetT], self)

        if self.in_flow_context:
            return self_as_job_template.run(*args, **kwargs)

        raise TypeError(f"'{self.__class__.__name__}' object is not callable. Try .run() method")

    def _call_job(self, *args: _CallP.args, **kwargs: _CallP.kwargs) -> _RetT:
        ...

    def _check_engine(self, engine_protocol: Type):
        if self.engine is None or not isinstance(self.engine, engine_protocol):
            raise RuntimeError(f'Engine "{self.engine}" does not support '
                               f'job runner protocol: {engine_protocol.__name__}')


class JobTemplateMixin(Generic[_JobTemplateT, _JobT, _CallP, _RetT]):
    def __init__(self, *args: object, **kwargs: object):
        if JobBase not in self.__class__.__mro__:
            raise TypeError('JobTemplateMixin is not meant to be instantiated outside the context '
                            'of a JobBase subclass.')

    @classmethod
    def create_job_template(cls, *args: object, **kwargs: object) -> _JobTemplateT:
        cls_as_job_base = cast(type[IsJobBase[_JobTemplateT, _JobT, _CallP, _RetT]], cls)
        return cls_as_job_base._create_job_template(*args, **kwargs)

    def _cast_to_job_tmpl(
        self
    ) -> IsJobTemplate[_JobTemplateT, IsJob[_JobTemplateT, _JobT, _CallP, _RetT], _CallP, _RetT]:
        return cast(
            IsJobTemplate[_JobTemplateT, IsJob[_JobTemplateT, _JobT, _CallP, _RetT], _CallP, _RetT],
            self)

    def run(self, *args: _CallP.args, **kwargs: _CallP.kwargs) -> _RetT:
        # TODO: Using JobTemplateMixin.run() inside flows should give error message
        return self._cast_to_job_tmpl().apply()(*args, **kwargs)

    def apply(self) -> _JobT:
        job = self._cast_to_job_tmpl()._apply()
        update_wrapper(job, self, updated=[])
        return cast(_JobT, job)

    def refine(self, *args: Any, update: bool = True, **kwargs: object) -> _JobTemplateT:
        self_as_job_base = cast(IsJobBase[_JobTemplateT, _JobT, _CallP, _RetT], self)
        return self_as_job_base._refine(*args, update=update, **kwargs)

    def __call__(self, *args: _CallP.args, **kwargs: _CallP.kwargs) -> _RetT:
        self_as_job_base = cast(IsJobBase[_JobTemplateT, _JobT, _CallP, _RetT], self)
        return self_as_job_base._call_job_template(*args, **kwargs)


class JobMixin(DynamicMixinAcceptor, Generic[_JobTemplateT, _JobT, _CallP, _RetT]):
    def __init__(self, *args, **kwargs):
        if JobBase not in self.__class__.__mro__:
            raise TypeError('JobMixin is not meant to be instantiated outside the context '
                            'of a JobBase subclass.')

    @abstractmethod
    def _apply_engine_decorator(self, engine: IsEngine) -> None:
        ...

    @property
    def time_of_cur_toplevel_flow_run(self) -> datetime | None:
        self_as_job_base = cast(IsJobBase[_JobTemplateT, _JobT, _CallP, _RetT], self)
        return self_as_job_base._job_creator.time_of_cur_toplevel_nested_context_run

    @classmethod
    def create_job(cls, *args: object, **kwargs: object) -> _JobT:
        cls_as_job_base = cast(IsJobBase[_JobTemplateT, _JobT, _CallP, _RetT], cls)
        return cls_as_job_base._create_job(*args, **kwargs)

    def revise(self) -> _JobTemplateT:
        self_as_job_base = cast(
            IsJobBase[IsJobTemplate[_JobTemplateT, _JobT, _CallP, _RetT], _JobT, _CallP, _RetT],
            self)
        job_template = self_as_job_base._revise()
        update_wrapper(job_template, self, updated=[])
        return cast(_JobTemplateT, job_template)

    def __call__(self, *args: _CallP.args, **kwargs: _CallP.kwargs) -> _RetT:
        self_as_job_base = cast(IsJobBase[_JobTemplateT, _JobT, _CallP, _RetT], self)

        try:
            return self_as_job_base._call_job(*args, **kwargs)
        except Exception as e:
            self_as_job_base.log(str(e), level=logging.ERROR)
            raise


# TODO: Change JobBase and friends into Generics such as one can annotated with
#       e.g. 'TaskTemplate[[int], int]' instead of just 'TaskTemplate'

JobBase.accept_mixin(NameJobBaseMixin)
JobMixin.accept_mixin(NameJobMixin)
