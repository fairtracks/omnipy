from collections.abc import KeysView
from enum import Enum
from textwrap import TextWrapper
from types import MappingProxyType
from typing import Any, Mapping, Sequence

import inflection

from omnipy.util.helpers import is_unreserved_identifier
from omnipy.util.literal_enum import LiteralEnum, LiteralEnumInnerTypes

ValueType = (
    Sequence[LiteralEnumInnerTypes]
    | Mapping[str, LiteralEnumInnerTypes]
    | MappingProxyType[str, LiteralEnumInnerTypes])


def generate_literal_enum_code(
    values: ValueType,
    docstrings: Mapping[LiteralEnumInnerTypes, Sequence[str]] | None = None,
    include_imports: bool = True,
    class_name: str = 'NewLiteralEnum',
) -> str:
    """
    Generate code for a LiteralEnum class based on a tuple of string values.

    Parameters:
        values: Either one of the following:
            1. Tuple of objects that define the literal values for the enum,
               where each value will be converted to a valid attribute name
            2. Dict of string keys to values, where the keys are used as
               attribute names
        docstrings: Optional dictionary mapping values to their
            corresponding docstrings. If provided, the docstrings will be
            added to the generated class attributes. The keys should match
            the values in `values`. If None, no docstrings are added
            (default: None)
        include_imports: If True, includes necessary imports for Literal and
            LiteralEnum (default: True)
        class_name: The name of the generated class (default:
            'GeneratedEnum')

    Returns:
        A string containing the complete Python code for a LiteralEnum class

    Raises:
        ValueError: If no values are provided or if class_name is not a
            valid identifier

    Example:
        >>> code = generate_literal_enum_code(('active', 'inactive', 'pending'))
        >>> print(code)
        from typing import Literal

        from omnipy.util.literal_enum import LiteralEnum


        class GeneratedEnum(LiteralEnum[str]):
            Literals = Literal['active', 'inactive', 'pending']
            ACTIVE: Literal['active'] = 'active'
            INACTIVE: Literal['inactive'] = 'inactive'
            PENDING: Literal['pending'] = 'pending'
    """
    enum_mappings = _generate_attrib_names(values)
    _check_params(values, docstrings, class_name, enum_mappings)

    lines: list[str] = []

    lines = _build_import_lines(lines, include_imports)
    lines = _build_class_definition_lines(lines, class_name, enum_mappings)
    lines = _build_attribute_definitions(docstrings, enum_mappings, lines)

    code = '\n'.join(lines)
    return code


def _generate_attrib_names(values: ValueType) -> Mapping[str, LiteralEnumInnerTypes]:
    enum_mappings: dict[str, LiteralEnumInnerTypes] = {}

    match values:
        case dict() | MappingProxyType():
            for key, value in values.items():
                enum_mappings[key] = value.value if isinstance(value, Enum) else value
        case _:
            for value in values:
                # Convert value to a valid attribute name
                attr_name = _generate_attribute_name(value, enum_mappings.keys())
                enum_mappings[attr_name] = value

    return enum_mappings


def _generate_attribute_name(value: Any, used_names: KeysView[str]) -> str:
    """
    Generate a valid Python attribute name from a value.

    Parameters:
        value: The value to convert to an attribute name
        used_names: QAlready used attribute names to avoid conflicts

    Returns:
        A valid Python attribute name
    """
    import re

    if not isinstance(value, str):
        value = str(value)

    if value == '':
        base_name = 'empty'
    elif value[0].isdigit():
        base_name = f'number_{value}'
    elif value.isspace():
        base_name = 'whitespace'
    else:
        base_name = value

    # Transliterate non-ascii characters
    base_name = inflection.transliterate(base_name)

    # Transform to snake_case and uppercase
    base_name = inflection.underscore(base_name).upper()

    # Replace non-alphanumeric characters with underscores
    base_name = re.sub(r'[^a-zA-Z0-9_]', '_', base_name)

    # Remove leading/trailing underscores and collapse multiple underscores
    base_name = re.sub(r'^_+|_+$', '', base_name)
    base_name = re.sub(r'_+', '_', base_name)

    # Ensure it's a valid identifier (this should now always pass)
    if not is_unreserved_identifier(base_name):
        base_name = f'VALUE_{base_name}'

    # Handle conflicts by adding a suffix
    candidate = base_name
    counter = 2
    while candidate in used_names:
        candidate = f'{base_name}_{counter}'
        counter += 1

    return candidate


def _check_params(values: ValueType,
                  docstrings: Mapping[LiteralEnumInnerTypes, Sequence[str]] | None,
                  class_name: str,
                  enum_mappings: Mapping[str, LiteralEnumInnerTypes]) -> None:
    if not values:
        raise ValueError('At least one value must be provided')

    if not is_unreserved_identifier(class_name):
        raise ValueError(f'"{class_name}" is not a valid Python class name')

    if docstrings:
        for val in docstrings:
            if val not in enum_mappings.values():
                raise ValueError(f'Docstring for {val!r} does not match any value')


def _build_import_lines(lines: list[str], include_imports: bool) -> list[str]:
    # Build the class code. First. we need to check if we need to include imports
    if include_imports:
        lines += [
            'from typing import Literal',
            'from omnipy.util.literal_enum import LiteralEnum',
            '',
            ''
        ]

    return lines


def _build_class_definition_lines(
    lines: list[str],
    class_name: str,
    enum_mappings: Mapping[str, LiteralEnumInnerTypes],
) -> list[str]:

    # Detect the value types
    value_types = {type(value).__name__: type(value) for value in enum_mappings.values()}
    inner_types = LiteralEnum.ALLOWED_LITERAL_INNER_TYPES
    for name, type_ in value_types.items():
        if type_ not in inner_types:
            raise ValueError(f'Unsupported value type: {name}. Allowed types: '
                             f"{', '.join(_.__name__ for _ in inner_types)}.")

    # Build the literals string
    literals_str = ', '.join(repr(value) for value in enum_mappings.values())

    # Add class definition
    lines += [
        f"class {class_name}(LiteralEnum[{' | '.join(value_types.keys())}]):",
        f'    Literals = Literal[{literals_str}]',
        '',
    ]

    return lines


def _build_attribute_definitions(
    docstrings: Mapping[LiteralEnumInnerTypes, Sequence[str]] | None,
    enum_mappings: Mapping[str, LiteralEnumInnerTypes],
    lines: list[str],
):
    textwrapper = TextWrapper(
        width=76,
        initial_indent='    ',
        subsequent_indent='    ',
    )
    # Add attribute definitions
    for attr_name, value in enum_mappings.items():
        lines.append(f'    {attr_name}: Literal[{repr(value)}] = {repr(value)}')
        if docstrings and value in docstrings:
            lines += ['    """']
            for paragraph in docstrings[value]:
                lines += textwrapper.wrap(paragraph) + ['']
            del lines[-1]
            lines += ['    """', '']

    return lines
