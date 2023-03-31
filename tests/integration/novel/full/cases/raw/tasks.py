from omnipy.compute.task import TaskTemplate
from omnipy.data.dataset import Dataset, MultiModelDataset

from ...helpers.models import GeneralTable, record_schema_factory, RecordSchemaDef, TableTemplate


@TaskTemplate()
def uppercase(text: str) -> str:
    return text.upper()


@TaskTemplate()
def square_root(number: int) -> dict[str, float]:
    return {'neg_root': -number**0.5, 'pos_root': number**0.5}


@TaskTemplate()
def merge_key_value_into_str(key: object, val: object) -> str:
    return '{}: {}'.format(key, val)


# TODO: Implement explicit serializer support (if needed)


@TaskTemplate()
def extract_record_schema_def(table: GeneralTable) -> RecordSchemaDef:
    record_model = {}
    for record in table.to_data():
        for field_key, field_val in record.items():
            if field_key not in record_model:
                record_model[field_key] = type(field_val)
            else:
                assert record_model[field_key] == type(field_val)

    return RecordSchemaDef(record_model)


# TODO: Implement support for extra validators
# @TaskTemplate(extra_validators=(first_dataset_keys_in_all_datasets,))
@TaskTemplate()
def apply_models_to_dataset(
        dataset: Dataset[GeneralTable],
        record_schema_defs: Dataset[RecordSchemaDef]) -> MultiModelDataset[GeneralTable]:
    multi_model_dataset = dataset.as_multi_model_dataset()
    for data_file in multi_model_dataset.keys():
        multi_model_dataset.set_model(
            data_file,
            TableTemplate[record_schema_factory(
                data_file,
                record_schema_defs[data_file],
            )])
    return multi_model_dataset
