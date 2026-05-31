"""JSON dataset types for collections of items with specific JSON shapes."""

from typing import Generic

from typing_extensions import TypeVar

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model

from .models import (JsonDictModel,
                     JsonDictOfDictsModel,
                     JsonDictOfDictsOfScalarsModel,
                     JsonDictOfListsModel,
                     JsonDictOfListsOfDictsModel,
                     JsonDictOfListsOfScalarsModel,
                     JsonDictOfNestedListsModel,
                     JsonDictOfScalarsModel,
                     JsonListModel,
                     JsonListOfDictsModel,
                     JsonListOfDictsOfScalarsModel,
                     JsonListOfListsModel,
                     JsonListOfListsOfScalarsModel,
                     JsonListOfNestedDictsModel,
                     JsonListOfScalarsModel,
                     JsonListOrDictModel,
                     JsonModel,
                     JsonNestedDictsModel,
                     JsonNestedListsModel,
                     JsonOnlyDictsModel,
                     JsonOnlyListsModel,
                     JsonScalarModel)

_JsonModelT = TypeVar('_JsonModelT', bound=Model, default=JsonModel)


class JsonBaseDataset(Dataset[_JsonModelT], Generic[_JsonModelT]):
    """Base dataset for collections of JSON-model items.

    Args:
        data: Optional mapping from file keys to JSON-compatible values that
            can be parsed by ``_JsonModelT``.

    Returns:
        JsonBaseDataset: Dataset instance containing validated JSON-model files.

    Raises:
        Exception: Propagates validation errors from the bound JSON model type.

    Example:
        >>> dataset = JsonBaseDataset[JsonModel]({'item': {'a': 1}})
        >>> tuple(dataset.keys())
        ('item',)
    """
    ...


class JsonDataset(JsonBaseDataset[JsonModel]):
    """Dataset whose files accept any valid JSON value.

    Args:
        data: Optional mapping from file keys to JSON-compatible values.

    Returns:
        JsonDataset: Dataset where each file is validated as a ``JsonModel``.

    Raises:
        Exception: Propagates validation errors from ``JsonModel``.

    Example:
        >>> dataset = JsonDataset({'item': [1, {'a': True}]})
        >>> dataset['item'].to_data()
        [1, {'a': True}]
    """
    ...


class JsonListOrDictDataset(JsonBaseDataset[JsonListOrDictModel]):
    """Dataset for JSON files constrained to top-level arrays or objects.

    Args:
        data: Optional mapping from file keys to list/dict JSON values.

    Returns:
        JsonListOrDictDataset: Dataset validated by ``JsonListOrDictModel``.

    Raises:
        Exception: Propagates validation errors when scalar JSON values are
            provided.

    Example:
        >>> dataset = JsonListOrDictDataset({'item': {'a': 1}})
        >>> dataset['item'].to_data()
        {'a': 1}
    """
    ...


class JsonScalarDataset(JsonBaseDataset[JsonScalarModel]):
    """Dataset for JSON scalar files.

    Args:
        data: Optional mapping from file keys to scalar JSON values.

    Returns:
        JsonScalarDataset: Dataset validated by ``JsonScalarModel``.

    Raises:
        Exception: Propagates validation errors when non-scalar values are
            provided.

    Example:
        >>> dataset = JsonScalarDataset({'answer': 42})
        >>> dataset['answer'].to_data()
        42
    """
    ...


# List at the top level


class JsonListDataset(JsonBaseDataset[JsonListModel]):
    """Dataset for JSON files with a top-level list.

    Args:
        data: Optional mapping from file keys to list-shaped JSON values.

    Returns:
        JsonListDataset: Dataset validated by ``JsonListModel``.

    Raises:
        Exception: Propagates validation errors when top-level values are not
            lists.

    Example:
        >>> dataset = JsonListDataset({'numbers': [1, 2, 3]})
        >>> dataset['numbers'].to_data()
        [1, 2, 3]
    """
    ...


class JsonListOfScalarsDataset(JsonBaseDataset[JsonListOfScalarsModel]):
    """Dataset for JSON files containing scalar-only lists.

    Args:
        data: Optional mapping from file keys to lists of JSON scalar values.

    Returns:
        JsonListOfScalarsDataset: Dataset validated by
        ``JsonListOfScalarsModel``.

    Raises:
        Exception: Propagates validation errors when list items are not scalar
            JSON values.

    Example:
        >>> dataset = JsonListOfScalarsDataset({'scores': [1, 2, 3]})
        >>> dataset['scores'].to_data()
        [1, 2, 3]
    """
    ...


class JsonListOfListsDataset(JsonBaseDataset[JsonListOfListsModel]):
    """Dataset for JSON files containing lists of JSON lists.

    Args:
        data: Optional mapping from file keys to list-of-list JSON values.

    Returns:
        JsonListOfListsDataset: Dataset validated by ``JsonListOfListsModel``.

    Raises:
        Exception: Propagates validation errors when top-level items are not
            JSON lists.

    Example:
        >>> dataset = JsonListOfListsDataset({'matrix': [[1], [2, 3]]})
        >>> dataset['matrix'].to_data()
        [[1], [2, 3]]
    """
    ...


class JsonListOfListsOfScalarsDataset(JsonBaseDataset[JsonListOfListsOfScalarsModel]):
    """Dataset for JSON files containing nested scalar-only lists.

    Args:
        data: Optional mapping from file keys to lists of scalar-only JSON
            lists.

    Returns:
        JsonListOfListsOfScalarsDataset: Dataset validated by
        ``JsonListOfListsOfScalarsModel``.

    Raises:
        Exception: Propagates validation errors when nested values are not JSON
            scalars.

    Example:
        >>> dataset = JsonListOfListsOfScalarsDataset({'matrix': [[1, 2], [3, 4]]})
        >>> dataset['matrix'].to_data()
        [[1, 2], [3, 4]]
    """
    ...


class JsonListOfDictsDataset(JsonBaseDataset[JsonListOfDictsModel]):
    """Dataset for JSON files containing lists of JSON objects.

    Args:
        data: Optional mapping from file keys to list-of-dict JSON values.

    Returns:
        JsonListOfDictsDataset: Dataset validated by ``JsonListOfDictsModel``.

    Raises:
        Exception: Propagates validation errors when top-level items are not
            JSON objects.

    Example:
        >>> dataset = JsonListOfDictsDataset({'records': [{'a': 1}, {'a': 2}]})
        >>> dataset['records'].to_data()
        [{'a': 1}, {'a': 2}]
    """
    ...


class JsonListOfDictsOfScalarsDataset(JsonBaseDataset[JsonListOfDictsOfScalarsModel]):
    """Dataset for lists of scalar-valued JSON objects.

    Args:
        data: Optional mapping from file keys to lists of dicts with scalar
            JSON values.

    Returns:
        JsonListOfDictsOfScalarsDataset: Dataset validated by
        ``JsonListOfDictsOfScalarsModel``.

    Raises:
        Exception: Propagates validation errors when object values are not JSON
            scalars.

    Example:
        >>> dataset = JsonListOfDictsOfScalarsDataset({'records': [{'a': 1}, {'a': 2}]})
        >>> dataset['records'].to_data()
        [{'a': 1}, {'a': 2}]
    """
    ...


# Dict at the top level


class JsonDictDataset(JsonBaseDataset[JsonDictModel]):
    """Dataset for JSON files with a top-level object.

    Args:
        data: Optional mapping from file keys to dict-shaped JSON values.

    Returns:
        JsonDictDataset: Dataset validated by ``JsonDictModel``.

    Raises:
        Exception: Propagates validation errors when top-level values are not
            JSON objects.

    Example:
        >>> dataset = JsonDictDataset({'obj': {'a': [1, 2]}})
        >>> dataset['obj'].to_data()
        {'a': [1, 2]}
    """
    ...


class JsonDictOfScalarsDataset(JsonBaseDataset[JsonDictOfScalarsModel]):
    """Dataset for JSON objects with scalar values.

    Args:
        data: Optional mapping from file keys to dict JSON values where each
            value is scalar.

    Returns:
        JsonDictOfScalarsDataset: Dataset validated by
        ``JsonDictOfScalarsModel``.

    Raises:
        Exception: Propagates validation errors when object values are not
            JSON scalars.

    Example:
        >>> dataset = JsonDictOfScalarsDataset({'item': {'a': 1, 'b': True}})
        >>> dataset['item'].to_data()
        {'a': 1, 'b': True}
    """
    ...


class JsonDictOfListsDataset(JsonBaseDataset[JsonDictOfListsModel]):
    """Dataset for JSON objects whose values are JSON lists.

    Args:
        data: Optional mapping from file keys to dict JSON values containing
            lists.

    Returns:
        JsonDictOfListsDataset: Dataset validated by ``JsonDictOfListsModel``.

    Raises:
        Exception: Propagates validation errors when object values are not JSON
            lists.

    Example:
        >>> dataset = JsonDictOfListsDataset({'item': {'a': [1], 'b': [2, 3]}})
        >>> dataset['item'].to_data()
        {'a': [1], 'b': [2, 3]}
    """
    ...


class JsonDictOfListsOfScalarsDataset(JsonBaseDataset[JsonDictOfListsOfScalarsModel]):
    """Dataset for objects whose values are scalar-only JSON lists.

    Args:
        data: Optional mapping from file keys to dict JSON values with
            scalar-only list values.

    Returns:
        JsonDictOfListsOfScalarsDataset: Dataset validated by
        ``JsonDictOfListsOfScalarsModel``.

    Raises:
        Exception: Propagates validation errors when nested list values are not
            JSON scalars.

    Example:
        >>> dataset = JsonDictOfListsOfScalarsDataset({'item': {'a': [1], 'b': [2, 3]}})
        >>> dataset['item'].to_data()
        {'a': [1], 'b': [2, 3]}
    """
    ...


class JsonDictOfDictsDataset(JsonBaseDataset[JsonDictOfDictsModel]):
    """Dataset for JSON objects whose values are JSON objects.

    Args:
        data: Optional mapping from file keys to dict-of-dict JSON values.

    Returns:
        JsonDictOfDictsDataset: Dataset validated by ``JsonDictOfDictsModel``.

    Raises:
        Exception: Propagates validation errors when object values are not JSON
            objects.

    Example:
        >>> dataset = JsonDictOfDictsDataset({'item': {'a': {'x': 1}}})
        >>> dataset['item'].to_data()
        {'a': {'x': 1}}
    """
    ...


class JsonDictOfDictsOfScalarsDataset(JsonBaseDataset[JsonDictOfDictsOfScalarsModel]):
    """Dataset for nested objects with scalar leaves.

    Args:
        data: Optional mapping from file keys to dict-of-dict JSON values with
            scalar leaves.

    Returns:
        JsonDictOfDictsOfScalarsDataset: Dataset validated by
        ``JsonDictOfDictsOfScalarsModel``.

    Raises:
        Exception: Propagates validation errors when nested values are not JSON
            scalars.

    Example:
        >>> dataset = JsonDictOfDictsOfScalarsDataset({'item': {'a': {'x': 1}}})
        >>> dataset['item'].to_data()
        {'a': {'x': 1}}
    """
    ...


# Nested datasets


class JsonOnlyListsDataset(JsonBaseDataset[JsonOnlyListsModel]):
    """Dataset for JSON content composed of lists and scalar leaves.

    Args:
        data: Optional mapping from file keys to scalar-or-nested-list JSON
            values.

    Returns:
        JsonOnlyListsDataset: Dataset validated by ``JsonOnlyListsModel``.

    Raises:
        Exception: Propagates validation errors when dict values are present.

    Example:
        >>> dataset = JsonOnlyListsDataset({'item': [1, [2, 3]]})
        >>> dataset['item'].to_data()
        [1, [2, 3]]
    """
    ...


class JsonNestedListsDataset(JsonBaseDataset[JsonNestedListsModel]):
    """Dataset for nested JSON lists with scalar leaves.

    Args:
        data: Optional mapping from file keys to nested list JSON values.

    Returns:
        JsonNestedListsDataset: Dataset validated by ``JsonNestedListsModel``.

    Raises:
        Exception: Propagates validation errors when nested values include JSON
            objects.

    Example:
        >>> dataset = JsonNestedListsDataset({'item': [[1], [2, [3]]]})
        >>> dataset['item'].to_data()
        [[1], [2, [3]]]
    """
    ...


class JsonOnlyDictsDataset(JsonBaseDataset[JsonOnlyDictsModel]):
    """Dataset for JSON content composed of objects and scalar leaves.

    Args:
        data: Optional mapping from file keys to scalar-or-nested-object JSON
            values.

    Returns:
        JsonOnlyDictsDataset: Dataset validated by ``JsonOnlyDictsModel``.

    Raises:
        Exception: Propagates validation errors when list values are present.

    Example:
        >>> dataset = JsonOnlyDictsDataset({'item': {'a': {'b': 1}}})
        >>> dataset['item'].to_data()
        {'a': {'b': 1}}
    """
    ...


class JsonNestedDictsDataset(JsonBaseDataset[JsonNestedDictsModel]):
    """Dataset for nested JSON objects with scalar leaves.

    Args:
        data: Optional mapping from file keys to nested-object JSON values.

    Returns:
        JsonNestedDictsDataset: Dataset validated by ``JsonNestedDictsModel``.

    Raises:
        Exception: Propagates validation errors when nested values include JSON
            arrays.

    Example:
        >>> dataset = JsonNestedDictsDataset({'item': {'a': {'b': 1}}})
        >>> dataset['item'].to_data()
        {'a': {'b': 1}}
    """
    ...


# More specific datasets


class JsonListOfNestedDictsDataset(JsonBaseDataset[JsonListOfNestedDictsModel]):
    """Dataset for JSON lists whose items are nested objects.

    Args:
        data: Optional mapping from file keys to list JSON values of nested
            objects.

    Returns:
        JsonListOfNestedDictsDataset: Dataset validated by
        ``JsonListOfNestedDictsModel``.

    Raises:
        Exception: Propagates validation errors when list items are not nested
            JSON objects.

    Example:
        >>> dataset = JsonListOfNestedDictsDataset({'item': [{'a': {'b': 1}}]})
        >>> dataset['item'].to_data()
        [{'a': {'b': 1}}]
    """
    ...


class JsonDictOfNestedListsDataset(JsonBaseDataset[JsonDictOfNestedListsModel]):
    """Dataset for JSON objects whose values are nested lists.

    Args:
        data: Optional mapping from file keys to dict JSON values containing
            nested lists.

    Returns:
        JsonDictOfNestedListsDataset: Dataset validated by
        ``JsonDictOfNestedListsModel``.

    Raises:
        Exception: Propagates validation errors when object values are not
            nested JSON lists.

    Example:
        >>> dataset = JsonDictOfNestedListsDataset({'item': {'a': [[1], [2]]}})
        >>> dataset['item'].to_data()
        {'a': [[1], [2]]}
    """
    ...


class JsonDictOfListsOfDictsDataset(JsonBaseDataset[JsonDictOfListsOfDictsModel]):
    """Dataset for JSON objects whose values are lists of objects.

    Args:
        data: Optional mapping from file keys to dict JSON values of
            list-of-object structures.

    Returns:
        JsonDictOfListsOfDictsDataset: Dataset validated by
        ``JsonDictOfListsOfDictsModel``.

    Raises:
        Exception: Propagates validation errors when object values are not
            list-of-object JSON structures.

    Example:
        >>> dataset = JsonDictOfListsOfDictsDataset({'item': {'a': [{'b': 1}]}})
        >>> dataset['item'].to_data()
        {'a': [{'b': 1}]}
    """
    ...


# Custom datasets
