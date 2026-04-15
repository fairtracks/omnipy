from typing import Any

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.shared.typing import TYPE_CHECKING

from .models import PandasModel


class PandasDataset(Dataset[PandasModel]):
    ...


if TYPE_CHECKING:
    from omnipy.data._mimic_models import Model_list

    class ListOfPandasDatasetsWithSameNumberOfFiles(Model_list[PandasDataset]):
        ...

else:

    class ListOfPandasDatasetsWithSameNumberOfFiles(Model[list[PandasDataset]]):
        @classmethod
        def _parse_data(cls, data: list[PandasDataset]) -> Any:
            dataset_list = data
            assert len(dataset_list) >= 2
            assert all(len(dataset) for dataset in dataset_list)
