from omnipy.compute.task import TaskTemplate
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model

from .models import JsonDataset


@TaskTemplate()
def convert_dataset_string_to_json(dataset: Dataset[Model[str]]) -> JsonDataset:
    json_dataset = JsonDataset()
    json_dataset.from_json(dataset.to_data())
    return json_dataset
