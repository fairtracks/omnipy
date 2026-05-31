"""Selection and key-rewriting helpers used by Omnipy dataset indexing operations."""

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable, Mapping, MutableMapping, TypeAlias

from typing_extensions import TypeVar

from omnipy.shared.constants import UNTITLED_KEY
from omnipy.util.helpers import is_iterable

_ValT = TypeVar('_ValT')


@dataclass
class SelectedKeys:
    """Normalized key-selection result used while applying dataset indexing.

    Attributes:
        singular: Whether the original selector targeted a single item.
        keys: Resolved string keys in selection order.
        last_index: Final insertion index used when extra items must be appended.
    """

    singular: bool
    keys: tuple[str, ...]
    last_index: int = -1


Key2DataItemType: TypeAlias = dict[str, tuple[str, _ValT] | None]
Index2DataItemsType: TypeAlias = defaultdict[int, list[tuple[str, _ValT]]]
MappingType: TypeAlias = MutableMapping[str, _ValT]


def select_keys(selector: str | int | slice | Iterable[str | int],
                mapping: MappingType[_ValT]) -> SelectedKeys:
    """Resolve a dataset selector into normalized string keys.

    Args:
        selector: Key, positional index, slice, or iterable of keys and indices.
        mapping: Source mapping whose key order defines positional selection.

    Returns:
        A normalized selection describing the resolved keys and insertion position.

    Raises:
        KeyError: If ``selector`` has an unsupported type.
    """

    if isinstance(selector, str):
        return SelectedKeys(singular=True, keys=(selector,))
    else:
        data_keys = tuple(mapping.keys())

        if isinstance(selector, int):
            return SelectedKeys(singular=True, keys=(data_keys[selector],))

        if isinstance(selector, slice):
            last_index = selector.indices(len(data_keys))[1] - 1
            return SelectedKeys(singular=False, keys=data_keys[selector], last_index=last_index)

        elif is_iterable(selector):
            keys = tuple(data_keys[_] if isinstance(_, int) else _ for _ in selector)
            if keys and keys[-1] in data_keys:
                last_index = data_keys.index(keys[-1])
            else:
                last_index = len(data_keys) - 1
            return SelectedKeys(singular=False, keys=keys, last_index=last_index)

        else:
            raise KeyError('Selector is of incorrect type. Must be a string, a positive integer,'
                           'or a slice (e.g. `dataset[2:5]`).')


def prepare_selected_items_with_mapping_data(
    keys: tuple[str, ...],
    last_index: int,
    data_obj: Mapping[str, _ValT],
) -> tuple[Key2DataItemType[_ValT], Index2DataItemsType[_ValT]]:
    """Align selected keys with mapping data for dataset update operations.

    Args:
        keys: Normalized selected keys.
        last_index: Index after which overflow items should be inserted.
        data_obj: Replacement data supplied as a mapping.

    Returns:
        A tuple containing direct key replacements and indexed overflow insertions.
    """

    data_obj_keys = tuple(data_obj.keys())
    key_2_data_item: Key2DataItemType[_ValT] = {}
    index_2_data_items: Index2DataItemsType[_ValT] = defaultdict(list)

    for i, data_key in enumerate(data_obj.keys()):
        if i < len(keys):
            key_2_data_item[keys[i]] = (data_key, data_obj[data_key])
        else:
            index_2_data_items[last_index].extend((key, data_obj[key]) for key in data_obj_keys[i:])
            break

    if len(keys) > len(data_obj_keys):
        for key in keys[len(data_obj_keys):]:
            key_2_data_item[key] = None

    return key_2_data_item, index_2_data_items


def prepare_selected_items_with_iterable_data(
    keys: tuple[str, ...],
    last_index: int,
    data_obj: tuple[_ValT, ...],
    mapping: Mapping[str, _ValT],
) -> tuple[Key2DataItemType[_ValT], Index2DataItemsType[_ValT]]:
    """Align selected keys with iterable data for dataset update operations.

    Args:
        keys: Normalized selected keys.
        last_index: Index after which overflow items should be inserted.
        data_obj: Replacement data supplied as positional values.
        mapping: Existing mapping used to preserve known keys where possible.

    Returns:
        A tuple containing direct key replacements and indexed overflow insertions.
    """

    key_2_data_item: Key2DataItemType[_ValT] = {}
    index_2_data_items: Index2DataItemsType[_ValT] = defaultdict(list)

    for i, data_val in enumerate(data_obj):
        if i < len(keys):
            if keys[i] in mapping:
                key_2_data_item[keys[i]] = (keys[i], data_val)
            else:
                index_2_data_items[last_index].append((keys[i], data_val))
        else:
            index_2_data_items[last_index].extend(
                (UNTITLED_KEY, val) for j, val in enumerate(data_obj[i:]))
            break

    if len(keys) > len(data_obj):
        for key in keys[len(data_obj):]:
            key_2_data_item[key] = None

    return key_2_data_item, index_2_data_items


def create_updated_mapping(
    mapping: MappingType[_ValT],
    key_2_data_item: Key2DataItemType[_ValT],
    index_2_data_item: Index2DataItemsType[_ValT],
) -> MappingType[_ValT]:
    """Build a new mapping with selected replacements and overflow insertions applied.

    Args:
        mapping: Original mapping to update.
        key_2_data_item: Direct replacements keyed by original selection key.
        index_2_data_item: Extra items grouped by insertion index.

    Returns:
        A new mapping containing the updated key/value order.
    """

    updated_mapping: dict[str, _ValT] = {}

    uniquely_add_extra_items_by_index_to_mapping(-1, index_2_data_item, updated_mapping)

    for i, (key, val) in enumerate(mapping.items()):
        if key in key_2_data_item:
            uniquely_add_item_by_key_to_mapping_if_val(key, key_2_data_item, updated_mapping)
        else:
            uniquely_add_item_to_mapping(key, val, updated_mapping)

        uniquely_add_extra_items_by_index_to_mapping(i, index_2_data_item, updated_mapping)

    return updated_mapping


def uniquely_add_extra_items_by_index_to_mapping(
    index: int,
    index_2_data_item: Index2DataItemsType[_ValT],
    mapping: MappingType[_ValT],
) -> None:
    """Insert any queued overflow items for ``index`` using unique output keys."""

    if index in index_2_data_item:
        for key, val in index_2_data_item[index]:
            uniquely_add_item_to_mapping(key, val, mapping)


def uniquely_add_item_by_key_to_mapping_if_val(
    key: str,
    key_2_data_item: Key2DataItemType[_ValT],
    mapping: MappingType[_ValT],
):
    """Insert a keyed replacement when the selection resolved to an actual value."""

    data_item = key_2_data_item[key]
    if data_item is not None:
        key, val = data_item
        uniquely_add_item_to_mapping(key, val, mapping)


def uniquely_add_item_to_mapping(key: str, val: _ValT, mapping: MappingType[_ValT]) -> None:
    """Insert ``val`` into ``mapping`` under a key made unique if necessary."""

    mapping[make_unique_key(key, mapping)] = val


def make_unique_key(key: str, mapping: MappingType[_ValT]) -> str:
    """Return a non-conflicting key by appending or incrementing a numeric suffix."""

    while key in mapping:
        if is_duplicate_name(key):
            key = increase_duplicate_count(key)
        else:
            key = f'{key}_2'
    return key


def is_duplicate_name(key: str) -> bool:
    """Return whether ``key`` already ends with Omnipy's duplicate-name suffix format."""

    split_key = key.rsplit('_', 1)
    return len(split_key) == 2 and split_key[1].isdigit()


def increase_duplicate_count(key: str) -> str:
    """Increment the numeric duplicate suffix appended to ``key``."""

    key, count = key.rsplit('_', 1)
    return f'{key}_{int(count) + 1}'
