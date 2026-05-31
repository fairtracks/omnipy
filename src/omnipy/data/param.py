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
        """Initialize a params class and validate all declared default values.

        Args:
            name: Name of the params class being created.
            bases: Base classes used for the params class.
            namespace: Class namespace dictionary with declared attributes.

        Returns:
            None.

        Raises:
            ValueError: If a field uses ``default_factory`` or is missing a required default.
            pyd.ValidationError: If one or more declared default values fail model validation.

        Example:
            >>> class MyParams(ParamsBase):
            ...     limit: int = 5
            >>> MyParams.limit
            5
        """
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
        """Read a parameter value from the class-level field defaults.

        Args:
            attr: Name of the parameter field to read.

        Returns:
            The validated default value for the requested parameter field.

        Raises:
            AttributeError: If ``attr`` is not a defined params field.

        Example:
            >>> class MyParams(ParamsBase):
            ...     retries: int = 3
            >>> MyParams.retries
            3
        """
        model_cls = cast(type[pyd.BaseModel], cls)
        if attr in model_cls.__fields__:
            return cls._get_param_value(attr, model_cls)
        raise AttributeError(f'{model_cls.__name__}.{attr} is not defined')

    @functools.cache
    def _get_param_value(cls, attr, model_cls):
        """Return the cached default value for a parameter field.

        Args:
            attr: Name of the parameter field.
            model_cls: Params model class that defines the field.

        Returns:
            The field default value, or a value produced by ``default_factory``.

        Raises:
            KeyError: If ``attr`` is not present in ``model_cls.__fields__``.

        Example:
            >>> class MyParams(ParamsBase):
            ...     threshold: float = 0.75
            >>> _ParamsMeta._get_param_value('threshold', MyParams)
            0.75
        """
        if model_cls.__fields__[attr].default_factory is not None:
            return model_cls.__fields__[attr].default_factory()
        else:
            return model_cls.__fields__[attr].default

    def __setattr__(cls, attr: str, value: object) -> None:
        """Prevent writes to declared parameter fields on the params class.

        Args:
            attr: Name of the attribute to set.
            value: Value requested for assignment.

        Returns:
            None.

        Raises:
            AttributeError: If ``attr`` targets a params field or unknown public attribute.

        Example:
            >>> class MyParams(ParamsBase):
            ...     retries: int = 3
            >>> MyParams.retries = 5
            Traceback (most recent call last):
            ...
            AttributeError: MyParams.retries is read-only
        """
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
        """Pydantic model configuration: allows arbitrary types and enables smart union matching."""
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
        """Create an adjusted clone of the model class.

        Args:
            model_name: Name for the cloned model class.
            *args: Positional arguments, which are not supported.
            **kwargs: Parameter overrides applied to the cloned ``Params`` class.

        Returns:
            A cloned model class with adjusted parameter defaults.

        Raises:
            AttributeError: If any positional argument is supplied.

        Example:
            >>> adjust_model = bind_adjust_model_func(clone_model_func, params_cls)
            >>> NewModel = adjust_model('NewModel', retries=2)
        """
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
        """Create an adjusted clone of the dataset class.

        Args:
            dataset_name: Name for the cloned dataset class.
            model_name: Name for the intermediate adjusted model class.
            *args: Positional arguments, which are not supported.
            **kwargs: Parameter overrides applied to model and params classes.

        Returns:
            A cloned dataset class bound to the adjusted model class.

        Raises:
            AttributeError: If any positional argument is supplied.

        Example:
            >>> adjust_dataset = bind_adjust_dataset_func(clone_dataset_func, model_cls, params_cls)
            >>> NewDataset = adjust_dataset('NewDataset', 'NewModel', retries=2)
        """
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
        """Wrap a class using ``dataclass(..., kw_only=True)``.

        Args:
            cls: Class to transform into a keyword-only dataclass.

        Returns:
            The dataclass-decorated class.

        Example:
            >>> @params_dataclass
            ... class P:
            ...     x: int = 1
            >>> P(x=2)
            P(x=2)
        """
        return dataclass(cls, kw_only=True)

    return wrap(cls)
