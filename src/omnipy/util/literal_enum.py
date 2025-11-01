import random
from typing import Any, cast, ClassVar, Generic, get_args, get_type_hints, Iterator, overload

from typing_extensions import TypeVar

from omnipy.shared.typedefs import TypeForm
from omnipy.util.helpers import all_type_variants, is_literal_type

LiteralEnumInnerTypes = bool | str | int | bytes | None  # Types that can be used in LiteralEnum

LiteralInnerTypeT = TypeVar('LiteralInnerTypeT', bound=LiteralEnumInnerTypes)


class LiteralEnumMeta(type):
    """
    A metaclass for LiteralEnum that contains the logic for iteration.
    """
    @overload
    def __iter__(  # type: ignore[misc]
        self: 'type[LiteralEnum[LiteralEnumInnerTypes]]'  # Match generic LiteralEnum subtypes
    ) -> Iterator[LiteralEnumInnerTypes]:
        ...

    @overload
    def __iter__(  # type: ignore[misc]
        self: 'type[LiteralEnum[LiteralInnerTypeT]]'  # Match specialized LiteralEnum subtypes
    ) -> Iterator[LiteralInnerTypeT]:
        ...

    def __iter__(self) -> Iterator[LiteralEnumInnerTypes]:
        """
        Iterate over the enum values. Narrows the type according to the
        specialization to specific Literal inner types

        Returns:
            An typed iterator over the enum values.
        """
        return iter(get_args(cast(LiteralEnum, self).Literals))


class LiteralEnum(Generic[LiteralInnerTypeT], metaclass=LiteralEnumMeta):
    """
    Base class for creating enums with defined literal choices, with support
    from the main static type checkers (tested with `mypy` and `pyright`).
    Unlike standard Enums, LiteralEnum supports multiple inheritance and the
    use the enum attribute names and underlying values directly in type
    hints and function signatures. At the same time, LiteralEnum maintains
    the main benefits of traditional Enum types: a clearly defined and
    namespaced set of choices with possibilities for flexible naming and
    per-item documentation.

    Subclasses must define a `Literals` class attribute that specify the
    valid choices as a Literal type. Each choice must also be defined as a
    separate class attribute with a Literal type. The LiteralEnum superclass
    will ensure that all choices are defined according to these rules.

    Example LiteralEnum:

    ```python
    from typing import Literal
    from omnipy import LiteralEnum

    class ClearBoolChoices(LiteralEnum[bool]):
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

    Specializing the `LiteralEnum` class with a specific inner type allows
    for more precise type checking for iteration and other methods. If no
    specialization is provided, the default inner types are defined as:

    `LiteralEnumInnerTypes = `bool | str | int | bytes | None`

    Example usage in a function signature:

    ```python
    def i_need_a_clear_choice(choice: ClearBoolChoices.Literals) -> str:
        match choice:
            case ClearBoolChoices.POSITIVE:
                return 'You chose a positive response'
            case ClearBoolChoices.NEGATIVE:
                return 'You chose a negative response'
    ```

    All the following calls will work at runtime, but with different static
    type checking results:

    ```pycon
    >>> i_need_a_clear_choice(ClearBoolChoices.POSITIVE)  # Will pass static type checking
    'You chose a positive response'

    >>> i_need_a_clear_choice(False)  # Unlike Enums, passing the value also works
    'You chose a negative response'

    >>> response = i_need_a_clear_choice('maybe')  # This will fail static type checking
    >>> response is None
    True
    ```

    LiteralEnum supports multiple inheritance, allowing you to combine
    different sets of choices into a single enum, e.g.:

    ```python
    class ClearStrChoices(LiteralEnum[str]):
        Literals = Literal['yes', 'no']

        POSITIVE: Literal['yes'] = 'yes'
        NEGATIVE: Literal['no'] = 'no'

    class UnclearStrChoices(LiteralEnum):
        Literals = Literal['maybe', 'possibly']

        MAYBE: Literal['maybe'] = 'maybe'
        POSSIBLY: Literal['possibly'] = 'possibly'

    class AllStrChoices(ClearStrChoices, UnclearStrChoices):
        Literals = Literal[ClearStrChoices.Literals, UnclearStrChoices.Literals]
    ```

    The `AllStrChoices` enum will have all the choices from both
    `ClearStrChoices` and `UnclearStrChoices`. The `Literals` type of
    `AllStrChoices` will be a union of the literals from both enums,
    allowing for flexible type checking and usage in function signatures.

    When there are many enum values, you can avoid manually specifying all
    the choices by making use of a type narrowing function. As a bonus,
    `mypy` (as of v1.16.1) supports exhaustiveness checking for `TypeIs`
    narrowing in the same way as with explicit pattern matching.

    Example:

    ```python
    # For Python versions < 3.13
    # In any case:
    # Otherwise, use the built-in versions:
    from typing import get_args, TypeIs

    from typing_extensions import TypeIs

    def is_unclear_choice(choice: AllStrChoices.Literals) -> TypeIs[UnclearStrChoices.Literals]:
        \"\"\"
        A type narrowing function that checks if the choice is a member of UnclearStrChoices.
        The `TypeIs` return type narrows the type of choice to `UnclearStrChoices.Literals` if the
        check succeeds. Otherwise, the type of choice is negatively narrowed to the remaining
        choices in `AllStrChoices.Literals`.
        \"\"\"
        return choice in UnclearStrChoices

    # This will produce a static type error on the return value, as we forgot to handle the
    # case of AllStrChoices.NEGATIVE
    def most_choices_are_ok(choice: AllStrChoices.Literals) -> str:
        match choice:
            case AllStrChoices.POSITIVE:
                return "You chose yes"
            case x if is_unclear_choice(x):
                return f"You chose an unclear option: {x}"
    ```

    Note that there are still no runtime checks:

    ```pycon
    >>> most_choices_are_ok('maybe')  # No static type checking errors
    'You chose an unclear option: maybe'

    >>> response = most_choices_are_ok('whatever')  # Static type checking error here
    >>> response is None
    True
    ```
    Note: pyright (as of v1.1.402) does not support `TypeIs` narrowing of
    exhaustiveness checks:

        https://github.com/microsoft/pyright/issues/10680

    In contrast to `i_need_a_clear_choice()`, the `most_choices_are_ok()`
    function also checks the provided value at runtime. This is due to the
    use of the `assert_never()` function:

    For runtime checks, there are several options:

    1. Make use of the new `assert_never()` function, which also provides
    exhaustiveness checks when there are no return values:

    ```python
    # For Python versions < 3.11
    # Otherwise, use the built-in versions:
    from typing import assert_never

    from typing_extensions import assert_never

    def most_choices_are_still_ok(choice: AllStrChoices.Literals) -> None:
        match choice:
            case AllStrChoices.POSITIVE:
                print("You chose yes")
            case x if is_unclear_choice(x):
                print(f"You chose an unclear option: {x}")
            case _ as never:
                assert_never(never)  # This will raise an error if the case is not handled
    ```

    The following call will fail both at static type checking and at runtime:

    ```pycon
    >>> most_choices_are_still_ok('whatever')
    (...)
    AssertionError: Expected code to be unreachable, but got: 'whatever'
    ```

    2. Use e.g. pydantic to validate (and transform) the input:

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

    ALLOWED_LITERAL_INNER_TYPES: tuple[type, ...] = cast(
        tuple[type, ...],
        all_type_variants(LiteralEnumInnerTypes),
    )

    _RESERVED_PUBLIC_ATTRS = set(('Literals', 'ALLOWED_LITERAL_INNER_TYPES'))
    _RESERVED_PUBLIC_METHODS = set(('names', 'name_for_value'))
    _RESERVED_PUBLIC_NAMES = _RESERVED_PUBLIC_ATTRS | _RESERVED_PUBLIC_METHODS

    Literals: ClassVar
    """
    A class variable  that specify the valid choices as a Literal type. Each
    choice must also be defined as a separate class attribute with a Literal
    type.
    """
    def __init_subclass__(cls) -> None:
        """
        This method is called when a subclass of LiteralEnum is created. It
        makes sure all values of the `Literals` class variable are also
        defined as members of the subclass. The method also checks that the
        types of the class attributes correctly defined.
        """
        # Check cls.Literals
        all_cls_literal_vals = cls._check_literals_outer_type()
        cls._check_literals_inner_types_are_allowed(all_cls_literal_vals)

        # Check all defined attributes
        defined_attr_literal_vals = cls._check_attributes(all_cls_literal_vals)

        # Check that all values in cls.Literals are defined as attributes
        cls._check_missing_attributes(all_cls_literal_vals, defined_attr_literal_vals)

    @classmethod
    def _check_literals_outer_type(cls) -> set[LiteralEnumInnerTypes]:
        """
        Checks that the `Literals` class variable is defined as a Literal
        type and returns the set of all possible values defined in it.

        Returns:
            The set of all values defined in `cls.Literals`.
        """
        if not hasattr(cls, 'Literals'):
            raise TypeError(f'{cls.__name__} must define a Literals property.')

        assert is_literal_type(cls.Literals), \
            f'{cls.__name__}.Literals must be defined as a Literal type.'

        return set(get_args(cls.Literals))

    @classmethod
    def _check_literals_inner_types_are_allowed(
            cls, all_cls_literal_vals: set[LiteralEnumInnerTypes]) -> None:
        """
        Checks that all values in cls.Literals are of the allowed inner
        types. For a generic class, the checks are performed against
        LiteralEnumInnerTypes. For a specialized class, the checks are
        performed against the specialized inner types.
        """
        specialized_inner_types: tuple[type, ...] = cls._get_specialized_literal_inner_types()

        if specialized_inner_types:
            literal_inner_types = specialized_inner_types
        else:
            literal_inner_types = cls.ALLOWED_LITERAL_INNER_TYPES

        non_matching_inner_types = []

        for literal_val in all_cls_literal_vals:
            if not isinstance(literal_val, literal_inner_types):
                non_matching_inner_types.append(literal_val)

        if non_matching_inner_types:
            plurality_text = 'value does' if len(non_matching_inner_types) == 1 else 'values do'
            raise TypeError(
                f'{cls.__name__}: Literal {plurality_text} not match the specialization '
                f"({', '.join(_.__name__ for _ in specialized_inner_types)}): "
                + ', '.join(f'{_!r}' for _ in non_matching_inner_types))

    @classmethod
    def _get_specialized_literal_inner_types(cls) -> tuple[type, ...]:
        """
        Extract the specialized inner types from the Generics machinery.
        """
        bases_names = [_.__name__ for _ in cls.__orig_bases__]  # type: ignore[attr-defined]
        try:
            lit_enum_idx = bases_names.index('LiteralEnum')
            return cast(
                tuple[type, ...],
                tuple(
                    _typ for _typ in all_type_variants(
                        get_args(cls.__orig_bases__[lit_enum_idx])[0]  # type: ignore[attr-defined]
                    )))
        except ValueError:
            # Not a specialized LiteralEnum, so return an empty tuple
            return tuple()

    @classmethod
    def _check_attributes(
            cls, all_cls_literal_vals: set[LiteralEnumInnerTypes]) -> set[LiteralEnumInnerTypes]:
        """
        Checks that all public attributes are defined:
        - with an uppercase name
        - annotated as Literal types and with a matching value
        - match the inner types defined in `Literals`

        Returns:
            The set of all correctly defined attribute values
        """

        defined_attr_vals: set[LiteralEnumInnerTypes] = set()

        for member_name in dir(cls):
            member = getattr(cls, member_name)

            if cls._is_public_attr(member_name, member):
                cls._check_uppercase_attr_name(member_name)
                cls._check_attr_annotation_and_value_are_matching_literals(member_name, member)
                cls._check_attr_matches_cls_literals(all_cls_literal_vals, member)

                defined_attr_vals.add(member)

        return defined_attr_vals

    @classmethod
    def _check_uppercase_attr_name(cls, attr):
        assert attr.isupper(), f'{cls.__name__}.{attr} must be an uppercase attribute name.'

    @classmethod
    def _check_attr_annotation_and_value_are_matching_literals(
        cls,
        attr: str,
        value: Any,
    ):
        """
        Checks that the attribute is annotated as a Literal type and that
        the value matches the annotation.
        """
        cls_type_hints: dict[str, TypeForm] = get_type_hints(cls)

        assert attr in cls_type_hints and is_literal_type(cls_type_hints[attr]), \
            f'{cls.__name__}.{attr} must be annotated as a Literal type.'

        annotation_args = get_args(cls_type_hints[attr])
        assert annotation_args == (value,), \
            (f'The value of the Literal annotation must match the assigned value for '
             f'{attr}: {annotation_args} != {(value,)}')

    @classmethod
    def _check_attr_matches_cls_literals(
        cls,
        all_cls_literal_vals: set[LiteralEnumInnerTypes],
        value: Any,
    ):
        """
        Checks that the value of the attribute is one of the defined
        literals in `cls.Literals`.
        """
        if value not in all_cls_literal_vals:
            raise TypeError(f'{value} is not defined in {cls.Literals}.')

    @classmethod
    def _is_public_attr(cls, attr: str, value: Any) -> bool:
        return (
            # Check if the attribute is not private
            not attr.startswith('_')
            # Check if the attribute is not a reserved public attribute
            and attr not in cls._RESERVED_PUBLIC_ATTRS
            # Check if the attribute is not a method
            and not cls._is_method(value))

    @classmethod
    def _is_method(cls, val: Any) -> bool:
        return hasattr(val, '__func__')

    @classmethod
    def _check_missing_attributes(
        cls,
        all_cls_literal_vals: set[LiteralEnumInnerTypes],
        defined_attrs: set[LiteralEnumInnerTypes],
    ):
        """
        Checks that all choices in `cls.Literals` are defined as class
        attributes.
        """
        literal_missing_attrs = all_cls_literal_vals - defined_attrs
        if literal_missing_attrs:
            raise TypeError(f'Not all choices in {cls.__name__}.Literals are defined as members. '
                            f'Missing members: {literal_missing_attrs}')

    @classmethod
    def names(cls) -> Iterator[str]:
        """
        Get an iterator of all attribute names defined in the enum.

        Returns:
            An iterator of attribute names defined in the enum.
        """
        return (attr_name for attr_name in cls.__dict__.keys()
                if not attr_name.startswith('_') and attr_name not in cls._RESERVED_PUBLIC_NAMES)

    @classmethod
    def name_for_value(cls: 'type[LiteralEnum[LiteralInnerTypeT]]',
                       value: LiteralInnerTypeT) -> str:
        """
        Get the name of the enum attribute that corresponds to the given value.

        Parameters:
            value: The value to look up in the enum

        Returns:
            The name of the enum attribute that corresponds to the value, or raise ValueError if the
            value is not found.
        """
        for attr_name, attr_value in cls.__dict__.items():
            if attr_value == value:
                return attr_name
        raise ValueError(f'Value {value!r} not found in {cls.__name__}')

    @classmethod
    def random_choice(cls) -> LiteralInnerTypeT:
        """
        Returns a random choice from all available enum values.
        """
        from omnipy.shared.constants import AUTO_VALUE, RANDOM_PREFIX
        exclude_prefixes = [RANDOM_PREFIX, AUTO_VALUE]
        choice = ''
        while choice == '' or any(choice.startswith(_) for _ in exclude_prefixes):
            choice = random.choice(get_args(cls.Literals))

        return cast(LiteralInnerTypeT, choice)

    @classmethod
    def is_random_choice_value(cls, value: object) -> bool:
        """
        Checks whether the provided value is a valid random choice value for
        this enum.

        Parameters:
            value: The value to check.

        Returns:
            True if the value is a valid random choice value for this enum,
            False otherwise.
        """
        from omnipy.shared.constants import RANDOM_PREFIX
        return (isinstance(value, str) and cast(LiteralInnerTypeT, value) in cls
                and value.startswith(RANDOM_PREFIX))
