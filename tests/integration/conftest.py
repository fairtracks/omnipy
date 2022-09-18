from typing import Any, Dict

import pytest

from unifair.config.runtime import Runtime
from unifair.data.dataset import Dataset, MultiModelDataset
from unifair.data.serializer import CsvSerializer, PythonSerializer
from unifair.engine.local import LocalRunner


@pytest.fixture
def runtime():
    return Runtime()


@pytest.fixture
def runtime_local_runner(runtime):
    runtime.engine = LocalRunner()
    return runtime


@pytest.fixture
def extract_record_model(runtime, RecordSchema, GeneralTable):  # noqa
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
        multi_model_dataset = dataset.as_multi_model_dataset()
        for obj_type in multi_model_dataset.keys():
            multi_model_dataset.set_model(obj_type, models[obj_type])
        return multi_model_dataset

    return apply_models_to_dataset


@pytest.fixture
def specialize_record_models_dag_flow(
        runtime,
        GeneralTable,  # noqa
        extract_record_model,
        apply_models_to_dataset):
    @runtime.dag_flow_template(
        extract_record_model.refine(
            param_key_map={'data', 'tables'},
            result_key='models',
            iterate_over_dataset=True,
        ),
        apply_models_to_dataset,
    )
    def specialize_record_models(
            tables: Dataset[GeneralTable]) -> MultiModelDataset[GeneralTable]:  # noqa
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


@pytest.fixture
def uppercase(runtime):
    @runtime.task_template()
    def uppercase(text: str) -> str:
        return text.upper()

    return uppercase


@pytest.fixture
def square_root(runtime):
    @runtime.task_template()
    def square_root(number: int) -> Dict[str, float]:
        return {'neg_root': -number**1 / 2, 'pos_root': number**1 / 2}

    return square_root


@pytest.fixture
def merge_key_value_into_str(runtime):
    @runtime.task_template()
    def merge_key_value_into_str(key: Any, val: Any) -> str:
        return '{}: {}'.format(key, val)

    return merge_key_value_into_str


@pytest.fixture
def pos_square_root_dag_flow(runtime, uppercase, square_root, merge_key_value_into_str):
    @runtime.dag_flow_template(
        uppercase.refine(result_key='upper'),
        square_root,
        merge_key_value_into_str.refine(
            param_key_map={
                'key': 'upper', 'val': 'pos_root'
            }, result_key='pos_square_root'))
    def pos_square_root(number: int, text: str) -> str:
        ...

    return pos_square_root


@pytest.fixture
def pos_square_root_func_flow(runtime, uppercase, square_root, merge_key_value_into_str):
    @runtime.func_flow_template(result_key='pos_square_root')
    def pos_square_root(number: int, text: str, result_key: str) -> Dict[str, int]:
        upper = uppercase(text)
        _neg_root, pos_root = square_root(number)
        return {result_key: merge_key_value_into_str(upper, pos_root)}

    return pos_square_root
