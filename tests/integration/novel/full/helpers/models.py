import typing
from typing import Generic, Mapping, Type, TypeVar

from omnipy.data.model import Model
import omnipy.util._pydantic as pyd

# Types


class RecordSchemaBase(pyd.BaseModel):
    class Config:
        extra = pyd.Extra.forbid


# TODO: Revisit RecordT typing with pydantic v2 and/or new versions of mypy and python
#
# A rundown of various typing-related issues with the RecordT TypeVar, for later reference.
# Hours were spend figuring this out. Let's start with the following TypeVar definition, which
# looks like it ought to be working:
#
#     RecordT = TypeVar('RecordT', bound=Model[dict[str, Type | UnionType] | RecordSchemaBase])
#
# There are, however, several issues with this that cause mypy to complain, however the exact
# reasons are difficult to unravel. Mypy only complains with a very generic error message:
#
#     Type argument "GeneralRecord" of "TableTemplate" must be a subtype of
#     "Model[Union[dict[str, Union[Type[Any], UnionType]], RecordSchemaBase]]"  [type-var] (95:25)
#
# The first reason for failure is that dict is invariant, while `GeneralRecord` is a specialization
# of the bound `RecordT` type variable and therefore needs it to be covariant or contravariant.
# Switching `dict` with `Mapping`, which is not invariant, still does not work:
#
#     RecordT = TypeVar('RecordT', bound=Model[Mapping[str, Type | UnionType] | RecordSchemaBase])
#
# Now the code fails not run at all with the error:
#
#     TypeError: 'member_descriptor' object is not iterable
#
# In addition, mypy still fails, unhelpfully with the exact same error message as above. It turns
# out the reason for both is that neither of Pydantic version 1.10.13 or mypy v1.7.0 supports
# `UnionType` introduced in Python 3.10, even when `GeneralRecord` is defined using new union
# notation (`int | str` instead of `Union[int, str]`). Both pydantic and mypy, however, works with
# `typing._UnionGenericAlias` independently of notation type even though (in Python 3.10):
#
#     ```python
#     isinstance(int | str,  _UnionGenericAlias) == False
#     isinstance(int | str, UnionType) == True
#     isinstance(Union[int, str],  _UnionGenericAlias) == False
#     isinstance(Union[int, str],  UnionType) == True
#     ```
#
# Due to this inconsistency and the use of a private type, `UnionType` was switched to `object`.
# With the final variant, all of mypy, pydantic and omnipy work as they should:

RecordT = TypeVar('RecordT', bound=Model[Mapping[str, Type | object] | RecordSchemaBase])

RecordSchemaDefType = dict[str, Type[object]]

# Models


class RecordSchemaDef(Model[RecordSchemaDefType]):
    ...


def record_schema_factory(data_file: str,
                          record_schema_def: RecordSchemaDefType) -> Type[RecordSchemaBase]:
    class Config(pyd.BaseConfig):
        extra = pyd.Extra.forbid

    # For real-world implementation config.dynamically_convert_elements_to_models must be forced
    # to False here.

    return pyd.create_model(
        data_file,
        __base__=RecordSchemaBase,
        **{
            key: (val, val()) for key, val in record_schema_def.items()
        },
    )


if typing.TYPE_CHECKING:
    # TODO: Revisit the need for static classes for mypy after updates to Pydantic v2
    #       as this is a workaround only for these hard-coded test cases

    class MyRecordSchemaBase(RecordSchemaBase):
        a: int
        b: str

    class MyRecordSchema(Model[MyRecordSchemaBase]):
        ...

    class MyOtherRecordSchemaBase(RecordSchemaBase):
        b: str
        c: int

    class MyOtherRecordSchemaModel(Model[MyOtherRecordSchemaBase]):
        ...
else:
    MyRecordSchemaBase = record_schema_factory('MyRecordSchemaBase', {'a': int, 'b': str})

    class MyRecordSchema(Model[MyRecordSchemaBase]):
        ...

    MyOtherRecordSchemaBase = record_schema_factory('MyOtherRecordSchemaBase', {'b': str, 'c': int})

    class MyOtherRecordSchema(Model[MyOtherRecordSchemaBase]):
        ...


class TableTemplate(Model[list[RecordT]], Generic[RecordT]):
    """This is a generic template model for tables"""


class GeneralRecord(Model[dict[str, int | str]]):
    """This is a general record"""


class GeneralTable(Model[TableTemplate[GeneralRecord]]):
    """This is a general table"""
