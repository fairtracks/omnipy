from copy import deepcopy
from typing import Any, Callable, cast, Concatenate, ParamSpec

from pydantic import BaseModel
from pydantic.main import create_model, ModelMetaclass, validate_model
from typing_extensions import TypeVar

ModelT = TypeVar('ModelT')
ParamsP = ParamSpec('ParamsP')


class ParamsMeta(ModelMetaclass):
    def __init__(cls, name: str, bases: tuple[type, ...], namespace: dict[str, object]) -> None:
        super().__init__(name, bases, namespace)

        model_cls = cast(type[BaseModel], cls)
        default_vals = {}
        for field in model_cls.__fields__.values():
            if field.default_factory is not None:
                raise ValueError(f"Default factory is not supported for Params classes")

            default_vals[field.name] = field.get_default()
            if default_vals[field.name] is None and not field.allow_none:
                raise ValueError(f"{model_cls.__name__}.{field.name} must have a default value")

        values, fields_set, validation_error = \
            validate_model(model_cls, input_data={k: v for k, v in default_vals.items()})

        if validation_error:
            raise validation_error

        for key, value in values.items():
            model_cls.__fields__[key].default = value

    def __getattr__(cls, attr: str) -> object:
        model_cls = cast(type[BaseModel], cls)
        if attr in model_cls.__fields__:
            if model_cls.__fields__[attr].default_factory is not None:
                return model_cls.__fields__[attr].default_factory()  # type: ignore[misc]
            else:
                return model_cls.__fields__[attr].default
        raise AttributeError(f"{model_cls.__name__}.{attr} is not defined")

    def __setattr__(cls, attr: str, value: object) -> None:
        model_cls = cast(type[BaseModel], cls)
        if attr in model_cls.__fields__:
            raise AttributeError(f"{model_cls.__name__}.{attr} is read-only")
        elif not attr.startswith('_'):
            raise AttributeError(f"{model_cls.__name__}.{attr} is not defined")
        super().__setattr__(attr, value)


class ParamsBase(BaseModel, metaclass=ParamsMeta):
    class Config:
        arbitrary_types_allowed = True
        smart_union = True

    def __new__(cls, *args: object, **kwargs: object) -> None:  # type: ignore[misc]
        raise RuntimeError(f"{cls.__name__} cannot be instantiated")

    @classmethod
    def copy_and_adjust(cls, model_name: str, **kwargs: object) -> type['ParamsBase']:
        all_field_infos = {
            field_name: deepcopy(field.field_info) for field_name, field in cls.__fields__.items()
        }

        for key, value in kwargs.items():
            all_field_infos[key].default = value

        return create_model(  # type: ignore[call-overload]
            model_name,
            __base__=ParamsBase,
            **{
                field_name: (cls.__fields__[field_name].outer_type_, field_info) for field_name,
                field_info in all_field_infos.items()
            })


def bind_adjust_func(
    clone_model_func: Callable[..., type[ModelT]],
    params_cls: Callable[ParamsP, Any],
) -> Callable[Concatenate[str, ParamsP], type[ModelT]]:
    def _func(model_name: str, *args: ParamsP.args, **kwargs: ParamsP.kwargs) -> type[ModelT]:
        if len(args) > 0:
            raise AttributeError(f'Positional arguments are not supported for '
                                 f'{params_cls.__module__}.{params_cls.__name__}')
        new_model = clone_model_func(model_name)
        new_model.Params = params_cls.copy_and_adjust(  # type: ignore[attr-defined]
            'Params',
            **kwargs,
        )
        return new_model

    return _func
