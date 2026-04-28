# flake8: noqa

from typing import TYPE_CHECKING

import pydantic
from pydantic_core import Url

PYDANTIC_V2 = pydantic.__version__.startswith('2')

if TYPE_CHECKING or PYDANTIC_V2:
    import pydantic.v1
    pyd = pydantic.v1

    import pydantic.v1.error_wrappers as pyd_error_wrappers
    import pydantic.v1.errors as pyd_errors
    import pydantic.v1.fields as pyd_fields
    import pydantic.v1.generics as pyd_generics
    import pydantic.v1.main as pyd_main
    import pydantic.v1.schema as pyd_schema
    import pydantic.v1.typing as pyd_typing
    import pydantic.v1.utils as pyd_utils
else:
    pyd = pydantic

    import pydantic.error_wrappers as pyd_error_wrappers
    import pydantic.errors as pyd_errors
    import pydantic.fields as pyd_fields
    import pydantic.generics as pyd_generics
    import pydantic.main as pyd_main
    import pydantic.schema as pyd_schema
    import pydantic.typing as pyd_typing
    import pydantic.utils as pyd_utils

BaseConfig = pyd.BaseConfig
BaseModel = pyd.BaseModel
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
Protocol = pyd.Protocol
root_validator = pyd.root_validator
StrictBytes = pyd.StrictBytes
StrictInt = pyd.StrictInt
StrictStr = pyd.StrictStr
validate_arguments = pyd.validate_arguments
ValidationError = pyd.ValidationError
validator = pyd.validator
dataclass = pyd.dataclasses.dataclass
ErrorWrapper = pyd_error_wrappers.ErrorWrapper
ConfigError = pyd_errors.ConfigError
NoneIsNotAllowedError = pyd_errors.NoneIsNotAllowedError
ModelField = pyd_fields.ModelField
Undefined = pyd_fields.Undefined
UndefinedType = pyd_fields.UndefinedType
GenericModel = pyd_generics.GenericModel
ModelMetaclass = pyd_main.ModelMetaclass
validate_model = pyd_main.validate_model
normalize_name = pyd_schema.normalize_name
display_as_type = pyd_typing.display_as_type
is_none_type = pyd_typing.is_none_type
lenient_isinstance = pyd_utils.lenient_isinstance
lenient_issubclass = pyd_utils.lenient_issubclass
sequence_like = pyd_utils.sequence_like


def pydantic_v1_hack():
    """
    Pydantic v1 needed to redefine typing.get_origin and typing.get_args
    for earlier Python versions not supported by Omnipy. This cause issues
    for Omnipy models like: `Model[type | typing.GenericAlias](list[int])`

    TODO: Remove pydantic_v1_hack for Pydantic v2
    """

    import typing

    if TYPE_CHECKING or PYDANTIC_V2:

        import pydantic.v1.fields
        import pydantic.v1.generics
        import pydantic.v1.typing

        pydantic.v1.fields.get_origin = typing.get_origin  # pyright: ignore
        pydantic.v1.generics.get_args = typing.get_args  # pyright: ignore
        pydantic.v1.typing.get_args = typing.get_args  # pyright: ignore
    else:
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
    'normalize_name',
    'display_as_type',
    'is_none_type',
    'lenient_isinstance',
    'lenient_issubclass',
    'sequence_like',
    'Url',
]
