"""Utility predicates and parsers for JSON-compatible values."""

import json

from typing_extensions import TypeIs

import omnipy.util.pydantic as pyd

from .typedefs import Json, JsonDict, JsonList, JsonScalar


def is_json_scalar(json_val: Json) -> TypeIs[JsonScalar]:
    """Return whether a JSON value is a scalar."""

    match json_val:
        case str() | int() | float() | bool() | None:
            return True
        case _:
            return False


def is_json_dict(json_val: Json) -> TypeIs[JsonDict]:
    """Return whether a JSON value is an object."""

    match json_val:
        case dict():
            return True
        case _:
            return False


def is_json_list(json_val: Json) -> TypeIs[JsonList]:
    """Return whether a JSON value is an array."""

    match json_val:
        case list():
            return True
        case _:
            return False


def parse_str_as_json(_line: str) -> Json | pyd.UndefinedType:
    """Parse a string as JSON, returning ``Undefined`` on failure."""

    try:
        return json.loads(_line)
    except json.JSONDecodeError:
        return pyd.Undefined


def parse_line_as_elements_of_dict(_line: str) -> JsonDict | pyd.UndefinedType:
    """Parse a line as the comma-separated contents of a JSON object."""

    if _line.startswith('"'):
        try:
            return json.loads(f'{{{_line}}}')
        except json.JSONDecodeError:
            pass
    return pyd.Undefined


def parse_line_as_elements_of_list(_line: str) -> JsonList | pyd.UndefinedType:
    """Parse a line as the comma-separated contents of a JSON array."""

    try:
        return json.loads(f'[{_line}]')
    except json.JSONDecodeError:
        return pyd.Undefined
