from typing import get_args, Literal

import pytest

from omnipy.util.literal_enum import LiteralEnum


def test_basic_creation() -> None:
    class Status(LiteralEnum):
        Literals = Literal['active', 'inactive']
        ACTIVE: Literal['active'] = 'active'
        INACTIVE: Literal['inactive'] = 'inactive'

    assert Status.ACTIVE == 'active'
    assert Status.INACTIVE == 'inactive'
    assert get_args(Status.Literals) == ('active', 'inactive')


def test_creation_boolean_values() -> None:
    class BoolChoice(LiteralEnum):
        Literals = Literal[True, False]
        YES: Literal[True] = True
        NO: Literal[False] = False

    assert BoolChoice.YES is True
    assert BoolChoice.NO is False

    class BoolChoiceSpecialized(LiteralEnum[bool]):
        Literals = Literal[True, False]
        YES: Literal[True] = True
        NO: Literal[False] = False

    assert BoolChoiceSpecialized.YES is True
    assert BoolChoiceSpecialized.NO is False


def test_creation_numeric_values() -> None:
    class Priority(LiteralEnum):
        Literals = Literal[1, 2, 3]
        LOW: Literal[1] = 1
        MEDIUM: Literal[2] = 2
        HIGH: Literal[3] = 3

    assert Priority.LOW == 1
    assert Priority.HIGH == 3

    class PrioritySpecialized(LiteralEnum[int]):
        Literals = Literal[1, 2, 3]
        LOW: Literal[1] = 1
        MEDIUM: Literal[2] = 2
        HIGH: Literal[3] = 3

    assert PrioritySpecialized.LOW == 1
    assert PrioritySpecialized.HIGH == 3


def test_creation_mixed_type_values() -> None:
    class Mixed(LiteralEnum):
        Literals = Literal['text', 42, True]
        TEXT: Literal['text'] = 'text'
        NUMBER: Literal[42] = 42
        BOOL: Literal[True] = True

    assert Mixed.TEXT == 'text'
    assert Mixed.NUMBER == 42
    assert Mixed.BOOL is True

    class MixedSpecialized(LiteralEnum[str | int | bool]):
        Literals = Literal['text', 42, True]
        TEXT: Literal['text'] = 'text'
        NUMBER: Literal[42] = 42
        BOOL: Literal[True] = True

    assert MixedSpecialized.TEXT == 'text'
    assert MixedSpecialized.NUMBER == 42
    assert MixedSpecialized.BOOL is True


def test_basic_inheritance() -> None:
    class BaseChoices(LiteralEnum):
        Literals = Literal['yes', 'no']
        YES: Literal['yes'] = 'yes'
        NO: Literal['no'] = 'no'

    class ExtendedChoices(LiteralEnum):
        Literals = Literal['maybe']
        MAYBE: Literal['maybe'] = 'maybe'

    class AllChoices(BaseChoices, ExtendedChoices):
        Literals = Literal[BaseChoices.Literals, ExtendedChoices.Literals]

    # Check that all attributes are inherited
    assert AllChoices.YES == 'yes'
    assert AllChoices.NO == 'no'
    assert AllChoices.MAYBE == 'maybe'
    assert get_args(AllChoices.Literals) == ('yes', 'no', 'maybe')


def test_missing_literals_attribute() -> None:
    with pytest.raises(TypeError, match='must define a Literals property'):

        class BadEnum(LiteralEnum):
            SOME_VALUE = 'value'


def test_literals_not_literal_type() -> None:
    with pytest.raises(AssertionError, match='must be defined as a Literal type'):

        class BadEnum(LiteralEnum):
            Literals = str  # Not a Literal type
            VALUE = 'value'


def test_attribute_not_in_literals() -> None:
    with pytest.raises(TypeError, match='is not defined in'):

        class BadEnum(LiteralEnum):
            Literals = Literal['valid']
            VALID: Literal['valid'] = 'valid'
            INVALID: Literal['invalid'] = 'invalid'  # Not in Literals


def test_missing_attribute_definition() -> None:
    with pytest.raises(TypeError, match='Not all choices.*are defined as members'):

        class BadEnum(LiteralEnum):
            Literals = Literal['one', 'two', 'three']
            ONE: Literal['one'] = 'one'
            TWO: Literal['two'] = 'two'
            # Missing THREE


def test_literals_not_in_line_with_specialization() -> None:
    with pytest.raises(TypeError, match=r'Literal values do not match the specialization'):

        class BadEnum(LiteralEnum[str | bool]):
            Literals = Literal['Text', 123, True, None]
            TEXT: Literal['Text'] = 'Text'
            NUMBER_123: Literal[123] = 123
            TRUE: Literal[True] = True
            NONE: Literal[None] = None


def test_not_uppercase_attribute_name() -> None:
    with pytest.raises(AssertionError, match='must be an uppercase attribute name'):

        class BadEnum(LiteralEnum):
            Literals = Literal['value']
            value: Literal['value'] = 'value'  # Not uppercase


def test_name_check_works_with_reserved_names() -> None:
    with pytest.raises(AssertionError, match='must be an uppercase attribute name'):

        class BadEnum(LiteralEnum):
            Literals = Literal['names', 'name_for_value']
            names: Literal['names'] = 'names'  # type: ignore[assignment]
            name_for_value: Literal['name_for_value'] = 'name_for_value'  # type: ignore[assignment]


def test_attribute_lacking_annotation() -> None:
    with pytest.raises(AssertionError, match='must be annotated as a Literal type'):

        class BadEnum(LiteralEnum):
            Literals = Literal['value']
            VALUE = 'value'  # Lacking annotation


def test_attribute_wrong_annotation() -> None:
    with pytest.raises(AssertionError, match='must be annotated as a Literal type'):

        class BadEnum(LiteralEnum):
            Literals = Literal['value']
            VALUE: str = 'value'  # Wrong annotation type


def test_attribute_incorrect_literal() -> None:
    with pytest.raises(AssertionError, match='value of the Literal annotation must match'):

        class BadEnum(LiteralEnum):
            Literals = Literal['value']
            VALUE: Literal['different'] = 'value'  # type: ignore[assignment]


def test_attribute_too_many_literal_values() -> None:
    with pytest.raises(AssertionError, match='value of the Literal annotation must match'):

        class BadEnum(LiteralEnum):
            Literals = Literal['value']
            VALUE: Literal['value', 'other'] = 'value'


def test_attribute_value_mismatch() -> None:
    with pytest.raises(TypeError, match='is not defined in'):

        class BadEnum(LiteralEnum):
            Literals = Literal['expected']
            VALUE: Literal['different'] = 'different'


def test_empty_literals() -> None:
    # This should work but be practically useless
    class EmptyEnum(LiteralEnum):
        Literals = Literal[()]  # type: ignore[valid-type]

    # Should have no members except Literals
    assert hasattr(EmptyEnum, 'Literals')


def test_single_value_enum() -> None:
    class SingleEnum(LiteralEnum):
        Literals = Literal['only']
        ONLY: Literal['only'] = 'only'

    assert SingleEnum.ONLY == 'only'
    assert get_args(SingleEnum.Literals) == ('only',)


def test_duplicate_values_different_names() -> None:
    # This should work - same value with different attribute names
    class DuplicateEnum(LiteralEnum):
        Literals = Literal['same', 'same']
        FIRST: Literal['same'] = 'same'
        SECOND: Literal['same'] = 'same'

    assert DuplicateEnum.FIRST == DuplicateEnum.SECOND == 'same'


def test_private_attributes_ignored() -> None:
    class WithPrivate(LiteralEnum):
        Literals = Literal['public']
        PUBLIC: Literal['public'] = 'public'
        _private = 'ignored'
        __dunder__ = 'also ignored'

    assert WithPrivate.PUBLIC == 'public'
    assert WithPrivate._private == 'ignored'
    assert WithPrivate.__dunder__ == 'also ignored'


def test_name_of_value() -> None:
    class NumberEnum(LiteralEnum):
        Literals = Literal['one', 'two']
        ONE: Literal['one'] = 'one'
        TWO: Literal['two'] = 'two'

    assert NumberEnum.name_for_value('one') == 'ONE'
    assert NumberEnum.name_for_value('two') == 'TWO'

    with pytest.raises(ValueError, match="Value 'three' not found in NumberEnum"):
        NumberEnum.name_for_value('three')

    with pytest.raises(ValueError, match='Value 3 not found in NumberEnum'):
        NumberEnum.name_for_value(3)

    # Specialized version with type hinting allows type checking for name_for_value()
    class NumberEnumSpecialized(LiteralEnum[str]):
        Literals = Literal['one', 'two']
        ONE: Literal['one'] = 'one'
        TWO: Literal['two'] = 'two'

    with pytest.raises(ValueError, match='Value 3 not found in NumberEnum'):
        NumberEnumSpecialized.name_for_value(3)  # type: ignore[arg-type]


def test_contains() -> None:
    class ColorEnum(LiteralEnum):
        Literals = Literal['red', 'green', 'blue']
        RED: Literal['red'] = 'red'
        GREEN: Literal['green'] = 'green'
        BLUE: Literal['blue'] = 'blue'

    assert 'red' in ColorEnum
    assert 'green' in ColorEnum
    assert 'blue' in ColorEnum
    assert 'yellow' not in ColorEnum
    assert None not in ColorEnum

    class ColorEnumSpecialized(LiteralEnum[str | int]):
        Literals = Literal['red', 'green', 'blue']
        RED: Literal['red'] = 'red'
        GREEN: Literal['green'] = 'green'
        BLUE: Literal['blue'] = 'blue'

    assert 'red' in ColorEnumSpecialized
    assert 'green' in ColorEnumSpecialized
    assert 'blue' in ColorEnumSpecialized
    assert 'yellow' not in ColorEnumSpecialized

    # Type narrowing according to specialization works correctly
    assert None not in ColorEnumSpecialized  # type: ignore[operator]

    assert 'RED' in ColorEnum.names()
    assert 'GREEN' in ColorEnum.names()
    assert 'BLUE' in ColorEnum.names()
    assert 'YELLOW' not in ColorEnum.names()


def test_iteration() -> None:
    class SimpleEnum(LiteralEnum):
        Literals = Literal['one', 'two', 'three']
        ONE: Literal['one'] = 'one'
        TWO: Literal['two'] = 'two'
        THREE: Literal['three'] = 'three'

    assert [name for name in SimpleEnum.names()] == ['ONE', 'TWO', 'THREE']

    # Only type narrowing to general LiteralEnumInnerTypes
    for value in SimpleEnum:
        value.capitalize()  # type: ignore[union-attr]

    class SimpleEnumSpecialized(LiteralEnum[str]):
        Literals = Literal['one', 'two', 'three']
        ONE: Literal['one'] = 'one'
        TWO: Literal['two'] = 'two'
        THREE: Literal['three'] = 'three'

    # Type narrowing according to specialization works correctly
    for value in SimpleEnumSpecialized:
        value.capitalize()


def test_random_choice() -> None:
    class RandomEnum(LiteralEnum):
        Literals = Literal['apple', 'banana', 'cherry']
        APPLE: Literal['apple'] = 'apple'
        BANANA: Literal['banana'] = 'banana'
        CHERRY: Literal['cherry'] = 'cherry'

    choice = RandomEnum.random_choice()
    assert choice in RandomEnum

    class RandomEnumSpecialized(LiteralEnum[str]):
        Literals = Literal['apple', 'banana', 'cherry']
        APPLE: Literal['apple'] = 'apple'
        BANANA: Literal['banana'] = 'banana'
        CHERRY: Literal['cherry'] = 'cherry'

    choice_specialized = RandomEnumSpecialized.random_choice()
    assert choice_specialized in RandomEnumSpecialized


def test_random_choice_no_excluded_prefixes() -> None:
    class RandomEnum(LiteralEnum):
        Literals = Literal['apple', 'auto', 'random-fruit']
        APPLE: Literal['apple'] = 'apple'
        AUTO: Literal['auto'] = 'auto'
        RANDOM_FRUIT: Literal['random-fruit'] = 'random-fruit'

    for _ in range(30):
        choice = RandomEnum.random_choice()
        assert choice == RandomEnum.APPLE
