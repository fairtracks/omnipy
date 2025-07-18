from enum import Enum
from typing import get_args

import pytest

from omnipy.util.literal_enum import LiteralEnum
from omnipy.util.literal_enum_generator import generate_literal_enum_code


def test_generate_literal_enum_code_basic_tuple() -> None:
    """Test basic code generation with simple string values."""
    code = generate_literal_enum_code(('active', 'inactive', 'pending'))

    expected_lines = [
        'from typing import Literal',
        'from omnipy.util.literal_enum import LiteralEnum',
        '',
        '',
        'class NewLiteralEnum(LiteralEnum[str]):',
        "    Literals = Literal['active', 'inactive', 'pending']",
        '',
        "    ACTIVE: Literal['active'] = 'active'",
        "    INACTIVE: Literal['inactive'] = 'inactive'",
        "    PENDING: Literal['pending'] = 'pending'"
    ]

    assert code == '\n'.join(expected_lines)


def test_generate_literal_enum_code_basic_tuple_no_imports() -> None:
    """Test basic code generation with simple string values."""
    code = generate_literal_enum_code(
        ('active', 'inactive', 'pending'),
        include_imports=False,
    )

    expected_lines = [
        'class NewLiteralEnum(LiteralEnum[str]):',
        "    Literals = Literal['active', 'inactive', 'pending']",
        '',
        "    ACTIVE: Literal['active'] = 'active'",
        "    INACTIVE: Literal['inactive'] = 'inactive'",
        "    PENDING: Literal['pending'] = 'pending'"
    ]

    assert code == '\n'.join(expected_lines)


def test_generate_literal_enum_code_basic_tuple_with_docstrings() -> None:
    """Test basic code generation with simple string values."""
    code = generate_literal_enum_code(
        ('active', 'inactive', 'pending'),
        docstrings={
            'active': ('This is an active state',),
            'inactive': ('This is an inactive state. This docstring is longer than the others, '
                         'and more than 74 characters long.',
                         'Here is a second paragraph.'),
        },
        include_imports=False,
    )

    expected_lines = [
        'class NewLiteralEnum(LiteralEnum[str]):',
        "    Literals = Literal['active', 'inactive', 'pending']",
        '',
        "    ACTIVE: Literal['active'] = 'active'",
        '    """',
        '    This is an active state',
        '    """',
        '',
        "    INACTIVE: Literal['inactive'] = 'inactive'",
        '    """',
        '    This is an inactive state. This docstring is longer than the others, and',
        '    more than 74 characters long.',
        '',
        '    Here is a second paragraph.',
        '    """',
        '',
        "    PENDING: Literal['pending'] = 'pending'",
    ]

    assert code == '\n'.join(expected_lines)


def test_generate_literal_enum_code_basic_dict() -> None:
    """Test basic code generation with simple dict values."""
    code = generate_literal_enum_code({'YES': True, 'NO': False})

    expected_lines = [
        'from typing import Literal',
        'from omnipy.util.literal_enum import LiteralEnum',
        '',
        '',
        'class NewLiteralEnum(LiteralEnum[bool]):',
        '    Literals = Literal[True, False]',
        '',
        '    YES: Literal[True] = True',
        '    NO: Literal[False] = False',
    ]

    assert code == '\n'.join(expected_lines)


def test_generate_literal_enum_from_other_enum_mapping() -> None:
    """Test basic code generation with simple dict values."""
    class MyEnum(Enum):
        YES = True
        NO = False

    code = generate_literal_enum_code(MyEnum.__members__)  # type: ignore[arg-type]

    expected_lines = [
        'from typing import Literal',
        'from omnipy.util.literal_enum import LiteralEnum',
        '',
        '',
        'class NewLiteralEnum(LiteralEnum[bool]):',
        '    Literals = Literal[True, False]',
        '',
        '    YES: Literal[True] = True',
        '    NO: Literal[False] = False',
    ]

    assert code == '\n'.join(expected_lines)


def test_generate_literal_enum_code_custom_class_name() -> None:
    """Test code generation with custom class name."""
    code = generate_literal_enum_code(
        (True, False),
        class_name='YesNoChoice',
    )

    assert 'class YesNoChoice(LiteralEnum[bool]):' in code
    assert 'Literals = Literal[True, False]' in code
    assert 'TRUE: Literal[True] = True' in code
    assert 'FALSE: Literal[False] = False' in code


def test_generate_literal_enum_code_single_value() -> None:
    """Test code generation with a single value."""
    code = generate_literal_enum_code(('only',))

    assert "Literals = Literal['only']" in code
    assert "ONLY: Literal['only'] = 'only'" in code


def test_generate_literal_enum_code_special_characters() -> None:
    """Test code generation with values containing special characters."""
    code = generate_literal_enum_code(('hello-world', 'foo.bar', 'test@example'))

    # Check that special characters are handled in attribute names
    assert 'HELLO_WORLD:' in code
    assert 'FOO_BAR:' in code
    assert 'TEST_EXAMPLE:' in code

    # Check that original values are preserved in literals
    assert "'hello-world'" in code
    assert "'foo.bar'" in code
    assert "'test@example'" in code


def test_generate_literal_enum_code_numbers_and_numeric_strings() -> None:
    """Test code generation with numeric string values."""
    code = generate_literal_enum_code((123, '456'))

    assert 'LiteralEnum[int | str]' in code

    # Numerics should get NUMBER_ prefix for attribute names
    assert 'NUMBER_123:' in code
    assert 'NUMBER_456:' in code
    assert '123' in code
    assert "'456'" in code


def test_generate_literal_enum_code_empty() -> None:
    """Test code generation with empty strings and whitespace."""
    code = generate_literal_enum_code(('', ''))

    assert 'LiteralEnum[str]' in code

    # Empty strings should get EMPTY attribute names
    assert 'EMPTY:' in code
    assert 'EMPTY_2' in code

    # Original values should be preserved
    assert "''" in code


def test_generate_literal_enum_code_whitespace() -> None:
    """Test code generation with empty strings and whitespace."""
    code = generate_literal_enum_code(('   ', '\t\n'))

    assert 'LiteralEnum[str]' in code

    # Whitespace-only strings should get WHITESPACE attribute names
    assert 'WHITESPACE:' in code
    assert 'WHITESPACE_2:' in code  # Handle conflicts

    # Original values should be preserved
    assert "'   '" in code
    assert "'\\t\\n'" in code


def test_generate_literal_enum_code_duplicate_values() -> None:
    """Test code generation with duplicate values."""
    code = generate_literal_enum_code(('same', 'same', 'different'))

    # Should handle duplicates by creating unique attribute names
    assert 'SAME:' in code
    assert 'SAME_2:' in code  # Some conflict resolution
    assert 'DIFFERENT:' in code

    # All values should appear in Literals
    assert "Literal['same', 'same', 'different']" in code


def test_generate_literal_enum_code_keywords() -> None:
    """Test code generation with Python keywords as values."""
    code = generate_literal_enum_code(('class', 'def', 'if'))

    assert 'CLASS:' in code
    assert 'DEF:' in code
    assert 'IF:' in code

    # Original values preserved
    assert "'class'" in code
    assert "'def'" in code
    assert "'if'" in code


def test_generate_literal_enum_code_mixed_cases() -> None:
    """Test code generation with mixed case values."""
    code = generate_literal_enum_code(('CamelCase', 'snake_case', 'UPPER_CASE'))

    # All should be converted to uppercase for attribute names
    assert 'CAMEL_CASE:' in code
    assert 'SNAKE_CASE:' in code
    assert 'UPPER_CASE:' in code


def test_error_generate_literal_enum_code_empty_values_error() -> None:
    """Test that empty tuple raises ValueError."""
    with pytest.raises(ValueError, match='At least one value must be provided'):
        generate_literal_enum_code(())


def test_error_generate_literal_enum_code_unmatching_docstrings() -> None:
    """Test that invalid class names raise ValueError."""
    with pytest.raises(ValueError, match="Docstring for 'maybe' does not match any value"):
        generate_literal_enum_code(
            ('yes', 'no'),
            docstrings={'maybe': ('This is an irrelevant docstring',)},
        )


def test_error_generate_literal_enum_code_invalid_class_name() -> None:
    """Test that invalid class names raise ValueError."""
    with pytest.raises(ValueError, match='is not a valid Python class name'):
        generate_literal_enum_code(
            ('value',),
            class_name='123InvalidName',
        )

    with pytest.raises(ValueError, match='is not a valid Python class name'):
        generate_literal_enum_code(
            ('value',),
            class_name='class',
        )  # keyword


def test_error_generate_literal_enum_code_invalid_value_type() -> None:
    """Test that invalid class names raise ValueError."""
    with pytest.raises(ValueError, match='Unsupported value type: dict'):
        generate_literal_enum_code(({1: 2},),)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match='is not a valid Python class name'):
        generate_literal_enum_code(
            ('value',),
            class_name='class',
        )  # keyword


def test_generate_literal_enum_code_generated_class_works() -> None:
    """Test that the generated code actually creates a working LiteralEnum."""
    code = generate_literal_enum_code(('active', 'inactive'), class_name='StatusEnum')

    # Execute the generated code
    namespace: dict[str, type[LiteralEnum]] = {}
    exec(code, namespace)

    # Get the generated class
    StatusEnum = namespace['StatusEnum']

    # Test that it works like a proper LiteralEnum
    assert StatusEnum.ACTIVE == 'active'  # type: ignore[attr-defined]
    assert StatusEnum.INACTIVE == 'inactive'  # type: ignore[attr-defined]
    assert get_args(StatusEnum.Literals) == ('active', 'inactive')

    # Test that it's actually a LiteralEnum subclass
    assert issubclass(StatusEnum, LiteralEnum)


def test_generate_literal_enum_code_complex_example() -> None:
    """Test code generation with a complex real-world example."""
    values = ('pending-approval', 'in-progress', 'completed', 'failed', 'cancelled')
    code = generate_literal_enum_code(values, class_name='TaskStatus')

    # Execute and test the generated code
    namespace: dict[str, type[LiteralEnum]] = {}
    exec(code, namespace)
    TaskStatus = namespace['TaskStatus']

    # Check all values are accessible
    assert TaskStatus.PENDING_APPROVAL == 'pending-approval'  # type: ignore[attr-defined]
    assert TaskStatus.IN_PROGRESS == 'in-progress'  # type: ignore[attr-defined]
    assert TaskStatus.COMPLETED == 'completed'  # type: ignore[attr-defined]
    assert TaskStatus.FAILED == 'failed'  # type: ignore[attr-defined]
    assert TaskStatus.CANCELLED == 'cancelled'  # type: ignore[attr-defined]

    # Check Literals type
    expected_literals = ('pending-approval', 'in-progress', 'completed', 'failed', 'cancelled')
    assert get_args(TaskStatus.Literals) == expected_literals
