from copy import deepcopy
from dataclasses import dataclass
import functools
from typing import Any, Callable, cast, Concatenate, ParamSpec

from typing_extensions import dataclass_transform, TypeVar

import omnipy.util.pydantic as pyd

_ModelT = TypeVar('_ModelT')
_DatasetT = TypeVar('_DatasetT')
_ParamsT = TypeVar('_ParamsT')
_ParamsP = ParamSpec('_ParamsP')


class _ParamsMeta(pyd.ModelMetaclass):
    def __init__(cls, name: str, bases: tuple[type, ...], namespace: dict[str, object], **kwargs: object) -> None:
        super().__init__(name, bases, namespace, **kwargs)

        model_cls = cast(type[pyd.BaseModel], cls)
        default_vals = {}
        for field_name, field in model_cls.model_fields.items():
            if field.default_factory is not None:
                raise ValueError('Default factory is not supported for Params classes')

            default_vals[field_name] = field.default if field.default is not pyd.Undefined else None
            if default_vals[field_name] is None and not cls._field_allow_none(field):
                raise ValueError(f'{model_cls.__name__}.{field_name} must have a default value')

        try:
            values, fields_set, validation_error = \
                pyd.validate_model(model_cls, input_data={k: v for k, v in default_vals.items()})
        except RuntimeError:
            # ParamsBase.__new__ prevents instantiation, which pydantic v2
            # model_validate needs. Fall back to direct default extraction.
            values = default_vals
            validation_error = None

        if validation_error:
            raise validation_error

        for key, value in values.items():
            model_cls.model_fields[key].default = value

    @staticmethod
    def _field_allow_none(field: pyd.FieldInfo) -> bool:
        from omnipy.util.pydantic import is_none_type
        from typing import get_args
        ann = field.annotation
        if ann is None:
            return False
        return any(is_none_type(a) for a in get_args(ann))

    def __getattr__(cls, attr: str) -> object:
        model_cls = cast(type[pyd.BaseModel], cls)
        # Access __pydantic_fields__ via cls.__dict__ to avoid recursion:
        # model_fields property calls getattr(cls, '__pydantic_fields__', {}),
        # which triggers __getattr__ again -> infinite loop.
        pydantic_fields: dict = model_cls.__dict__.get('__pydantic_fields__', {})
        if attr in pydantic_fields:
            return cls._get_param_value(attr, pydantic_fields)
        raise AttributeError(f'{model_cls.__name__}.{attr} is not defined')

    def _get_param_value(cls, attr, pydantic_fields):
        finfo = pydantic_fields[attr]
        if finfo.default_factory is not None:
            return finfo.default_factory()
        else:
            return finfo.default

    def __setattr__(cls, attr: str, value: object) -> None:
        model_cls = cast(type[pyd.BaseModel], cls)
        pydantic_fields: dict = model_cls.__dict__.get('__pydantic_fields__', {})
        if attr in pydantic_fields:
            raise AttributeError(f'{model_cls.__name__}.{attr} is read-only')
        elif not attr.startswith('_'):
            raise AttributeError(f'{model_cls.__name__}.{attr} is not defined')
        super().__setattr__(attr, value)


class ParamsBase(pyd.BaseModel, metaclass=_ParamsMeta):
    class Config:
        arbitrary_types_allowed = True

    def __new__(cls, *args: object, **kwargs: object) -> None:  # type: ignore[misc]
        raise RuntimeError(f'{cls.__name__} cannot be instantiated')

    @classmethod
    def copy_and_adjust(cls, model_name: str, **kwargs: object) -> type['ParamsBase']:
        field_definitions: dict[str, Any] = {
            field_name: (cls.model_fields[field_name].annotation, deepcopy(cls.model_fields[field_name]))
            for field_name in cls.model_fields
        }

        for key, value in kwargs.items():
            field_definitions[key] = (field_definitions[key][0], pyd.Field(default=value))

        return pyd.create_model(  # type: ignore[call-overload]
            model_name, __base__=ParamsBase, **field_definitions)


def bind_adjust_model_func(
    clone_model_func: Callable[..., type[_ModelT]],
    params_cls: Callable[_ParamsP, Any],
) -> Callable[Concatenate[str, _ParamsP], type[_ModelT]]:
    def _func(model_name: str, *args: _ParamsP.args, **kwargs: _ParamsP.kwargs) -> type[_ModelT]:
        if len(args) > 0:
            raise AttributeError(f'Positional arguments are not supported for '
                                 f'{params_cls.__module__}.{params_cls.__name__}')
        new_model_cls = clone_model_func(model_name)
        new_model_cls.Params = params_cls.copy_and_adjust(  # type: ignore[attr-defined]
            'Params',
            **kwargs,
        )
        return new_model_cls

    return _func


def bind_adjust_dataset_func(
    clone_dataset_func: Callable[..., type[_DatasetT]],
    model_cls: type[_ModelT],
    params_cls: Callable[_ParamsP, Any],
) -> Callable[Concatenate[str, str, _ParamsP], type[_DatasetT]]:
    def _func(dataset_name: str, model_name: str, *args: _ParamsP.args,
              **kwargs: _ParamsP.kwargs) -> type[_DatasetT]:
        if len(args) > 0:
            raise AttributeError(f'Positional arguments are not supported for '
                                 f'{params_cls.__module__}.{params_cls.__name__}')
        new_model_cls: type[_ModelT] = cast(
            type[_ModelT],
            model_cls.adjust(model_name, **kwargs),  # type: ignore[attr-defined]
        )

        new_dataset_cls = clone_dataset_func(dataset_name, new_model_cls)
        new_model_cls.Params = params_cls.copy_and_adjust(  # type: ignore[attr-defined]
            'Params',
            **kwargs,
        )
        return new_dataset_cls

    return _func


@dataclass_transform(kw_only_default=True)
def params_dataclass(cls: type[_ParamsT]) -> type[_ParamsT]:
    def wrap(cls):
        return dataclass(cls, kw_only=True)

    return wrap(cls)
