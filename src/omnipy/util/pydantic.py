from pydantic import BaseModel, create_model
from pydantic.class_validators import root_validator, validator
from pydantic.config import BaseConfig, ConfigDict, Extra
from pydantic.dataclasses import dataclass
from pydantic.decorator import validate_arguments
from pydantic.error_wrappers import ErrorWrapper, ValidationError
from pydantic.errors import ConfigError, NoneIsNotAllowedError
from pydantic.fields import Field, ModelField, PrivateAttr, Undefined, UndefinedType
from pydantic.generics import GenericModel
from pydantic.main import ModelMetaclass, validate_model
from pydantic.networks import EmailStr
from pydantic.parse import Protocol
from pydantic.types import (conint,
                            constr,
                            NonNegativeFloat,
                            NonNegativeInt,
                            PositiveInt,
                            StrictBytes,
                            StrictInt,
                            StrictStr)
from pydantic.typing import display_as_type, is_none_type
from pydantic.utils import lenient_isinstance, lenient_issubclass, sequence_like
from pydantic_core import Url


def pydantic_v1_hack():
    """
    Pydantic v1 needed to redefine typing.get_origin and typing.get_args
    for earlier Python versions not supported by Omnipy. This cause issues
    for Omnipy models like: `Model[type | typing.GenericAlias](list[int])`

    TODO: Remove pydantic_v1_hack for Pydantic v2
    """
    import typing

    import pydantic.fields
    import pydantic.generics
    import pydantic.typing

    pydantic.fields.get_origin = typing.get_origin  # pyright: ignore
    pydantic.generics.get_args = typing.get_args  # pyright: ignore
    pydantic.typing.get_args = typing.get_args  # pyright: ignore


pydantic_v1_hack()

__all__ = [
    'BaseConfig',
    'BaseModel',
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
    'StrictBytes',
    'StrictInt',
    'StrictStr',
    'validate_arguments',
    'ValidationError',
    'validator',
    'dataclass',
    'ErrorWrapper',
    'ModelField',
    'Undefined',
    'UndefinedType',
    'GenericModel',
    'ModelMetaclass',
    'validate_model',
    'display_as_type',
    'is_none_type',
    'lenient_isinstance',
    'lenient_issubclass',
    'sequence_like',
    'Url',
]
