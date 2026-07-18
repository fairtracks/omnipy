"""Datasets that map file names to pandas-backed table models."""

from typing import Any

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.shared.typing import TYPE_CHECKING

from .models import PandasModel


class PandasDataset(Dataset[PandasModel]):
    """Store named pandas-backed tables as ``PandasModel`` data files.

    This dataset maps each data file name to a table represented by
    :class:`~omnipy.components.pandas.models.PandasModel`.

    Examples:
        >>> dataset = PandasDataset({'table': [{'id': 1, 'value': 'a'}]})
        >>> tuple(dataset.keys())
        ('table',)
    """

    ...


if TYPE_CHECKING:
    from omnipy.data._typing.mimic_models import Model_list

    class ListOfPandasDatasetsWithSameNumberOfFiles(Model_list[PandasDataset]):
        """Represent a list of aligned ``PandasDataset`` instances.

        The list is expected to contain at least two datasets and each dataset
        must contain one or more files.
        """

        ...

else:

    class ListOfPandasDatasetsWithSameNumberOfFiles(Model[list[PandasDataset]]):
        """Validate a list of aligned ``PandasDataset`` instances.

        The list is expected to contain at least two datasets and each dataset
        must contain one or more files.
        """
        @classmethod
        def _parse_data(cls, data: list[PandasDataset]) -> Any:
            dataset_list = data
            assert len(dataset_list) >= 2
            assert all(len(dataset) for dataset in dataset_list)
