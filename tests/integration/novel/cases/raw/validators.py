from typing import Any

from unifair.data.dataset import Dataset
from unifair.data.model import Model


def first_dataset_keys_in_all_datasets(*datasets: Dataset[Model[Any]]):
    assert all(all(key in dataset for dataset in datasets) for key in datasets[0])
