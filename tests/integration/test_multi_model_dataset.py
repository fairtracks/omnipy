from typing import Any, Dict, Generic, List, Tuple, Type, TypeVar, Union

from pydantic import (BaseModel, create_model, Extra, root_validator, ValidationError, validator)
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


@pytest.fixture
def runtime():
    return RuntimeConfig()


@pytest.fixture
def runtime_local_runner(runtime):
    runtime.engine = LocalRunner()
    return runtime


@pytest.fixture
def extract_record_model(runtime, RecordSchema, TableSchemaSerializer, GeneralTable):  # noqa
    @runtime.task_template(serializer=PythonSerializer)
    def extract_record_model(table: GeneralTable) -> RecordSchema:
        record_model = {}
        for record in table:
            for field_key, field_val in record.items():
                if field_key not in record_model:
                    record_model[field_key] = type(field_val)
                else:
                    assert record_model[field_key] == type(field_val)

        return record_model


@pytest.fixture
def apply_models_to_dataset(runtime, RecordSchema, GeneralTable, TableTemplate):  # noqa
    def first_dataset_keys_in_all_datasets(*datasets: Dataset[Any]):
        assert all(all(key in dataset for dataset in datasets) for key in datasets[0])

    @runtime.task_template(
        serializer=CsvSerializer, extra_validators=(first_dataset_keys_in_all_datasets,))
    def apply_models_to_dataset(dataset: Dataset[GeneralTable],
                                models: Dataset[RecordSchema]) -> MultiModelDataset[GeneralTable]:
        for obj_type in dataset:
            dataset.set_model(obj_type, models[obj_type])
        return dataset

    return apply_models_to_dataset


@pytest.fixture
def specialize_record_models_dag_flow(
        runtime,
        GeneralTable,  # noqa
        extract_record_model,
        apply_models_to_dataset):
    @runtime.dag_flow_template(
        extract_record_model.refine(
            param_key_map={'dataset', 'tables'},
            result_key='models',
            iterate_over_dataset=True,
        ),
        apply_models_to_dataset,
    )
    def specialize_record_models(tables: Dataset[GeneralTable]) -> MultiModelDataset[GeneralTable]:
        ...

    return specialize_record_models


@pytest.fixture
def specialize_record_models_func_flow(
        runtime,
        GeneralTable,  # noqa
        RecordSchema,  # noqa
        extract_record_model,
        apply_models_to_dataset):
    @runtime.func_flow_template()
    def specialize_record_models(tables: Dataset[GeneralTable]) -> MultiModelDataset[GeneralTable]:
        record_models = Dataset[RecordSchema]([
            (table_name, extract_record_model(table)) for table_name, table in tables
        ])
        return apply_models_to_dataset(tables, record_models)

    return specialize_record_models


def _common_test_run_dataset_flow(specialize_record_models: FlowTemplate,
                                  GeneralTable: Model):  # noqa
    f_specialize_record_models = specialize_record_models.apply()

    old_dataset = Dataset[GeneralTable]()
    old_dataset['a'] = [{'a': 123, 'b': 'ads'}, {'a': 234, 'b': 'acs'}]
    old_dataset['b'] = [{'b': 'df', 'c': True}, {'b': False, 'c': 'sg'}]  # inconsistent types

    with pytest.raises(AssertionError):
        _new_dataset = f_specialize_record_models(old_dataset)

    old_dataset['b'] = [{'b': 'df', 'c': True}, {'b': 'sg', 'c': False}]  # consistent types

    new_dataset = f_specialize_record_models(old_dataset)

    # general model allows the tables to be switched
    old_dataset['a'], old_dataset['b'] = old_dataset['b'], old_dataset['a']

    with pytest.raises(ValidationError):
        # per-table specialized models do not allow the tables to be switched
        new_dataset['a'], new_dataset['b'] = new_dataset['b'], new_dataset['a']


def test_run_dataset_dag_flow(runtime_local_runner, specialize_record_models_dag_flow,
                              GeneralTable):  # noqa
    _common_test_run_dataset_flow(specialize_record_models_dag_flow, GeneralTable)


def test_run_dataset_func_flow(runtime_local_runner,
                               specialize_record_models_func_flow,
                               GeneralTable):  # noqa
    _common_test_run_dataset_flow(specialize_record_models_func_flow, GeneralTable)
