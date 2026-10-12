"""Models for representing nested datasets and enumerated list structures."""

from typing_extensions import TypeVar

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.shared.typing import TYPE_CHECKING

from ..general.models import Chain2

if TYPE_CHECKING:
    from .datasets import StructuredNestedDataset  # noqa: F401

DatasetT = TypeVar('DatasetT')


class EnumeratedListOfTuplesModel(Model[list[tuple[int, object]]]):
    """A Model for explicit list positions.

    Its data consists of ordered ``(index, value)`` pairs. The indices must
    form the contiguous sequence ``0, 1, ...``; validation rejects gaps,
    reordering, and a non-zero first index.

    This Model marks list data whose positions have already been made explicit.
    ``EnumeratedListModel`` uses it as the canonical form before list positions
    become names for Dataset items.
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
    """A Model for list data before it becomes named Dataset items.

    Ordinary list input is given explicit zero-based positions in an
    ``EnumeratedListOfTuplesModel``. Input that is already an
    ``EnumeratedListOfTuplesModel`` is retained as such.

    An explicit-position Model distinguishes an ordinary list whose values
    happen to be tuples from list data that is already prepared for
    interpretation as Dataset items.
    """
    @classmethod
    def _parse_data(
        cls, data: EnumeratedListOfTuplesModel | list[object] | list[dict[str, object]]
    ) -> EnumeratedListOfTuplesModel:
        if not isinstance(data, EnumeratedListOfTuplesModel):
            return EnumeratedListOfTuplesModel(list(enumerate(data)))  # pyright: ignore
        else:
            return data


class _ListAsStructuredNestedDatasetModel(Chain2[EnumeratedListModel, 'StructuredNestedDataset']):
    ...


if TYPE_CHECKING:
    from ..json.models import JsonScalarModel  # noqa: F401

    class ListAsStructuredNestedDatasetModel(
            Model[Dataset['StructuredNestedDataset | JsonScalarModel']]):
        """A Model representing a list as a position-keyed StructuredNestedDataset.

        List positions become the names of Dataset items: ``['a', {'b': 1}]`` is
        represented as ``{'0': 'a', '1': {'b': 1}}``. The values of those items are
        then interpreted recursively by ``StructuredNestedDataset`` according to
        ``NestedUnion``.

        This lets list values participate in the same bottom-up structuring of
        hierarchical data as mappings, tables, records, and scalar values.
        """

        ...
else:

    class ListAsStructuredNestedDatasetModel(_ListAsStructuredNestedDatasetModel):
        """A Model representing a list as a position-keyed StructuredNestedDataset.

        List positions become the names of Dataset items: ``['a', {'b': 1}]`` is
        represented as ``{'0': 'a', '1': {'b': 1}}``. The values of those items are
        then interpreted recursively by ``StructuredNestedDataset`` according to
        ``NestedUnion``.

        This lets list values participate in the same bottom-up structuring of
        hierarchical data as mappings, tables, records, and scalar values.
        """

        ...
