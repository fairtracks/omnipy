from typing import get_args, Literal

import pytest
from typing_extensions import assert_never, TypeIs

from omnipy.util.literal_enum import LiteralEnum


class ClearBoolChoices(LiteralEnum):
    Literals = Literal[True, False]

    POSITIVE: Literal[True] = True
    """
    Documentation for the positive choice.
    """

    NEGATIVE: Literal[False] = False
    """
    Documentation for the negative choice.
    """


def test_docs_clear_choices_example() -> None:
    def i_need_a_clear_choice(choice: ClearBoolChoices.Literals) -> str:
        match choice:
            case ClearBoolChoices.POSITIVE:
                return 'You chose a positive response'
            case ClearBoolChoices.NEGATIVE:
                return 'You chose a negative response'

    # All following calls will work at runtime, but with different static type checking results:
    response = i_need_a_clear_choice(ClearBoolChoices.POSITIVE)  # Will pass static type checking
    assert response == 'You chose a positive response'

    response = i_need_a_clear_choice(False)  # Unlike Enums, passing the value also works
    assert response == 'You chose a negative response'

    response = i_need_a_clear_choice('maybe')  # type: ignore[arg-type]
    assert response is None


class ClearStrChoices(LiteralEnum):
    Literals = Literal['yes', 'no']
    POSITIVE: Literal['yes'] = 'yes'
    NEGATIVE: Literal['no'] = 'no'


class UnclearStrChoices(LiteralEnum):
    Literals = Literal['maybe', 'possibly']
    MAYBE: Literal['maybe'] = 'maybe'
    POSSIBLY: Literal['possibly'] = 'possibly'


class AllStrChoices(ClearStrChoices, UnclearStrChoices):
    Literals = Literal[ClearStrChoices.Literals, UnclearStrChoices.Literals]


def test_docs_multiple_inheritance_example() -> None:
    assert AllStrChoices.POSITIVE == 'yes'
    assert AllStrChoices.MAYBE == 'maybe'
    assert set(get_args(AllStrChoices.Literals)) == {'yes', 'no', 'maybe', 'possibly'}


def test_docs_type_narrowing_exhaustiveness_check_with_return() -> None:
    def is_unclear_choice(choice: AllStrChoices.Literals) -> TypeIs[UnclearStrChoices.Literals]:
        return choice in get_args(UnclearStrChoices.Literals)

    # This will produce a static type error on the return value, as we forgot to handle the
    # case of AllStrChoices.NEGATIVE
    def most_choices_are_ok(choice: AllStrChoices.Literals) -> str:  # type: ignore[return-value]
        match choice:
            case AllStrChoices.POSITIVE:
                return 'You chose yes'
            case x if is_unclear_choice(x):
                return f'You chose an unclear option: {x}'

    # Still no runtime checks
    response = most_choices_are_ok('maybe')  # No static type checking errors
    assert response == 'You chose an unclear option: maybe'

    response = most_choices_are_ok('whatever')  # type: ignore[arg-type]
    assert response is None


def test_docs_type_narrowing_exhaustiveness_check_with_assert_never() -> None:
    def is_unclear_choice(choice: AllStrChoices.Literals) -> TypeIs[UnclearStrChoices.Literals]:
        return choice in get_args(UnclearStrChoices.Literals)

    def most_choices_are_still_ok(choice: AllStrChoices.Literals) -> None:
        match choice:
            case AllStrChoices.POSITIVE:
                print('You chose yes')
            case x if is_unclear_choice(x):
                print(f'You chose an unclear option: {x}')
            case _ as never:
                assert_never(never)  # type: ignore[arg-type]

    # The following call will fail both at static type checking and at runtime
    with pytest.raises(AssertionError, match='Expected code to be unreachable'):
        most_choices_are_still_ok('whatever')  # type: ignore[arg-type]
