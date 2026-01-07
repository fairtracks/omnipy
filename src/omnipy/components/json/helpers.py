import json

from typing_extensions import TypeIs

import omnipy.util._pydantic as pyd

from .typedefs import Json, JsonDict, JsonList, JsonScalar


def is_json_scalar(json_val: Json) -> TypeIs[JsonScalar]:
    match json_val:
        case str() | int() | float() | bool() | None:
            return True
        case _:
            return False


def is_json_dict(json_val: Json) -> TypeIs[JsonDict]:
    match json_val:
        case dict():
            return True
        case _:
            return False


def is_json_list(json_val: Json) -> TypeIs[JsonList]:
    match json_val:
        case list():
            return True
        case _:
            return False


def parse_str_as_json(_line: str) -> Json | pyd.UndefinedType:
    try:
        return json.loads(_line)
    except json.JSONDecodeError:
        return pyd.Undefined


def parse_line_as_elements_of_dict(_line: str) -> JsonDict | pyd.UndefinedType:
    if _line.startswith('"'):
        try:
            return json.loads(f'{{{_line}}}')
        except json.JSONDecodeError:
            pass
    return pyd.Undefined


def parse_line_as_elements_of_list(_line: str) -> JsonList | pyd.UndefinedType:
    try:
        return json.loads(f'[{_line}]')
    except json.JSONDecodeError:
        return pyd.Undefined
