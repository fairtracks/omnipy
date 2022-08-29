from typing import Any, Dict, Generic, List, Tuple, Type, TypeVar, Union

from pydantic import (BaseModel,
                      create_model,
                      Extra,
                      root_validator,
                      ValidationError,
                      validator)
import pytest

from unifair.compute.flow import FlowTemplate
from unifair.config.runtime import RuntimeConfig
from unifair.dataset.dataset import Dataset, MultiModelDataset
from unifair.dataset.model import Model
from unifair.dataset.serializer import CsvSerializer, PythonSerializer
from unifair.engine.local import LocalRunner


@pytest.fixture
def RecordSchemaFactory():  # noqa
    class RecordSchemaFactory(Model[Tuple[str, Dict[str, Type]]]):
        @classmethod
        def _parse_data(cls, data: Tuple[str, Dict[str, Type]]) -> Type[Model]:
            name, contents = data

            class Config:
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


def test_table_models(GeneralTable, TableTemplate, MyRecordSchema, MyOtherRecordSchema):  # noqa
    _a = GeneralTable([{'a': 123, 'b': 'ads'}, {'a': 234, 'b': 'acs'}])
    _b = TableTemplate[MyRecordSchema]([{'a': 123, 'b': 'ads'}, {'a': 234, 'b': 'acs'}])

    with pytest.raises(ValidationError):
        _c = TableTemplate[MyOtherRecordSchema]([{'a': 123, 'b': 'ads'}, {'a': 234, 'b': 'acs'}])

    # print(_a.to_json_schema(pretty=True))
    # print(_b.to_json_schema(pretty=True))


def test_dataset_with_multiple_table_models(
        GeneralTable,  # noqa
        TableTemplate,  # noqa
        MyRecordSchema,  # noqa
        MyOtherRecordSchema):  # noqa
    my_dataset = MultiModelDataset[GeneralTable]()

    my_dataset['a'] = [{'a': 123, 'b': 'ads'}, {'a': 234, 'b': 'acs'}]
    assert my_dataset.get_model('a') == GeneralTable

    my_dataset.set_model('a', TableTemplate[MyRecordSchema])
    assert my_dataset.get_model('a') == TableTemplate[MyRecordSchema]

    my_dataset['b'] = [{'b': 'df', 'c': True}, {'b': 'sg', 'c': False}]
    with pytest.raises(ValidationError):
        my_dataset.set_model('b', TableTemplate[MyRecordSchema])
    assert my_dataset.get_model('b') == GeneralTable

    my_dataset.set_model('b', TableTemplate[MyOtherRecordSchema])
    assert my_dataset.get_model('b') == TableTemplate[MyOtherRecordSchema]

    my_dataset.set_model('c', TableTemplate[MyOtherRecordSchema])
    assert my_dataset.get_model('c') == TableTemplate[MyOtherRecordSchema]
    assert my_dataset['c'] == []

    with pytest.raises(ValidationError):
        my_dataset['c'] = [{'b': 'sd', 'd': False}, {'b': 'dd', 'd': False}]
    assert my_dataset['c'] == []
    my_dataset['c'] = [{'b': 'sd', 'c': False}, {'b': 'dd', 'c': False}]

    del my_dataset['b']
    assert my_dataset.get_model('b') == TableTemplate[MyOtherRecordSchema]

    with pytest.raises(ValidationError):
        my_dataset.from_data({'c': [{'b': 'rt', 'd': True}, {'b': 'vf', 'd': True}]}, update=False)
    my_dataset.from_data({'c': [{'b': 'rt', 'c': True}, {'b': 'vf', 'c': True}]}, update=False)
    assert my_dataset.get_model('a') == TableTemplate[MyRecordSchema]

    with pytest.raises(ValidationError):
        my_dataset.update({'a': [{'a': 444, 'd': True}]})
    my_dataset.update({'a': [{'a': 444, 'b': 'fae'}]})
    assert my_dataset.get_model('a') == TableTemplate[MyRecordSchema]
