"""Helper classes shared by component test cases."""

from typing import NamedTuple, Type

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.util.helpers import IsDataclass

ERROR_PREFIX = 'err_'


class CaseInfo(NamedTuple):
    """Describe reusable model and dataset case data."""

    name: str
    prefix2model_classes: dict[str, tuple[Type[Model], ...]]
    prefix2dataset_classes: dict[str, tuple[Type[Dataset], ...]]
    data_points: IsDataclass

    @staticmethod
    def data_point_should_fail(name: str) -> bool:
        """Return whether a named data point represents a failure case."""
        return name.startswith(ERROR_PREFIX)

    @staticmethod
    def _remove_error_prefix(name: str) -> str:
        """Strip the failure prefix from a data point name."""
        if name.startswith(ERROR_PREFIX):
            name = name[len(ERROR_PREFIX):]
        return name

    def model_classes_for_data_point(self, name: str) -> tuple[Type[Model], ...]:
        """Return model classes registered for a data point name."""
        name = self._remove_error_prefix(name)
        for prefix, model_classes in self.prefix2model_classes.items():
            if name.startswith(prefix):
                return model_classes
        raise KeyError(f'{name} does not match any registered prefix for this test')

    def dataset_classes_for_data_point(self, name: str) -> tuple[Type[Dataset], ...]:
        """Return dataset classes registered for a data point name."""
        name = self._remove_error_prefix(name)
        for prefix, dataset_classes in self.prefix2dataset_classes.items():
            if name.startswith(prefix):
                return dataset_classes
        raise KeyError(f'{name} does not match any registered prefix for this test')
