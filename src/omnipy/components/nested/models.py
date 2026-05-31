"""Models for representing nested datasets and enumerated list structures."""

from typing_extensions import TypeVar

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.shared.typing import TYPE_CHECKING

from ..general.models import Chain2

if TYPE_CHECKING:
    from .datasets import NestedDataset  # noqa: F401

DatasetT = TypeVar('DatasetT')


class EnumeratedListOfTuplesModel(Model[list[tuple[int, object]]]):
    """Store an ordered list of index/value tuples with strict sequence checks.

    The model asserts that tuple indices are contiguous and start at zero,
    preserving explicit positional semantics for nested list conversion.
    """
    @classmethod
    def _parse_data(cls, data: list[tuple[int, object]]) -> list[tuple[int, object]]:
        for expected_index, (actual_index, _) in enumerate(data):
            if expected_index != actual_index:
                raise ValueError(f'Indices are not sequential starting from 0: '
                                 f'expected {expected_index}, got {actual_index}')
        return data


class EnumeratedListModel(Model[EnumeratedListOfTuplesModel | list[object]
                                | list[dict[str, object]]]):
    """Convert plain lists into explicitly enumerated index/value tuples.

    Incoming list-like structures are normalized to
    :class:`EnumeratedListOfTuplesModel` using ``enumerate``.
    """
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
        """Represent list-like input as a nested dataset structure.

        The model acts as a typed bridge between list representations and recursive
        nested dataset forms used throughout nested components.
        """

        ...
else:

    class ListAsNestedDatasetModel(_ListAsNestedDatasetModel):
        """Represent list-like input as a nested dataset structure.

        The model acts as a typed bridge between list representations and recursive
        nested dataset forms used throughout nested components.
        """

        ...
