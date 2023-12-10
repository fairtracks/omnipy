from types import NoneType
from typing import Dict, Generic, get_args, Iterator, Optional, TypeVar, Union

from typing_inspect import get_generic_type

from omnipy.util.helpers import (is_iterable,
                                 is_optional,
                                 is_strict_subclass,
                                 transfer_generic_args_to_cls)

T = TypeVar('T')
U = TypeVar('U')


class MyGenericDict(dict[T, U], Generic[T, U]):
    ...


def test_transfer_generic_params_to_new_generic_cls() -> None:
    init_dict = MyGenericDict[str, int]({'a': 123})

    assert get_args(get_generic_type(init_dict)) == (str, int)

    class MyDict(Dict[T, U]):
        ...

    my_dict = MyDict({'b': 234})

    assert get_args(get_generic_type(my_dict)) == ()

    my_typed_dict_cls = transfer_generic_args_to_cls(MyDict, get_generic_type(init_dict))

    my_typed_dict = my_typed_dict_cls({'b': 234})

    assert get_args(get_generic_type(my_typed_dict)) == (str, int)


def test_do_not_transfer_generic_params_to_non_generic_cls() -> None:
    my_int = 123
    my_int_cls = transfer_generic_args_to_cls(int, get_generic_type(my_int))

    my_typed_int = my_int_cls(123)

    assert get_args(get_generic_type(my_typed_int)) == ()


def test_is_iterable() -> None:
    assert is_iterable(None) is False
    assert is_iterable(False) is False
    assert is_iterable(42) is False
    assert is_iterable(3.14) is False

    assert is_iterable('money') is True
    assert is_iterable((1, 2, 3)) is True
    assert is_iterable([1, 2, 3]) is True
    assert is_iterable({1: 2, 3: 4}) is True
    assert is_iterable({1, 5, 6}) is True

    class MyNonIter:
        ...

    class MyHistoricIter:
        def __getitem__(self, index: int) -> int:
            return (1, 2, 3)[index]

    class MyModernIter:
        def __iter__(self) -> Iterator[int]:
            return iter((1, 2, 3))

    assert is_iterable(MyNonIter()) is False
    assert is_iterable(MyHistoricIter()) is True
    assert is_iterable(MyModernIter()) is True


def test_is_optional() -> None:
    assert is_optional(str) is False
    assert is_optional(Optional[str]) is True  # type: ignore
    assert is_optional(Union[str, None]) is True  # type: ignore
    assert is_optional(Union[str, NoneType]) is True  # type: ignore
    assert is_optional(str | None) is True
    assert is_optional(str | NoneType) is True

    assert is_optional(str | int) is False
    assert is_optional(Union[str, int]) is False  # type: ignore
    assert is_optional(Optional[str | int]) is True  # type: ignore
    assert is_optional(Optional[Union[str, int]]) is True  # type: ignore

    assert is_optional(Union[str, int, None]) is True  # type: ignore
    assert is_optional(Union[str, int, NoneType]) is True  # type: ignore
    assert is_optional(Union[str, None, int]) is True  # type: ignore
    assert is_optional(Union[str, NoneType, int]) is True  # type: ignore

    assert is_optional(Union[Union[str, int], None]) is True  # type: ignore
    assert is_optional(Union[Union[str, int], NoneType]) is True  # type: ignore
    assert is_optional(Union[Union[str, NoneType], int]) is True  # type: ignore
    assert is_optional(Union[Union[str, None], int]) is True  # type: ignore

    assert is_optional(Union[str, int] | None) is True  # type: ignore
    assert is_optional(Union[str, int] | NoneType) is True
    assert is_optional(Union[str, NoneType] | int) is True
    assert is_optional(Union[str, None] | int) is True

    assert is_optional(str | int | None) is True
    assert is_optional(str | int | NoneType) is True
    assert is_optional(str | None | int) is True
    assert is_optional(str | NoneType | int) is True

    assert is_optional(None) is False


def test_is_strict_subclass() -> None:
    class Mother:
        ...

    class Father:
        ...

    class Sister(Mother, Father):
        ...

    class Brother(Mother, Father):
        ...

    class Child(Mother, Father):
        ...

    assert issubclass(Child, Mother) is True
    assert issubclass(Child, Brother) is False
    assert issubclass(Mother, Child) is False
    assert issubclass(Mother, Mother) is True
    assert issubclass(Child, Child) is True

    assert is_strict_subclass(Child, Mother) is True
    assert is_strict_subclass(Child, Brother) is False
    assert is_strict_subclass(Mother, Child) is False
    assert is_strict_subclass(Mother, Mother) is False
    assert is_strict_subclass(Child, Child) is False

    assert issubclass(Child, (Father, Mother)) is True
    assert issubclass(Child, (Mother, Brother)) is True
    assert issubclass(Father, (Sister, Brother)) is False
    assert issubclass(Mother, (Mother, Father)) is True
    assert issubclass(Child, (Mother, Child)) is True

    assert is_strict_subclass(Child, (Father, Mother)) is True
    assert is_strict_subclass(Child, (Mother, Brother)) is True
    assert is_strict_subclass(Father, (Sister, Brother)) is False
    assert is_strict_subclass(Mother, (Mother, Father)) is False
    assert is_strict_subclass(Child, (Mother, Child)) is False
