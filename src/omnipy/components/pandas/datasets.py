from typing import Any

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model

from .models import PandasModel


class PandasDataset(Dataset[PandasModel]):
    ...


class ListOfPandasDatasetsWithSameNumberOfFiles(Model[list[PandasDataset]]):
    @classmethod
    def _parse_data(cls, data: list[PandasDataset]) -> Any:
        dataset_list = data
        assert len(dataset_list) >= 2
        assert all(len(dataset) for dataset in dataset_list)
