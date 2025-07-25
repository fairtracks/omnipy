from copy import copy
from typing import cast

from .typedefs import (JsonDict,
                       JsonDictOfListsOfDicts,
                       JsonDictOfScalars,
                       JsonList,
                       JsonListOfDicts,
                       JsonScalar)


def flatten_outer_level_of_nested_record(
    nested_record: JsonDict,
    record_id: str,
    data_file_title: str,
    id_key: str,
    ref_key: str,
    default_key: str,
) -> tuple[JsonDictOfScalars, JsonDictOfListsOfDicts]:

    record_id = _ensure_item_first_in_nested_record(
        nested_record, key=id_key, value=f'{data_file_title}.{record_id}')

    new_data_files: JsonDictOfListsOfDicts = JsonDictOfListsOfDicts()
    records_of_scalars: JsonDictOfScalars = JsonDictOfScalars()

    for key, value in nested_record.items():
        if any(isinstance(value, typ) for typ in (dict, list)):
            new_data_file_title: str = f'{data_file_title}.{key}'
            new_data_file: JsonListOfDicts = _transform_into_list_of_dicts(
                cast(JsonList | JsonDict, value), default_key=default_key)

            _add_references_to_parent_in_child_records(
                child=new_data_file, parent_title=data_file_title, ident=record_id, ref_key=ref_key)

            new_data_files[new_data_file_title] = new_data_file
        else:
            records_of_scalars[key] = cast(JsonScalar, value)

    return records_of_scalars, new_data_files


def _ensure_item_first_in_nested_record(
    nested_record: JsonDict,
    key: str,
    value: str,
    fail_if_present: bool = False,
) -> str:
    if key in nested_record:
        assert not fail_if_present, f'Key "{key}" already present in dict'
        existing_value = nested_record[key]
        if isinstance(existing_value, str):
            value = existing_value
        del nested_record[key]

    _update_dict_from_front(nested_record, {key: value})

    return value


def _update_dict_from_front(dict_a: dict, dict_b: dict) -> None:
    dict_a_copy = copy(dict_a)
    dict_a.clear()
    dict_a.update(dict_b)
    dict_a.update(dict_a_copy)


def _transform_into_list_of_dicts(value: JsonList | JsonDict, default_key: str) -> JsonListOfDicts:
    if isinstance(value, dict):
        return JsonListOfDicts([value])
    else:
        ret_value = JsonListOfDicts()

        for list_val in value:
            if isinstance(list_val, dict):
                ret_value.append(list_val)
            else:
                new_nested_record = JsonDict({default_key: list_val})
                ret_value.append(new_nested_record)

        return ret_value


def _add_references_to_parent_in_child_records(
    child: JsonListOfDicts,
    parent_title: str,
    ident: str,
    ref_key: str,
):
    for new_nested_record in child:
        _ensure_item_first_in_nested_record(
            new_nested_record, key=ref_key, value=ident, fail_if_present=True)
