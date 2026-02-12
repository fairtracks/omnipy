from types import MethodType, NoneType, UnionType
from typing import Annotated, Any, ForwardRef, Generic, get_args, Iterator, Literal, Optional, Union

import pytest
from typing_extensions import TypeVar

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.util.helpers import (all_type_variants,
                                 called_from_omnipy_tests,
                                 ensure_non_str_byte_iterable,
                                 ensure_plain_type,
                                 evaluate_any_forward_refs_if_possible,
                                 get_calling_module_name,
                                 get_first_item,
                                 get_parametrized_type,
                                 has_items,
                                 is_iterable,
                                 is_literal_type,
                                 is_non_omnipy_pydantic_model,
                                 is_non_str_byte_iterable,
                                 is_optional,
                                 is_pure_pydantic_model,
                                 is_strict_subclass,
                                 is_union,
                                 is_unreserved_identifier,
                                 sorted_dict_hash,
                                 split_to_union_variants,
                                 transfer_generic_args_to_cls)
import omnipy.util.pydantic as pyd

T = TypeVar('T')
U = TypeVar('U')


def test_key_sorted_dict_hash() -> None:
    d1 = {'b': 2, 'a': 1}
    d2 = {'a': 1, 'b': 2}
    d3 = {'a': 1, 'c': 2}
    d4: dict[str, int] = {}
    d5: dict[str, int] = {}

    assert sorted_dict_hash(d1) == sorted_dict_hash(d2)
    assert sorted_dict_hash(d1) != sorted_dict_hash(d3)
    assert sorted_dict_hash(d3) != sorted_dict_hash(d4)
    assert sorted_dict_hash(d4) == sorted_dict_hash(d5)


class MyGenericDict(dict[T, U], Generic[T, U]):
    ...


def test_transfer_generic_params_to_new_generic_cls() -> None:
    init_dict = MyGenericDict[str, int]({'a': 123})

    assert get_args(get_parametrized_type(init_dict)) == (str, int)

    class MyDict(dict[T, U]):
        ...

    my_dict = MyDict({'b': 234})

    assert get_args(get_parametrized_type(my_dict)) == ()

    my_typed_dict_cls = transfer_generic_args_to_cls(MyDict, get_parametrized_type(init_dict))
    my_typed_dict = my_typed_dict_cls({'b': 234})  # type: ignore

    assert get_args(get_parametrized_type(my_typed_dict)) == (str, int)


def test_do_not_transfer_generic_params_to_non_generic_cls() -> None:
    my_int = 123
    my_int_cls = transfer_generic_args_to_cls(int, get_parametrized_type(my_int))

    my_typed_int = my_int_cls(123)

    assert get_args(get_parametrized_type(my_typed_int)) == ()


def test_ensure_plain_type() -> None:
    T = TypeVar('T')

    assert ensure_plain_type(ForwardRef('list[str]')) == ForwardRef('list[str]')  # ForwardRef
    assert ensure_plain_type(T) == T  # TypeVar
    assert ensure_plain_type(list) == list  # type
    assert ensure_plain_type(list[str]) == list  # GenericAlias
    assert ensure_plain_type(str | int) == UnionType  # UnionType
    assert ensure_plain_type(Any) == Any  # _SpecialForm
    assert ensure_plain_type(Literal[5]) == Literal  # _LiteralGenericAlias
    assert ensure_plain_type(Union[str, int]) == UnionType  # _UnionGenericAlias
    assert ensure_plain_type(Annotated[str, 'annotation']) == Annotated  # _AnnotatedAlias
    assert ensure_plain_type(None) is None  # NoneType
    assert ensure_plain_type(NoneType) is None  # NoneType


class MyGlobalClass:
    ...


def test_evaluate_any_forward_refs_if_possible() -> None:
    assert evaluate_any_forward_refs_if_possible(ForwardRef('list')) == list
    assert evaluate_any_forward_refs_if_possible(ForwardRef('list[str]')) == list[str]

    assert evaluate_any_forward_refs_if_possible(ForwardRef('MyGlobalClass')) == MyGlobalClass
    assert evaluate_any_forward_refs_if_possible(
        list[ForwardRef('MyGlobalClass')]) == list[MyGlobalClass]  # type: ignore[misc]
    assert evaluate_any_forward_refs_if_possible(
        list[list[ForwardRef('MyGlobalClass')]]) == list[list[MyGlobalClass]]  # type: ignore[misc]

    assert evaluate_any_forward_refs_if_possible(
        ForwardRef('MyLocalClass')) == ForwardRef('MyLocalClass')

    assert evaluate_any_forward_refs_if_possible(
        ForwardRef('MyLocalClass'),
        **locals(),
    ) == ForwardRef('MyLocalClass')

    class MyLocalClass:
        ...

    assert evaluate_any_forward_refs_if_possible(
        ForwardRef('MyLocalClass'),) == ForwardRef('MyLocalClass')

    assert evaluate_any_forward_refs_if_possible(
        ForwardRef('MyLocalClass'),
        **locals(),
    ) == MyLocalClass

    assert evaluate_any_forward_refs_if_possible(
        ForwardRef('MyLocalClass'),
        MyLocalClass=MyLocalClass,
    ) == MyLocalClass

    assert evaluate_any_forward_refs_if_possible(
        list[ForwardRef('MyLocalClass')],  # type: ignore[misc]
        MyLocalClass=MyLocalClass,
    ) == list[MyLocalClass]

    assert evaluate_any_forward_refs_if_possible(
        Union[
            list[ForwardRef('MyLocalClass')],  # type: ignore[misc]
            tuple[ForwardRef('MyLocalClass')]],  # type: ignore[misc]
        MyLocalClass=MyLocalClass,
    ) == Union[list[MyLocalClass], tuple[MyLocalClass]]

    assert evaluate_any_forward_refs_if_possible(
        list[ForwardRef('MyLocalClass')] | tuple[ForwardRef('MyLocalClass')],  # type: ignore[misc]
        MyLocalClass=MyLocalClass,
    ) == list[MyLocalClass] | tuple[MyLocalClass]


def test_all_type_variants() -> None:
    assert all_type_variants(list) == (list,)
    assert all_type_variants(list[str]) == (list[str],)
    assert all_type_variants(int | str) == (int, str)
    assert all_type_variants(int | str | tuple[int] | list[int | str]) == (int,
                                                                           str,
                                                                           tuple[int],
                                                                           list[int | str])


def test_is_iterable() -> None:
    assert is_iterable(None) is False
    assert is_iterable(False) is False
    assert is_iterable(42) is False
    assert is_iterable(3.14) is False

    assert is_iterable('money') is True
    assert is_iterable(b'money') is True
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


def test_is_non_str_byte_iterable() -> None:
    assert is_non_str_byte_iterable(None) is False
    assert is_non_str_byte_iterable(False) is False
    assert is_non_str_byte_iterable(42) is False
    assert is_non_str_byte_iterable(3.14) is False

    assert is_non_str_byte_iterable('money') is False
    assert is_non_str_byte_iterable(b'money') is False
    assert is_non_str_byte_iterable((1, 2, 3)) is True
    assert is_non_str_byte_iterable([1, 2, 3]) is True
    assert is_non_str_byte_iterable({1: 2, 3: 4}) is True
    assert is_non_str_byte_iterable({1, 5, 6}) is True

    class MyNonIter:
        ...

    class MyHistoricIter:
        def __getitem__(self, index: int) -> int:
            return (1, 2, 3)[index]

    class MyModernIter:
        def __iter__(self) -> Iterator[int]:
            return iter((1, 2, 3))

    assert is_non_str_byte_iterable(MyNonIter()) is False
    assert is_non_str_byte_iterable(MyHistoricIter()) is True
    assert is_non_str_byte_iterable(MyModernIter()) is True


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


def test_has_items() -> None:
    assert has_items(None) is False
    assert has_items(False) is False
    assert has_items(42) is False
    assert has_items(3.14) is False

    assert has_items('') is False
    assert has_items(b'') is False
    assert has_items('money') is True
    assert has_items(b'money') is True

    assert has_items(()) is False
    assert has_items([]) is False
    assert has_items({}) is False
    assert has_items(set()) is False

    assert has_items((1, 2, 3)) is True
    assert has_items([1, 2, 3]) is True
    assert has_items({1: 2, 3: 4}) is True
    assert has_items({1, 5, 6}) is True

    class MyClass:
        ...

    def __len__(self):
        return 1

    a = MyClass()
    a.__len__ = MethodType(__len__, a)  # type: ignore[attr-defined]

    assert has_items(a) is True


def test_get_first_item() -> None:
    with pytest.raises(AssertionError):
        get_first_item(42)  # type: ignore[arg-type]

    with pytest.raises(AssertionError):
        get_first_item('')

    with pytest.raises(AssertionError):
        get_first_item([])

    assert get_first_item((1, 2, 3)) == 1
    assert get_first_item([1, 2, 3]) == 1
    assert get_first_item({1: 2, 3: 4}) == 1
    assert get_first_item({1, 5, 6}) == 1


def test_split_to_union_variants() -> None:
    assert split_to_union_variants(str) == (str,)
    assert split_to_union_variants(Optional[str]) == (str, NoneType)
    assert split_to_union_variants(Union[str, None]) == (str, NoneType)
    assert split_to_union_variants(str | None) == (str, NoneType)

    assert split_to_union_variants(str | int) == (str, int)
    assert split_to_union_variants(Union[str, int]) == (str, int)
    assert split_to_union_variants(Optional[str | int]) == (str, int, NoneType)
    assert split_to_union_variants(Optional[Union[str, int]]) == (str, int, NoneType)

    assert split_to_union_variants(Union[str, int, None]) == (str, int, NoneType)
    assert split_to_union_variants(Union[Union[str, int], None]) == (str, int, NoneType)
    assert split_to_union_variants(Union[Union[str, None], int]) == (str, NoneType, int)

    assert split_to_union_variants(Union) == ()

    assert split_to_union_variants(str | int | None) == (str, int, NoneType)
    assert split_to_union_variants(str | None | int) == (str, NoneType, int)


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
    assert is_union(Union) is True

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
    assert is_optional(str | Literal[None]) is True

    assert is_optional(str | int) is False
    assert is_optional(Union[str, int]) is False
    assert is_optional(Optional[str | int]) is True
    assert is_optional(Optional[Union[str, int]]) is True

    assert is_optional(Union[str, int, None]) is True
    assert is_optional(Union[str, int, NoneType]) is True
    assert is_optional(Union[str, int, Literal[None]]) is True
    assert is_optional(Union[str, None, int]) is True
    assert is_optional(Union[str, NoneType, int]) is True
    assert is_optional(Union[str, Literal[None], int]) is True

    assert is_optional(Union[Union[str, int], None]) is True
    assert is_optional(Union[Union[str, int], NoneType]) is True
    assert is_optional(Union[Union[str, int], Literal[None]]) is True
    assert is_optional(Union[Union[str, None], int]) is True
    assert is_optional(Union[Union[str, NoneType], int]) is True
    assert is_optional(Union[Union[str, Literal[None]], int]) is True

    assert is_optional(Union[str, int] | None) is True
    assert is_optional(Union[str, int] | NoneType) is True
    assert is_optional(Union[str, int] | Literal[None]) is True
    assert is_optional(Union[str, None] | int) is True
    assert is_optional(Union[str, NoneType] | int) is True
    assert is_optional(Union[str, Literal[None]] | int) is True

    assert is_optional(str | int | None) is True
    assert is_optional(str | int | NoneType) is True
    assert is_optional(str | int | Literal[None]) is True
    assert is_optional(str | None | int) is True
    assert is_optional(str | NoneType | int) is True
    assert is_optional(str | Literal[None] | int) is True

    assert is_optional(None) is False
    assert is_optional(NoneType) is False
    assert is_optional(Literal[None]) is False


def test_is_literal_type() -> None:
    assert is_literal_type(Literal['a', 'b'])
    assert is_literal_type(Literal[True, False])
    assert is_literal_type(Literal[1, 2, 3])
    assert is_literal_type(Literal['one value'])

    assert not is_literal_type(str)
    assert not is_literal_type(int)
    assert not is_literal_type(bool)
    assert not is_literal_type(list)


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


def test_is_pydantic_model() -> None:
    class PydanticModel(pyd.BaseModel):
        ...

    T = TypeVar('T')

    class GenericPydanticModel(pyd.GenericModel, Generic[T]):
        ...

    class Mixin:
        ...

    class MultiInheritModel(pyd.BaseModel, Mixin):
        ...

    class PydanticModelSubclass(PydanticModel):
        ...

    class OmnipyModel(Model[int]):
        ...

    class OmnipyModelSubclass(Model[int]):
        ...

    class MultiInheritOmnipyAndPydanticModel(Model[int], pyd.BaseModel):
        ...

    class MultiInheritOmnipyAndGenericPydanticModel(Model[int], pyd.GenericModel, Generic[T]):
        ...

    assert is_pure_pydantic_model(PydanticModel())
    assert not is_pure_pydantic_model(pyd.BaseModel())
    assert not is_pure_pydantic_model(GenericPydanticModel())
    assert not is_pure_pydantic_model(MultiInheritModel())
    assert not is_pure_pydantic_model(PydanticModelSubclass())
    assert not is_pure_pydantic_model(OmnipyModel())
    assert not is_pure_pydantic_model(OmnipyModelSubclass())
    assert not is_pure_pydantic_model(MultiInheritOmnipyAndPydanticModel())
    assert not is_pure_pydantic_model(MultiInheritOmnipyAndGenericPydanticModel())
    assert not is_pure_pydantic_model(Model[PydanticModel]())
    assert not is_pure_pydantic_model(Dataset[Model[PydanticModel]]())
    assert not is_pure_pydantic_model('model')

    assert is_non_omnipy_pydantic_model(PydanticModel())
    assert not is_non_omnipy_pydantic_model(pyd.BaseModel())
    assert is_non_omnipy_pydantic_model(GenericPydanticModel())
    assert is_non_omnipy_pydantic_model(MultiInheritModel())
    assert is_non_omnipy_pydantic_model(PydanticModelSubclass())
    assert not is_non_omnipy_pydantic_model(OmnipyModel())
    assert not is_non_omnipy_pydantic_model(OmnipyModelSubclass())
    assert not is_non_omnipy_pydantic_model(MultiInheritOmnipyAndPydanticModel())
    assert not is_non_omnipy_pydantic_model(MultiInheritOmnipyAndGenericPydanticModel())
    assert not is_non_omnipy_pydantic_model(Model[PydanticModel]())
    assert not is_non_omnipy_pydantic_model(Dataset[Model[PydanticModel]]())
    assert not is_non_omnipy_pydantic_model('model')


def test_is_unreserved_identifier():
    assert is_unreserved_identifier('MyClass') is True
    assert is_unreserved_identifier('myobj_1') is True
    assert is_unreserved_identifier('123_a') is False
    assert is_unreserved_identifier('abc def') is False
    assert is_unreserved_identifier('class') is False
    assert is_unreserved_identifier('match') is False


def test_get_calling_module_name() -> None:
    def local_call_get_calling_module_name() -> str | None:
        return get_calling_module_name()

    from .helpers.other_module import (calling_module_name_when_importing_other_module,
                                       other_module_call_get_calling_module_name)

    assert local_call_get_calling_module_name() == 'tests.util.test_helpers'
    assert other_module_call_get_calling_module_name() == 'tests.util.test_helpers'
    assert calling_module_name_when_importing_other_module == 'tests.util.test_helpers'


def test_called_from_omnipy_tests() -> None:
    # Negative test is left as an exercise to the reader
    assert called_from_omnipy_tests()


def test_min_or_none() -> None:
    from omnipy.util.helpers import min_or_none

    assert min_or_none(3, 1, 2.5) == 1
    assert min_or_none(3, 1, None) == 1
    assert min_or_none(None, None) is None
    assert min_or_none() is None


def test_max_or_none() -> None:
    from omnipy.util.helpers import max_or_none

    assert max_or_none(3, 1, 2.5) == 3
    assert max_or_none(3, 1, None) == 3
    assert max_or_none(None, None) is None
    assert max_or_none() is None
