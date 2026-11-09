"""Models for representing nested datasets and enumerated list structures."""

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.shared.typing import TYPE_CHECKING

from ..general.models import (
    Chain2,
    EnumeratedListModel,
)

if TYPE_CHECKING:
    from .datasets import StructuredNestedDataset  # noqa: F401


class _ListAsStructuredNestedDatasetModel(
    Chain2[EnumeratedListModel, 'StructuredNestedDataset']
): ...


if TYPE_CHECKING:
    from ..json.models import JsonScalarModel  # noqa: F401

    class ListAsStructuredNestedDatasetModel(
        Model[Dataset['StructuredNestedDataset | JsonScalarModel']]
    ):
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
