from typing import Any, Dict

from unifair.compute.task import TaskTemplate
from unifair.data.dataset import Dataset, MultiModelDataset

from ...helpers.models import GeneralTable, RecordSchema

# from .validators import first_dataset_keys_in_all_datasets


@TaskTemplate
def uppercase(text: str) -> str:
    return text.upper()


@TaskTemplate
def square_root(number: int) -> Dict[str, float]:
    return {'neg_root': -number**1 / 2, 'pos_root': number**1 / 2}


@TaskTemplate
def merge_key_value_into_str(key: Any, val: Any) -> str:
    return '{}: {}'.format(key, val)


# @TaskTemplate(serializer=PythonSerializer)
@TaskTemplate()
def extract_record_model(table: GeneralTable) -> RecordSchema:
    record_model = {}
    for record in table.to_data():
        for field_key, field_val in record.items():
            if field_key not in record_model:
                record_model[field_key] = type(field_val)
            else:
                assert record_model[field_key] == type(field_val)

    return record_model


# @TaskTemplate(serializer=CsvSerializer, extra_validators=(first_dataset_keys_in_all_datasets,))
@TaskTemplate
def apply_models_to_dataset(dataset: Dataset[GeneralTable],
                            models: Dataset[RecordSchema]) -> MultiModelDataset[GeneralTable]:
    multi_model_dataset = dataset.as_multi_model_dataset()
    for obj_type in multi_model_dataset.keys():
        multi_model_dataset.set_model(obj_type, models[obj_type])
    return multi_model_dataset
