from typing import Dict, List, Union

from unifair.data.dataset import Dataset
from unifair.data.model import Model


class JsonDatasetModel(Model[List[Dict[str, Union[int, float, List, Dict, str]]]]):
    ...

    @classmethod
    def _parse_data(cls, data: List) -> List:
        data = cls._data_not_empty_object(data)
        return data

    @classmethod
    def _data_not_empty_object(cls, data: List):
        for obj in data:
            assert len(obj) > 0
        return data


class JsonDataset(Dataset[JsonDatasetModel]):
    ...
