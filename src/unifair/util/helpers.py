from types import MappingProxyType
from typing import Any, Dict, Union


def create_merged_dict(dict_1: Union[Dict[Any, Any], MappingProxyType[Any, Any]],
                       dict_2: Union[Dict[Any, Any], MappingProxyType[Any, Any]]) -> Dict[Any, Any]:
    merged_dict = dict(dict_1)
    merged_dict.update(dict_2)
    return merged_dict
