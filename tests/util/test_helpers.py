from copy import copy
from types import NoneType
from typing import Annotated, Generic, get_args, Iterator, Optional, TypeVar, Union

import pytest
from typing_inspect import get_generic_type

from omnipy.util.helpers import (ensure_non_str_byte_iterable,
                                 ensure_plain_type,
                                 get_calling_module_name,
                                 is_iterable,
                                 is_optional,
                                 is_strict_subclass,
                                 is_union,
                                 remove_annotated_plus_optional_if_present,
                                 RestorableContents,
                                 transfer_generic_args_to_cls)

from .helpers import other_module_call_get_calling_module_name

T = TypeVar('T')
U = TypeVar('U')


class MyGenericDict(dict[T, U], Generic[T, U]):
    ...


def test_transfer_generic_params_to_new_generic_cls() -> None:
    init_dict = MyGenericDict[str, int]({'a': 123})

    assert get_args(get_generic_type(init_dict)) == (str, int)

    class MyDict(dict[T, U]):
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


def test_ensure_plain_type() -> None:
    assert ensure_plain_type(list) == list
    assert ensure_plain_type(list[str]) == list


def test_ensure_non_str_byte_iterable() -> None:
    assert ensure_non_str_byte_iterable((1, 2, 3)) == (1, 2, 3)
    assert ensure_non_str_byte_iterable([1, 2, 3]) == [1, 2, 3]
    assert ensure_non_str_byte_iterable({'a': 1, 'b': 2}) == {'a': 1, 'b': 2}
    assert ensure_non_str_byte_iterable({'a', 'b'}) == {'a', 'b'}

    assert ensure_non_str_byte_iterable(123) == (123,)
    assert ensure_non_str_byte_iterable('abc') == ('abc',)
    assert ensure_non_str_byte_iterable(b'abc') == (b'abc',)
    assert ensure_non_str_byte_iterable(None) == (None,)
    assert ensure_non_str_byte_iterable(True) == (True,)

    x = object()
    assert ensure_non_str_byte_iterable(x) == (x,)


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


def test_is_union() -> None:
    assert is_union(str) is False
    assert is_union(Optional[str]) is True
    assert is_union(Union[str, None]) is True
    assert is_union(str | None) is True

    assert is_union(str | int) is True
    assert is_union(Union[str, int]) is True
    assert is_union(Optional[str | int]) is True
    assert is_union(Optional[Union[str, int]]) is True

    assert is_union(Union[str, int, None]) is True
    assert is_union(Union[Union[str, int], None]) is True
    assert is_union(Union[Union[str, None], int]) is True

    assert is_union(Union[str, int] | None) is True
    assert is_union(Union[str, None] | int) is True

    assert is_union(str | int | None) is True
    assert is_union(str | None | int) is True

    assert is_union(None) is False


def test_is_optional() -> None:
    assert is_optional(str) is False
    assert is_optional(Optional[str]) is True
    assert is_optional(Union[str, None]) is True
    assert is_optional(Union[str, NoneType]) is True
    assert is_optional(str | None) is True
    assert is_optional(str | NoneType) is True

    assert is_optional(str | int) is False
    assert is_optional(Union[str, int]) is False
    assert is_optional(Optional[str | int]) is True
    assert is_optional(Optional[Union[str, int]]) is True

    assert is_optional(Union[str, int, None]) is True
    assert is_optional(Union[str, int, NoneType]) is True
    assert is_optional(Union[str, None, int]) is True
    assert is_optional(Union[str, NoneType, int]) is True

    assert is_optional(Union[Union[str, int], None]) is True
    assert is_optional(Union[Union[str, int], NoneType]) is True
    assert is_optional(Union[Union[str, NoneType], int]) is True
    assert is_optional(Union[Union[str, None], int]) is True

    assert is_optional(Union[str, int] | None) is True
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


def test_remove_annotated_optional_if_present() -> None:
    remove_annotated_plus_opt = remove_annotated_plus_optional_if_present

    assert remove_annotated_plus_opt(str) == str
    assert remove_annotated_plus_opt(str | list[int]) == str | list[int]
    assert remove_annotated_plus_opt(str | list[int] | None) == str | list[int] | None
    assert remove_annotated_plus_opt(Union[str, list[int]]) == Union[str, list[int]]
    assert remove_annotated_plus_opt(Union[str, list[int], None]) == Union[str, list[int], None]
    assert remove_annotated_plus_opt(Optional[Union[str, list[int]]]) == \
           Optional[Union[str, list[int]]]

    assert remove_annotated_plus_opt(Annotated[str, 'something']) == str
    assert remove_annotated_plus_opt(Annotated[str | list[int], 'something']) == str | list[int]
    assert remove_annotated_plus_opt(Annotated[Union[str, list[int]], 'something']) == \
           Union[str, list[int]]

    assert remove_annotated_plus_opt(Annotated[str | None, 'something']) == str
    assert remove_annotated_plus_opt(Annotated[Union[str, None], 'something']) == str
    assert remove_annotated_plus_opt(Annotated[Optional[str], 'something']) == str

    assert remove_annotated_plus_opt(Annotated[str | list[int] | None, 'something']) == \
           Union[str, list[int]]
    assert remove_annotated_plus_opt(Annotated[Union[str, list[int], None], 'something']) == \
           Union[str, list[int]]
    assert remove_annotated_plus_opt(Annotated[Optional[Union[str, list[int]]], 'something']) == \
           Union[str, list[int]]
    assert remove_annotated_plus_opt(Annotated[Optional[str | list[int]],
                                               'something']) == Union[str, list[int]]


def test_restorable_contents():
    contents = RestorableContents()

    my_list = [1, 3, 5]
    my_dict = {1: 2, 3: 4}
    my_other_list = [my_list]

    assert contents.has_snapshot() is False

    with pytest.raises(AssertionError):
        contents.get_last_snapshot()

    with pytest.raises(AssertionError):
        contents.last_snapshot_taken_of_same_obj(my_list)

    with pytest.raises(AssertionError):
        contents.differs_from_last_snapshot(my_list)

    contents.take_snapshot(my_list)
    assert contents.has_snapshot() is True
    assert contents.last_snapshot_taken_of_same_obj(my_list) is True
    assert contents.differs_from_last_snapshot(my_list) is False

    assert contents.last_snapshot_taken_of_same_obj(copy(my_list)) is False
    assert contents.differs_from_last_snapshot(copy(my_list)) is False

    my_list.append(7)
    assert my_list == [1, 3, 5, 7]
    assert my_other_list == [[1, 3, 5, 7]]
    assert contents.last_snapshot_taken_of_same_obj(my_list) is True
    assert contents.differs_from_last_snapshot(my_list) is True

    my_old_list = my_list
    my_list = contents.get_last_snapshot()
    assert my_list == [1, 3, 5]
    assert my_old_list == [1, 3, 5, 7]
    assert my_other_list == [[1, 3, 5, 7]]

    assert my_list is not my_old_list  # the snapshot is a (preferably deep) copy of the old object
    assert contents.last_snapshot_taken_of_same_obj(my_list) is False
    assert contents.differs_from_last_snapshot(my_list) is False

    my_dict[5] = my_list
    assert my_dict == {1: 2, 3: 4, 5: [1, 3, 5]}

    assert contents.last_snapshot_taken_of_same_obj(my_dict) is False
    contents.take_snapshot(my_dict)
    assert contents.last_snapshot_taken_of_same_obj(my_dict) is True
    assert contents.differs_from_last_snapshot(my_dict) is False

    del my_dict[5]
    assert my_dict == {1: 2, 3: 4}
    assert contents.last_snapshot_taken_of_same_obj(my_dict) is True
    assert contents.differs_from_last_snapshot(my_dict) is True


def test_get_calling_module_name() -> None:
    def local_call_get_calling_module_name() -> str:
        return get_calling_module_name()

    assert local_call_get_calling_module_name() == 'tests.util.test_helpers'
    assert other_module_call_get_calling_module_name() == 'tests.util.test_helpers'
