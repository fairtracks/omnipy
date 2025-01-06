from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable, Mapping, MutableMapping, TypeAlias

from typing_extensions import TypeVar

from omnipy.data.constants import UNTITLED_KEY
from omnipy.util.helpers import is_iterable

_ValT = TypeVar('_ValT')


@dataclass
class SelectedKeys:
    singular: bool
    keys: tuple[str, ...]
    last_index: int = -1


Key2DataItemType: TypeAlias = dict[str, tuple[str, _ValT] | None]
Index2DataItemsType: TypeAlias = defaultdict[int, list[tuple[str, _ValT]]]
MappingType: TypeAlias = MutableMapping[str, _ValT]


def select_keys(selector: str | int | slice | Iterable[str | int],
                mapping: MappingType[_ValT]) -> SelectedKeys:
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
    if index in index_2_data_item:
        for key, val in index_2_data_item[index]:
            uniquely_add_item_to_mapping(key, val, mapping)


def uniquely_add_item_by_key_to_mapping_if_val(
    key: str,
    key_2_data_item: Key2DataItemType[_ValT],
    mapping: MappingType[_ValT],
):
    data_item = key_2_data_item[key]
    if data_item is not None:
        key, val = data_item
        uniquely_add_item_to_mapping(key, val, mapping)


def uniquely_add_item_to_mapping(key: str, val: _ValT, mapping: MappingType[_ValT]) -> None:
    mapping[make_unique_key(key, mapping)] = val


def make_unique_key(key: str, mapping: MappingType[_ValT]) -> str:
    while key in mapping:
        if is_duplicate_name(key):
            key = increase_duplicate_count(key)
        else:
            key = f'{key}_2'
    return key


def is_duplicate_name(key: str) -> bool:
    split_key = key.rsplit('_', 1)
    return len(split_key) == 2 and split_key[1].isdigit()


def increase_duplicate_count(key: str) -> str:
    key, count = key.rsplit('_', 1)
    return f'{key}_{int(count) + 1}'
