# flake8: noqa

from collections import deque
from dataclasses import dataclass as std_dataclass
from enum import Enum
from types import GeneratorType, NoneType
from abc import ABCMeta
import re
from typing import TYPE_CHECKING, Any, Generic, Literal, TypeVar, get_args, get_origin

import pydantic
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined as Undefined
from pydantic_core import PydanticUndefinedType as UndefinedType
from pydantic_core import Url

pyd = pydantic

BaseConfig = pyd.BaseConfig
BaseModel = pyd.BaseModel
RootModel = pyd.RootModel
RootModelMetaclass = type(RootModel)
ConfigDict = pyd.ConfigDict
conint = pyd.conint
constr = pyd.constr
create_model = pyd.create_model
EmailStr = pyd.EmailStr
Extra = pyd.Extra
Field = pyd.Field
NonNegativeFloat = pyd.NonNegativeFloat
NonNegativeInt = pyd.NonNegativeInt
PositiveInt = pyd.PositiveInt
PrivateAttr = pyd.PrivateAttr
StrictBytes = pyd.StrictBytes
StrictInt = pyd.StrictInt
StrictStr = pyd.StrictStr
dataclass = pyd.dataclasses.dataclass
field_validator = pyd.field_validator
model_validator = pyd.model_validator
validate_call = pyd.validate_call
ValidationError = pyd.ValidationError


class Protocol(str, Enum):
    json = 'json'
    pickle = 'pickle'


def root_validator(*args, **kwargs):
    # v2's deprecated root_validator ignores kwargs on bare decorator (@root_validator),
    # so we must call with explicit kwargs first, then apply to function.
    if 'skip_on_failure' not in kwargs and not kwargs.get('pre', False):
        kwargs['skip_on_failure'] = True
    if args:
        return pyd.root_validator(**kwargs)(args[0])
    return pyd.root_validator(**kwargs)


def validator(*args, **kwargs):
    return pyd.validator(*args, **kwargs)


def validate_arguments(func=None, *, config=None):
    return pyd.validate_call(func, config=config)


@std_dataclass(frozen=True)
class ErrorWrapper:
    exc: BaseException
    loc: str | int | tuple[str | int, ...]


class ConfigError(RuntimeError):
    pass


class NoneIsNotAllowedError(TypeError):
    msg_template = 'none is not an allowed value'


# v2 no longer exposes a v1-style ModelField runtime object.
# Keep this alias for typing/backward imports; callers needing v1-only attributes
# must use compatibility paths.
ModelField = FieldInfo
_RootT = TypeVar('_RootT')
_BaseModelMetaclass = type(BaseModel)


class _GenericModelCompatMeta(_BaseModelMetaclass):
    def __new__(mcls, name, bases, namespace, **kwargs):
        namespace_dict = dict(namespace)
        annotations = dict(namespace_dict.get('__annotations__', {}))

        has_root_alias = '__root__' in annotations or '__root__' in namespace_dict
        if '__root__' in annotations:
            annotations['root'] = annotations.pop('__root__')
            namespace_dict['__annotations__'] = annotations
        if '__root__' in namespace_dict:
            namespace_dict['root'] = namespace_dict.pop('__root__')

        # Suppress pydantic v2's strict "All parameters must be present on typing.Generic"
        # error. This fires when a parent (e.g. Model[_V | _U]) has TypeVars that aren't
        # all re-declared on the current class's Generic[...]. Python replaces parametrized
        # Generic bases with the raw Generic class in __bases__, so we extract the actual
        # TypeVars from __orig_bases__ in the namespace.
        if '__pydantic_generic_metadata__' not in kwargs:
            # Compute parent parameters from the closest base that has generic metadata
            parent_params = ()
            for base in bases:
                base_meta = getattr(base, '__pydantic_generic_metadata__', None)
                if base_meta:
                    parent_params = base_meta.get('parameters', ())
                    break

            if parent_params:
                # Extract the class's own TypeVars from __orig_bases__.
                # Python puts __orig_bases__ in the namespace only when the class uses
                # parametrized Generic/other special forms in its bases.
                own_params: set[object] = set()
                if '__orig_bases__' in namespace_dict:
                    from typing import _GenericAlias as _TyGenericAlias
                    for ob in namespace_dict['__orig_bases__']:
                        if isinstance(ob, _TyGenericAlias):
                            ob_params = getattr(ob, '__parameters__', ())
                            own_params.update(ob_params)

                if own_params and parent_params and not all(
                    p in own_params for p in parent_params
                ):
                    kwargs['__pydantic_generic_metadata__'] = {
                        'origin': None, 'args': (), 'parameters': tuple(own_params)
                    }

        cls = super().__new__(mcls, name, bases, namespace_dict, **kwargs)

        if has_root_alias and '__root__' not in cls.__dict__:

            def _get(self):
                return self.root

            def _set(self, value):
                self.root = value

            cls.__root__ = property(_get, _set)

        return cls


class GenericModel(BaseModel, metaclass=_GenericModelCompatMeta):
    model_config = pyd.ConfigDict(arbitrary_types_allowed=True)


ModelMetaclass = _GenericModelCompatMeta


def validate_model(
    model: type[BaseModel],
    input_data: dict[str, Any],
    cls: type[Any] | None = None,
) -> tuple[dict[str, Any], set[str], ValidationError | None]:
    del cls

    try:
        validation_input = _to_v2_validation_input(model=model, input_data=input_data)
        validated_obj = model.model_validate(validation_input)
    except ValidationError as exc:
        values = _as_v1_style_input_values(model=model, input_data=input_data)
        fields_set = _as_v1_style_input_fields_set(model=model, input_data=input_data)
        return values, fields_set, exc

    values = _as_v1_style_values(model=model, validated_obj=validated_obj)
    fields_set = _as_v1_style_fields_set(model=model, validated_obj=validated_obj)
    return values, fields_set, None


def validation_error_from_wrappers(
    errors: list[ErrorWrapper],
    model: type[BaseModel] | str,
) -> ValidationError:
    title = model if isinstance(model, str) else model.__name__
    line_errors: list[dict[str, Any]] = []

    for wrapper in errors:
        loc = wrapper.loc if isinstance(wrapper.loc, tuple) else (wrapper.loc,)
        line_errors.extend(_exception_to_line_errors(exc=wrapper.exc, loc_prefix=loc))

    return ValidationError.from_exception_data(title, line_errors)


def normalize_name(name: str) -> str:
    return re.sub(r'[^a-zA-Z0-9.\-_]', '_', name)


def display_as_type(type_: Any) -> str:
    return str(type_)


def is_none_type(type_: Any) -> bool:
    if type_ in (None, NoneType, type(None)):
        return True

    if get_origin(type_) is Literal:
        literal_args = get_args(type_)
        return len(literal_args) == 1 and literal_args[0] is None

    return False


def lenient_isinstance(o: Any, class_or_tuple: Any) -> bool:
    try:
        return isinstance(o, class_or_tuple)
    except TypeError:
        return False


def lenient_issubclass(cls: Any, class_or_tuple: Any) -> bool:
    try:
        return isinstance(cls, type) and issubclass(cls, class_or_tuple)
    except TypeError:
        return False


def sequence_like(v: Any) -> bool:
    return isinstance(v, (list, tuple, set, frozenset, GeneratorType, deque))


def _is_root_model_cls(model: type[BaseModel]) -> bool:
    return bool(getattr(model, '__pydantic_root_model__', False))


def _as_v1_style_input_values(model: type[BaseModel], input_data: dict[str, Any]) -> dict[str, Any]:
    if _is_root_model_cls(model):
        if 'root' in input_data:
            return {'__root__': input_data['root']}
        if '__root__' in input_data:
            return {'__root__': input_data['__root__']}
    return dict(input_data)


def _as_v1_style_input_fields_set(model: type[BaseModel], input_data: dict[str, Any]) -> set[str]:
    if _is_root_model_cls(model):
        if '__root__' in input_data or 'root' in input_data:
            return {'__root__'}
        return set()
    return set(input_data.keys())


def _as_v1_style_values(model: type[BaseModel], validated_obj: BaseModel) -> dict[str, Any]:
    if _is_root_model_cls(model):
        return {'__root__': validated_obj.root}
    return validated_obj.model_dump()


def _to_v2_validation_input(model: type[BaseModel], input_data: dict[str, Any]) -> Any:
    if _is_root_model_cls(model):
        if '__root__' in input_data:
            return input_data['__root__']
        if 'root' in input_data:
            return input_data['root']
    return input_data


def _as_v1_style_fields_set(model: type[BaseModel], validated_obj: BaseModel) -> set[str]:
    fields_set = set(getattr(validated_obj, '__pydantic_fields_set__', set()))
    if _is_root_model_cls(model):
        if 'root' in fields_set:
            fields_set.remove('root')
            fields_set.add('__root__')
    return fields_set


def _exception_to_line_errors(
    exc: BaseException,
    loc_prefix: tuple[str | int, ...],
) -> list[dict[str, Any]]:
    if isinstance(exc, ValidationError):
        nested_errors: list[dict[str, Any]] = []
        for error in exc.errors(include_url=False):
            nested_error = dict(error)
            nested_error['loc'] = loc_prefix + tuple(error.get('loc', ()))
            nested_errors.append(nested_error)
        return nested_errors

    if isinstance(exc, NoneIsNotAllowedError):
        return [{
            'type': 'none_required',
            'loc': loc_prefix,
            'msg': str(exc) or '[Omnipy] none is not an allowed value',
            'input': None,
        }]

    error = exc if isinstance(exc, ValueError) else ValueError(str(exc))
    return [{
        'type': 'value_error',
        'loc': loc_prefix,
        'msg': f'Value error, {error}',
        'input': None,
        'ctx': {
            'error': error,
        },
    }]

__all__ = [
    'BaseConfig',
    'BaseModel',
    'RootModel',
    'RootModelMetaclass',
    'ConfigDict',
    'ConfigError',
    'conint',
    'constr',
    'create_model',
    'EmailStr',
    'Extra',
    'Field',
    'NoneIsNotAllowedError',
    'NonNegativeFloat',
    'NonNegativeInt',
    'PositiveInt',
    'PrivateAttr',
    'Protocol',
    'root_validator',
    'field_validator',
    'model_validator',
    'StrictBytes',
    'StrictInt',
    'StrictStr',
    'validate_arguments',
    'validate_call',
    'ValidationError',
    'validator',
    'dataclass',
    'ErrorWrapper',
    'validation_error_from_wrappers',
    'ModelField',
    'Undefined',
    'UndefinedType',
    'GenericModel',
    'ModelMetaclass',
    'validate_model',
    'normalize_name',
    'display_as_type',
    'is_none_type',
    'lenient_isinstance',
    'lenient_issubclass',
    'sequence_like',
    'Url',
]
