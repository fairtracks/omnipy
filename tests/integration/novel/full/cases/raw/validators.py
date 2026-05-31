"""Validation helpers for integration novel full tests."""

from typing import Any

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model


def first_dataset_keys_in_all_datasets(*datasets: Dataset[Model[Any]]):
    """Return first dataset keys in all datasets."""
    assert all(all(key in dataset for dataset in datasets) for key in datasets[0])
