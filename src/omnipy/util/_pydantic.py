# flake8: noqa

from pydantic import (BaseConfig,
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
from pydantic.dataclasses import dataclass
from pydantic.error_wrappers import ErrorWrapper
from pydantic.fields import ModelField, Undefined, UndefinedType
from pydantic.generics import GenericModel
from pydantic.main import ModelMetaclass, validate_model
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