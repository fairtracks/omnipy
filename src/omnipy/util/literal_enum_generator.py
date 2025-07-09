from collections.abc import KeysView
from enum import Enum
from types import MappingProxyType
from typing import Any, Literal, overload

import inflection

from omnipy.util.helpers import is_unreserved_identifier


@overload
def generate_literal_enum_code(
    values: tuple[object, ...] | dict[str, object] | MappingProxyType[str, object],
    print_to_stdout: Literal[False],
    include_imports: bool = ...,
    class_name: str = ...,
) -> str:
    ...


@overload
def generate_literal_enum_code(
    values: tuple[object, ...] | dict[str, object] | MappingProxyType[str, object],
    print_to_stdout: Literal[True] = ...,
    include_imports: bool = ...,
    class_name: str = ...,
) -> None:
    ...


def generate_literal_enum_code(
    values: tuple[object, ...] | dict[str, object] | MappingProxyType[str, Enum | object],
    print_to_stdout: bool = True,
    include_imports: bool = True,
    class_name: str = 'NewLiteralEnum',
) -> str | None:
    """
    Generate code for a LiteralEnum class based on a tuple of string values.

    Args:
        values: Either one of the following:
            1. Tuple of objects that define the literal values for the enum,
               where each value will be converted to a valid attribute name
            2. Dict of string keys to values, where the keys are used as
               attribute names
        include_imports: If True, includes necessary imports for Literal and
            LiteralEnum (default: True)
        class_name: The name of the generated class (default:
            'GeneratedEnum')
        print_to_stdout: If True, prints the generated code to stdout
            (default: True)

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


        class GeneratedEnum(LiteralEnum):
            Literals = Literal['active', 'inactive', 'pending']
            ACTIVE: Literal['active'] = 'active'
            INACTIVE: Literal['inactive'] = 'inactive'
            PENDING: Literal['pending'] = 'pending'
    """
    if not values:
        raise ValueError('At least one value must be provided')

    if not is_unreserved_identifier(class_name):
        raise ValueError(f'"{class_name}" is not a valid Python class name')

    # Generate attribute names from values, handling duplicates
    enum_mappings: dict[str, object] = {}

    match values:
        case dict() | MappingProxyType():
            for key, value in values.items():
                enum_mappings[key] = value.value if isinstance(value, Enum) else value
        case tuple():
            for value in values:
                # Convert value to a valid attribute name
                attr_name = _generate_attribute_name(value, enum_mappings.keys())
                enum_mappings[attr_name] = value

    # Build the class code. First. we need to check if we need to include imports
    if include_imports:
        lines = [
            'from typing import Literal',
            'from omnipy.util.literal_enum import LiteralEnum',
            '',
            ''
        ]
    else:
        lines = []

    # Build the literals string
    literals_str = ', '.join(repr(value) for value in enum_mappings.values())

    # Add class definition
    lines += [f'class {class_name}(LiteralEnum):', f'    Literals = Literal[{literals_str}]', '']

    # Add attribute definitions
    for attr_name, value in enum_mappings.items():
        lines.append(f'    {attr_name}: Literal[{repr(value)}] = {repr(value)}')

    code = '\n'.join(lines)
    if print_to_stdout:
        print(code)
    else:
        return code


def _generate_attribute_name(value: Any, used_names: KeysView[str]) -> str:
    """
    Generate a valid Python attribute name from a value.

    Args:
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
