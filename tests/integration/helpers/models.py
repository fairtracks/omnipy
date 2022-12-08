from typing import Dict, Generic, List, Tuple, Type, TypeAlias, TypeVar, Union

from pydantic import BaseConfig, create_model, Extra
import pytest

from unifair.data.model import Model

RecordSchema = Model[Dict[str, Type]]


class RecordSchemaFactory(Model[Tuple[str, RecordSchema]]):
    @classmethod
    def _parse_data(cls, data: Tuple[str, RecordSchema]) -> Type[Model[RecordSchema]]:
        name, contents = data

        class Config(BaseConfig):
            extra = Extra.forbid

        return Model[create_model(
            name,
            **dict(((key, (val, val())) for key, val in contents.contents.items())),
            __config__=Config)]


RecordT = TypeVar('RecordT', bound=Dict)  # noqa


class TableTemplate(Model[List[RecordT]], Generic[RecordT]):
    """This is a generic template model for tables"""


class GeneralRecord(Model[Dict[str, Union[int, str]]]):
    """This is a general record"""


class GeneralTable(TableTemplate[GeneralRecord]):
    """This is a general table"""


MyRecordSchema = RecordSchemaFactory(('MyRecordSchema', {'a': int, 'b': str})).contents

MyOtherRecordSchema = RecordSchemaFactory(('MyOtherRecordSchema', {'b': str, 'c': int})).contents
