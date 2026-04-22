from typing import Union

from typing_extensions import TypeVar

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.shared.typing import TYPE_CHECKING

from ..general.models import Chain2
from ..json.typedefs import JsonScalar

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


class MixedJsonDictModel(Model[Union[tuple[dict[str, JsonScalar], 'NestedDataset'],
                                     dict[str, object]]]):
    @classmethod
    def _parse_data(
        cls, data: Union[tuple[dict[str, JsonScalar], 'NestedDataset'], dict[str, object]]
    ) -> tuple[dict[str, JsonScalar], 'NestedDataset']:
        from .datasets import NestedDataset

        data_scalars: dict[str, JsonScalar] = {}
        nested_data = NestedDataset()

        if isinstance(data, tuple):
            return data

        for key, val in data.items():
            if isinstance(val, JsonScalar):
                data_scalars[key] = val
            else:
                nested_data[key] = val

        assert len(nested_data) > 0
        assert len(data_scalars) > 0

        return data_scalars, nested_data
