from typing import Any, Dict, Mapping, Union


def create_merged_dict(dict_1: Union[Mapping[Any, Any]],
                       dict_2: Union[Mapping[Any, Any]]) -> Dict[Any, Any]:
    merged_dict = dict(dict_1)
    merged_dict.update(dict_2)
    return merged_dict
