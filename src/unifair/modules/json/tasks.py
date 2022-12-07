import os

from unifair.compute.task import TaskTemplate
from unifair.data.dataset import Dataset
from unifair.data.model import Model

from .models import JsonDataset


@TaskTemplate
def import_directory(directory: str) -> JsonDataset:
    raw_dataset = Dataset[Model[str]]()
    for import_filename in os.listdir(directory):
        print(import_filename)
        if import_filename.endswith('.json'):
            with open(os.path.join(directory, import_filename)) as open_file:
                dataset_name = import_filename.split('.')[0]
                print(dataset_name)
                raw_dataset[dataset_name] = open_file.read()

    dataset = JsonDataset()
    dataset.from_json(raw_dataset.to_data())
    return dataset
