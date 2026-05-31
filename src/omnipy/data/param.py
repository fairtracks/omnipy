"""Parameter model helpers for configurable Omnipy model and dataset classes.

This module defines the read-only parameter class pattern used by Omnipy models
and datasets, plus helpers that clone classes with adjusted parameter defaults.
"""

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
    def __init__(cls, name: str, bases: tuple[type, ...], namespace: dict[str, object]) -> None:
        super().__init__(name, bases, namespace)

        model_cls = cast(type[pyd.BaseModel], cls)
        default_vals = {}
        for field in model_cls.__fields__.values():
            if field.default_factory is not None:
                raise ValueError('Default factory is not supported for Params classes')

            default_vals[field.name] = field.get_default()
            if default_vals[field.name] is None and not field.allow_none:
                raise ValueError(f'{model_cls.__name__}.{field.name} must have a default value')

        values, fields_set, validation_error = \
            pyd.validate_model(model_cls, input_data={k: v for k, v in default_vals.items()})

        if validation_error:
            raise validation_error

        for key, value in values.items():
            model_cls.__fields__[key].default = value

    def __getattr__(cls, attr: str) -> object:
        model_cls = cast(type[pyd.BaseModel], cls)
        if attr in model_cls.__fields__:
            return cls._get_param_value(attr, model_cls)
        raise AttributeError(f'{model_cls.__name__}.{attr} is not defined')

    @functools.cache
    def _get_param_value(cls, attr, model_cls):
        if model_cls.__fields__[attr].default_factory is not None:
            return model_cls.__fields__[attr].default_factory()
        else:
            return model_cls.__fields__[attr].default

    def __setattr__(cls, attr: str, value: object) -> None:
        model_cls = cast(type[pyd.BaseModel], cls)
        if attr in model_cls.__fields__:
            raise AttributeError(f'{model_cls.__name__}.{attr} is read-only')
        elif not attr.startswith('_'):
            raise AttributeError(f'{model_cls.__name__}.{attr} is not defined')
        super().__setattr__(attr, value)


class ParamsBase(pyd.BaseModel, metaclass=_ParamsMeta):
    """Read-only class-level parameter container for adjusted model variants.

    ``ParamsBase`` subclasses declare validated default values as pydantic
    fields, but they are used as class objects rather than instantiated data
    objects. Omnipy reads parameter values directly from the class and can clone
    the parameter class with selected defaults overridden.
    """

    class Config:
        arbitrary_types_allowed = True
        smart_union = True

    def __new__(cls, *args: object, **kwargs: object) -> None:  # type: ignore[misc]
        """Disallow instantiation of parameter classes.

        Args:
            *args: Ignored positional arguments.
            **kwargs: Ignored keyword arguments.

        Raises:
            RuntimeError: Always, because parameter classes are used only via
                class attributes.
        """
        raise RuntimeError(f'{cls.__name__} cannot be instantiated')

    @classmethod
    def copy_and_adjust(cls, model_name: str, **kwargs: object) -> type['ParamsBase']:
        """Clone the parameter class with updated default field values.

        Args:
            model_name: Name to assign to the cloned parameter class.
            **kwargs: Field defaults to override in the clone.

        Returns:
            A new :class:`ParamsBase` subclass with validated adjusted defaults.
        """
        all_field_infos = {
            field_name: deepcopy(field.field_info) for field_name, field in cls.__fields__.items()
        }

        for key, value in kwargs.items():
            all_field_infos[key].default = value

        field_definitions: dict[str, Any] = {
            field_name: (cls.__fields__[field_name].outer_type_, field_info)
            for field_name, field_info in all_field_infos.items()
        }
        return pyd.create_model(  # type: ignore[call-overload]
            model_name, __base__=ParamsBase, **field_definitions)


def bind_adjust_model_func(
    clone_model_func: Callable[..., type[_ModelT]],
    params_cls: Callable[_ParamsP, Any],
) -> Callable[Concatenate[str, _ParamsP], type[_ModelT]]:
    """Bind a model-cloning helper to a parameter class.

    The returned function creates a cloned model class, then replaces its
    ``Params`` class with a copy of ``params_cls`` whose defaults are adjusted
    from the supplied keyword arguments.

    Args:
        clone_model_func: Function that clones the target model class.
        params_cls: Parameter class whose defaults should be adjusted.

    Returns:
        A helper that accepts a new model name and keyword-only parameter
        overrides, then returns the adjusted model class.
    """
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
    """Bind a dataset-cloning helper to model and parameter classes.

    The returned function first creates an adjusted model class, then clones a
    dataset class bound to that model, while also attaching a cloned ``Params``
    class with the same adjusted defaults.

    Args:
        clone_dataset_func: Function that clones the dataset class.
        model_cls: Base model class to adjust before cloning the dataset.
        params_cls: Parameter class whose defaults should be adjusted.

    Returns:
        A helper that accepts dataset and model names plus keyword-only
        parameter overrides, then returns the adjusted dataset class.
    """
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
    """Decorate a params declaration as a keyword-only dataclass.

    Args:
        cls: Class to transform into a keyword-only dataclass.

    Returns:
        The same class wrapped by :func:`dataclasses.dataclass` with
        ``kw_only=True``.
    """
    def wrap(cls):
        return dataclass(cls, kw_only=True)

    return wrap(cls)
