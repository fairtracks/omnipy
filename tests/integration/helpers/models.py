from typing import Dict, Generic, List, Tuple, Type, TypeVar, Union

from pydantic import BaseConfig, create_model, Extra
import pytest

from unifair.data.model import Model


@pytest.fixture
def RecordSchema():  # noqa
    return Dict[str, Type]


@pytest.fixture
def RecordSchemaFactory(RecordSchema):  # noqa
    class RecordSchemaFactory(Model[Tuple[str, RecordSchema]]):
        @classmethod
        def _parse_data(cls, data: Tuple[str, RecordSchema]) -> Type[Model[RecordSchema]]:
            name, contents = data

            class Config(BaseConfig):
                extra = Extra.forbid

            return Model[create_model(
                name,
                **dict(((key, (val, val())) for key, val in contents.items())),
                __config__=Config)]

    return RecordSchemaFactory


@pytest.fixture
def TableTemplate():  # noqa
    RecordT = TypeVar('RecordT', bound=Dict)  # noqa

    class TableTemplate(Model[List[RecordT]], Generic[RecordT]):
        """This is a generic template model for tables"""

    return TableTemplate


@pytest.fixture
def GeneralTable(TableTemplate):  # noqa
    class GeneralRecord(Model[Dict[str, Union[int, str]]]):
        """This is a general record"""

    class GeneralTable(TableTemplate[GeneralRecord]):
        """This is a general table"""

    return GeneralTable


@pytest.fixture
def MyRecordSchema(RecordSchemaFactory):  # noqa
    return RecordSchemaFactory(('MyRecordSchema', {'a': int, 'b': str})).contents


@pytest.fixture
def MyOtherRecordSchema(RecordSchemaFactory):  # noqa
    return RecordSchemaFactory(('MyOtherRecordSchema', {'b': str, 'c': int})).contents
