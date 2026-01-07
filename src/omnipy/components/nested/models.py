from typing_extensions import TypeVar

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.shared.typing import TYPE_CHECKING

from ..general.models import Chain2

if TYPE_CHECKING:
    from .datasets import NestedDataset  # noqa: F401

DatasetT = TypeVar('DatasetT')


class EnumeratedListOfTuplesModel(Model[list[tuple[int, object]]]):
    @classmethod
    def _parse_data(cls, data: list[tuple[int, object]]) -> list[tuple[int, object]]:
        for expected_index, (actual_index, _) in enumerate(data):
            if expected_index != actual_index:
                raise ValueError(f'Indices are not sequential starting from 0: '
                                 f'expected {expected_index}, got {actual_index}')
        return data


class EnumeratedListModel(Model[EnumeratedListOfTuplesModel | list[object]
                                | list[dict[str, object]]]):
    @classmethod
    def _parse_data(
        cls, data: EnumeratedListOfTuplesModel | list[object] | list[dict[str, object]]
    ) -> EnumeratedListOfTuplesModel:
        if not isinstance(data, EnumeratedListOfTuplesModel):
            return EnumeratedListOfTuplesModel(list(enumerate(data)))  # pyright: ignore
        else:
            return data


class _ListAsNestedDatasetModel(Chain2[EnumeratedListModel, 'NestedDataset']):
    ...


if TYPE_CHECKING:
    from ..json.models import JsonScalarModel  # noqa: F401

    class ListAsNestedDatasetModel(Model[Dataset['NestedDataset | JsonScalarModel']]):
        ...
else:

    class ListAsNestedDatasetModel(_ListAsNestedDatasetModel):
        ...
