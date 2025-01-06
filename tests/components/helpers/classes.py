from typing import NamedTuple, Type

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.util.helpers import IsDataclass

ERROR_PREFIX = 'err_'


class CaseInfo(NamedTuple):
    name: str
    prefix2model_classes: dict[str, tuple[Type[Model], ...]]
    prefix2dataset_classes: dict[str, tuple[Type[Dataset], ...]]
    data_points: IsDataclass

    @staticmethod
    def data_point_should_fail(name: str) -> bool:
        return name.startswith(ERROR_PREFIX)

    @staticmethod
    def _remove_error_prefix(name: str) -> str:
        if name.startswith(ERROR_PREFIX):
            name = name[len(ERROR_PREFIX):]
        return name

    def model_classes_for_data_point(self, name: str) -> tuple[Type[Model], ...]:
        name = self._remove_error_prefix(name)
        for prefix, model_classes in self.prefix2model_classes.items():
            if name.startswith(prefix):
                return model_classes
        raise KeyError(f'{name} does not match any registered prefix for this test')

    def dataset_classes_for_data_point(self, name: str) -> tuple[Type[Dataset], ...]:
        name = self._remove_error_prefix(name)
        for prefix, dataset_classes in self.prefix2dataset_classes.items():
            if name.startswith(prefix):
                return dataset_classes
        raise KeyError(f'{name} does not match any registered prefix for this test')
