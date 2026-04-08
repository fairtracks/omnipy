# flake8: noqa

from pydantic.v1 import (BaseConfig,
                         BaseModel,
                         ConfigDict,
                         ConfigError,
                         conint,
                         constr,
                         create_model,
                         EmailStr,
                         Extra,
                         Field,
                         NoneIsNotAllowedError,
                         NonNegativeFloat,
                         NonNegativeInt,
                         PositiveInt,
                         PrivateAttr,
                         Protocol,
                         root_validator,
                         StrictBytes,
                         StrictInt,
                         StrictStr,
                         validate_arguments,
                         ValidationError,
                         validator)
from pydantic.v1.dataclasses import dataclass
from pydantic.v1.error_wrappers import ErrorWrapper
from pydantic.v1.fields import ModelField, Undefined, UndefinedType
from pydantic.v1.generics import GenericModel
from pydantic.v1.main import ModelMetaclass, validate_model
from pydantic.v1.schema import normalize_name
from pydantic.v1.typing import display_as_type, is_none_type
from pydantic.v1.utils import lenient_isinstance, lenient_issubclass, sequence_like
from pydantic_core import Url


def pydantic_v1_hack():
    """
    Pydantic v1 needed to redefine typing.get_origin and typing.get_args
    for earlier Python versions not supported by Omnipy. This cause issues
    for Omnipy models like: `Model[type | typing.GenericAlias](list[int])`

    TODO: Remove pydantic_v1_hack for Pydantic v2
    """
    import typing

    import pydantic.v1.fields
    import pydantic.v1.generics
    import pydantic.v1.typing

    pydantic.v1.fields.get_origin = typing.get_origin  # pyright: ignore
    pydantic.v1.generics.get_args = typing.get_args  # pyright: ignore
    pydantic.v1.typing.get_args = typing.get_args  # pyright: ignore


pydantic_v1_hack()