from typing import ClassVar, get_args, get_type_hints

from omnipy.util.helpers import is_literal_type


class LiteralEnum:
    """
    A base class for creating enums with defined literal choices, with support from the main
    static type checkers (tested with `mypy` and `pyright`). Unlike standard Enums, LiteralEnum
    supports multiple inheritance and the use the enum attribute names and underlying values
    directly in type hints and function signatures. At the same time, LiteralEnum maintains the
    main benefits of traditional Enum types: a clearly defined and namespaced set of choices with
    possibilities for flexible naming and per-item documentation.

    Subclasses must define a `Literals` class attribute that specify the valid choices as a Literal
    type. Each choice must also be defined as a separate class attribute with a Literal type.
    The LiteralEnum superclass will ensure that all choices are defined according to these rules.

    Example LiteralEnum:

    ```python
    from typing import Literal

    class ClearBoolChoices(LiteralEnum):
        Literals = Literal[True, False]

        POSITIVE: Literal[True] = True
        \"\"\"
        Documentation for the positive choice.
        \"\"\"

        NEGATIVE: Literal[False] = False
        \"\"\"
        Documentation for the negative choice.
        \"\"\"
    ```

    Example usage:

    ```python
    def i_need_a_clear_choice(choice: ClearBoolChoices.Literals) -> str:
        match choice:
            case ClearBoolChoices.POSITIVE:
                return "You chose a positive response"
            case ClearBoolChoices.NEGATIVE:
                return "You chose a negative response"



    # All following calls will work at runtime, but with different static type checking results:
    response = i_need_a_clear_choice(ClearBoolChoices.POSITIVE)  # Will pass static type checking
    assert response == "You chose a positive response"

    response = i_need_a_clear_choice(False)  # Unlike Enums, passing the value also works
    assert response == "You chose a negative response"

    response = i_need_a_clear_choice('maybe')  # This will raise an error in static type checking
    assert response is None
    ```

    LiteralEnum supports multiple inheritance, allowing you to combine different sets of choices
    into a single enum, e.g.:

    ```python
    class UnclearStrChoices(LiteralEnum):
        Literals = Literal['maybe', 'possibly']
        MAYBE: Literal['maybe'] = 'maybe'
        POSSIBLY: Literal['possibly'] = 'possibly'

    class AllStrChoices(ClearStrChoices, UnclearStrChoices):
        Literals = Literal[ClearStrChoices.Literals, UnclearStrChoices.Literals]
    ```

    The `AllStrChoices` enum will have all the choices from both `ClearStrChoices` and
    `UnclearStrChoices`. The `Literals` type of `AllStrChoices` will be a union of the literals from
    both enums, allowing for flexible type checking and usage in function signatures.

    When there are many enum values, you can avoid manually specifying all the choices by making
    use of a type narrowing function. As a bonus, `mypy` (as of v1.16.1) supports exhaustiveness
    checking for `TypeIs` narrowing in the same way as with explicit pattern matching.

    Example:

    ```python
    # For Python versions < 3.13
    from typing_extensions import TypeIs

    # Otherwise, use the built-in versions:
    from typing import TypeIs

    # In any case:
    from typing import get_args

    def is_unclear_choice(choice: AllStrChoices.Literals) -> TypeIs[UnclearStrChoices.Literals]:
        \"\"\"
        A type narrowing function that checks if the choice is a member of UnclearStrChoices.
        The `TypeIs` return type narrows the type of choice to `UnclearStrChoices.Literals` if the
        check succeeds. Otherwise, the type of choice is negatively narrowed to the remaining
        choices in `AllStrChoices.Literals`.
        \"\"\"
        return choice in get_args(UnclearStrChoices.Literals)

    # This will produce a static type error on the return value, as we forgot to handle the
    # case of AllStrChoices.NEGATIVE
    def most_choices_are_ok(choice: AllStrChoices.Literals) -> str:
        match choice:
            case AllStrChoices.POSITIVE:
                return "You chose yes"
            case x if is_unclear_choice(x):
                return f"You chose an unclear option: {x}"

    # Still no runtime checks
    response = most_choices_are_ok('maybe')  # No static type checking errors
    assert response == "You chose an unclear option: maybe"

    response = most_choices_are_ok('whatever')  # Static type checking error here
    assert response is None
    ```
    Note: pyright (as of v1.1.402) does not support `TypeIs` narrowing of exhaustiveness checks:

        https://github.com/microsoft/pyright/issues/10680

    In contrast to `i_need_a_clear_choice()`, the `most_choices_are_ok()` function also
    checks the provided value at runtime. This is due to the use of the `assert_never()` function:

    For runtime checks, there are several options:

    One is to make use of the new `assert_never()` function, which also provides exhaustiveness
    checks when there are no return values:

    ```python
    # For Python versions < 3.11
    from typing_extensions import assert_never
    # Otherwise, use the built-in versions:
    from typing import assert_never

    def most_choices_are_still_ok(choice: AllStrChoices.Literals) -> None:
        match choice:
            case AllStrChoices.POSITIVE:
                print("You chose yes")
            case x if is_unclear_choice(x):
                print(f"You chose an unclear option: {x}")
            case _ as never:
                assert_never(never)  # This will raise an error if the case is not handled

    # The following call will fail both at static type checking and at runtime
    response = most_choices_are_still_ok('whatever')
    ```

    ```
    assert response is None
    one can also use e.g. pydantic to validate (and transform) the input:

    ```python
    class MyModel(BaseModel):
        clear: ClearBoolChoices.Literals
        confused: AllStrChoices.Literals
    ```

    As with `i_need_a_clear_choice()`, any combination of matching enum attributes and values will
    work at runtime and for static type checking:

    ```pycon
    >>> abc = MyModel(clear=True is False, confused=AllStrChoices.MAYBE)
    >>> abc
    MyModel(clear=False, confused='maybe')
    ```

    Incorrect values will fail static type checking and (in contrast to `i_need_a_clear_choice()`)
    also raise a validation error at runtime:

    ```pycon
    >>> abc = MyModel(clear=ClearBoolChoices.POSITIVE, confused='whatever')
    (…)
    confused
      unexpected value; permitted: 'yes', 'no', 'maybe', 'possibly' (…)
    ```
    """

    Literals: ClassVar
    """
    A class variable  that specify the valid choices as a Literal type. Each choice must also be
    defined as a separate class attribute with a Literal type.
    """
    def __init_subclass__(cls):
        """
        This method is called when a subclass of LiteralEnum is created. It makes sure all
        values of the `Literals` class variable are also defined as members of the subclass. The
        method also checks that the types of the class attributes correctly defined.
        """
        if not hasattr(cls, 'Literals'):
            raise TypeError(f'{cls.__name__} must define a Literals property.')

        assert is_literal_type(cls.Literals), \
            f'{cls.__name__}.Literals must be defined as a Literal type.'

        all_literals = set(get_args(cls.Literals))
        cls_type_hints = get_type_hints(cls)
        defined_attrs = set()

        # Check that all attributes are defined as Literal types and match the `Literals` attribute
        for attr in dir(cls):
            val = getattr(cls, attr)
            if not attr.startswith('_') and not is_literal_type(val):
                assert attr in cls_type_hints and is_literal_type(cls_type_hints[attr]), \
                    f'{cls.__name__}.{attr} must be annotated as a Literal type.'
                if val not in all_literals:
                    raise TypeError(f'{val} is not defined in {cls.Literals}.')
                defined_attrs.add(val)

        literal_missing_attrs = all_literals - defined_attrs
        if literal_missing_attrs:
            raise TypeError(f'Not all choices in {cls.__name__}.Literals are defined as members .'
                            f'Missing members: {literal_missing_attrs}')
