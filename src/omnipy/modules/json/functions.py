from copy import copy
from typing import cast, Dict, Tuple, Union

from omnipy.modules.json.types import (JsonDict,
                                       JsonDictOfAny,
                                       JsonDictOfListsOfDictsOfAny,
                                       JsonDictOfScalars,
                                       JsonListOfAny,
                                       JsonListOfDictsOfAny,
                                       JsonScalar)


def flatten_outer_level_of_nested_record(
    nested_record: JsonDictOfAny,
    record_id: str,
    data_file_title: str,
    id_key: str,
    ref_key: str,
    default_key: str,
) -> Tuple[JsonDictOfScalars, JsonDictOfListsOfDictsOfAny]:

    record_id = ensure_item_first_in_nested_record(nested_record, key=id_key, value=record_id)

    new_data_files: JsonDictOfListsOfDictsOfAny = JsonDictOfListsOfDictsOfAny()
    records_of_scalars: JsonDictOfScalars = JsonDictOfScalars()

    for key, value in nested_record.items():
        if any(isinstance(value, typ) for typ in (dict, list)):
            new_data_file_title: str = f'{data_file_title}.{key}'
            new_data_file: JsonListOfDictsOfAny = transform_into_list_of_dicts(
                cast(Union[JsonListOfAny, JsonDictOfAny], value), default_key=default_key)

            add_references_to_parent_in_child_records(
                child=new_data_file, parent_title=data_file_title, ident=record_id, ref_key=ref_key)

            new_data_files[new_data_file_title] = new_data_file
        else:
            records_of_scalars[key] = cast(JsonScalar, value)

    return records_of_scalars, new_data_files


def ensure_item_first_in_nested_record(
    nested_record: JsonDictOfAny,
    key: str,
    value: str,
    fail_if_present: bool = False,
) -> str:
    if key in nested_record:
        assert not fail_if_present, f'Key "{key}" already present in dict'
        del nested_record[key]

    update_dict_from_front(nested_record, {key: value})

    return value


def update_dict_from_front(dict_a: Dict, dict_b: Dict) -> None:
    dict_a_copy = copy(dict_a)
    dict_a.clear()
    dict_a.update(dict_b)
    dict_a.update(dict_a_copy)


def transform_into_list_of_dicts(value: Union[JsonListOfAny, JsonDictOfAny],
                                 default_key: str) -> JsonListOfDictsOfAny:
    if isinstance(value, JsonDict):
        return JsonListOfDictsOfAny([value])
    else:
        ret_value = JsonListOfDictsOfAny()

        for list_val in value:
            if isinstance(list_val, dict):
                ret_value.append(list_val)
            else:
                new_nested_record = JsonDictOfAny({default_key: list_val})
                ret_value.append(new_nested_record)

        return ret_value


def add_references_to_parent_in_child_records(
    child: JsonListOfDictsOfAny,
    parent_title: str,
    ident: str,
    ref_key: str,
):
    ref_value = get_ref_value(parent_title, ident)
    for new_nested_record in child:
        ensure_item_first_in_nested_record(
            new_nested_record, key=ref_key, value=ref_value, fail_if_present=True)


def get_ref_value(data_file_title: str, ident: str) -> str:
    return f'{data_file_title}.{ident}'
