from collections import UserDict, UserList
from copy import copy, deepcopy
import gc
import sys
from types import MethodType, NoneType, UnionType
from typing import (Annotated,
                    Any,
                    ForwardRef,
                    Generic,
                    get_args,
                    Iterator,
                    Literal,
                    Optional,
                    TypeVar,
                    Union)

from pydantic import BaseModel
from pydantic.generics import GenericModel
import pytest
from typing_inspect import get_generic_type

from omnipy.api.protocols.private.util import HasContents
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.util.contexts import Undefined
from omnipy.util.helpers import (all_type_variants,
                                 called_from_omnipy_tests,
                                 ensure_non_str_byte_iterable,
                                 ensure_plain_type,
                                 evaluate_any_forward_refs_if_possible,
                                 get_calling_module_name,
                                 get_first_item,
                                 has_items,
                                 is_iterable,
                                 is_non_omnipy_pydantic_model,
                                 is_non_str_byte_iterable,
                                 is_optional,
                                 is_pure_pydantic_model,
                                 is_strict_subclass,
                                 is_union,
                                 RefCountMemoDict,
                                 remove_annotated_plus_optional_if_present,
                                 Snapshot,
                                 SnapshotHolder,
                                 transfer_generic_args_to_cls,
                                 WeakKeyRefContainer)

T = TypeVar('T')
U = TypeVar('U')
_ContentT = TypeVar('_ContentT', covariant=True, bound=object)


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

    assert is_union(Union[str, int] | None) is True  # type: ignore[operator]
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

    assert is_optional(Union[str, int] | None) is True  # type: ignore[operator]
    assert is_optional(Union[str, int] | NoneType) is True  # type: ignore[operator]
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


def test_is_pydantic_model() -> None:
    class PydanticModel(BaseModel):
        ...

    T = TypeVar('T')

    class GenericPydanticModel(GenericModel, Generic[T]):
        ...

    class Mixin:
        ...

    class MultiInheritModel(BaseModel, Mixin):
        ...

    class PydanticModelSubclass(PydanticModel):
        ...

    class OmnipyModel(Model[int]):
        ...

    class OmnipyModelSubclass(Model[int]):
        ...

    class MultiInheritOmnipyAndPydanticModel(Model[int], BaseModel):
        ...

    class MultiInheritOmnipyAndGenericPydanticModel(Model[int], GenericModel, Generic[T]):
        ...

    assert is_pure_pydantic_model(PydanticModel())
    assert not is_pure_pydantic_model(BaseModel())
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
    assert not is_non_omnipy_pydantic_model(BaseModel())
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


def _assert_values_in_memo(memo: RefCountMemoDict,
                           all_ids: tuple[int, ...],
                           contained: tuple[bool, ...]) -> None:
    assert len(memo) == sum(1 for _ in contained if _ is True)
    for id_, is_contained in zip(all_ids, contained):
        assert (id_ in memo) == is_contained


def test_ref_count_memo_dict() -> None:
    # Note: WeakValueDictionary cannot be used here, as most basic types do not support weak refs.

    ref_count_memo_dict: RefCountMemoDict = RefCountMemoDict()

    class MyClass:
        def __init__(self, contents: object) -> None:
            self.contents = contents

        def __del__(self) -> None:
            print(f'__del__() called for {self}')
            print(ref_count_memo_dict)

            self_id = id(self)
            contents_id = id(self.contents)
            self.contents = Undefined
            ref_count_memo_dict.recursively_remove_deleted_objs(self_id, contents_id)

        def __repr__(self) -> str:
            return f'MyClass({self.contents})'

    def _outer_test_count_memo_dict() -> tuple:
        def _inner_test_count_memo_dict() -> tuple[MyClass, tuple]:
            a_list = [1, 2, 3]
            # creating tuple through list to not add a reference to the tuple in the code object
            b_tuple = tuple(['I want my...', 'I want my...', 'I want my MTV'])
            c_dict = {1: 2, 3: a_list}
            d_obj = MyClass({2: 4, 6: a_list})
            e_obj = MyClass({1: a_list, 2: d_obj})
            print(f'a_list refcount: {sys.getrefcount(a_list)}')

            id_a = id(a_list)
            id_b = id(b_tuple)
            id_c = id(c_dict)
            # id_d = id(d_obj)
            id_d_c = id(d_obj.contents)
            # id_e = id(e_obj)
            id_e_c = id(e_obj.contents)
            all_ids = (id_a, id_b, id_c, id_d_c, id_e_c)

            ref_count_memo_dict[id_a] = a_list
            ref_count_memo_dict[id_b] = b_tuple
            ref_count_memo_dict[id_c] = c_dict
            # ref_count_memo_dict[id_d] = d_obj
            ref_count_memo_dict[id_d_c] = d_obj.contents
            # ref_count_memo_dict[id_e] = e_obj
            ref_count_memo_dict[id_e_c] = e_obj.contents
            print(f'a_list refcount: {sys.getrefcount(a_list)}')

            assert ref_count_memo_dict[id_a] == a_list
            assert ref_count_memo_dict[id_b] == b_tuple
            assert ref_count_memo_dict[id_c] == c_dict
            # assert ref_count_memo_dict[id_d] == d_obj
            assert ref_count_memo_dict[id_d_c] == d_obj.contents
            # assert ref_count_memo_dict[id_e] == e_obj
            assert ref_count_memo_dict[id_e_c] == e_obj.contents

            _assert_values_in_memo(ref_count_memo_dict, all_ids, (True, True, True, True, True))

            del a_list
            del b_tuple

            # a_list was deleted, but is still linked from c_dict and d_obj
            ref_count_memo_dict.recursively_remove_deleted_objs(id_a)
            _assert_values_in_memo(ref_count_memo_dict, all_ids, (True, True, True, True, True))

            print('Returning from _inner_test_count_memo_dict()')

            return e_obj, all_ids

        e_obj, all_ids = _inner_test_count_memo_dict()
        id_a, id_b, id_c, id_d_c, id_e_c = all_ids

        # a_list is still linked from d_obj
        # b_tuple was already deleted, but not checked for ref count until now
        # c_dict was deleted when out of scope of_inner_test_count_memo_dict() and not linked from
        #     anywhere else
        # d_obj was deleted when out of scope of_inner_test_count_memo_dict(), but e_obj still
        #     references it.
        ref_count_memo_dict.recursively_remove_deleted_objs(id_b, id_c)
        _assert_values_in_memo(ref_count_memo_dict, all_ids, (True, False, False, True, True))

        print('Returning from _outer_test_count_memo_dict()')
        return all_ids

    all_ids = _outer_test_count_memo_dict()

    # e_obj is deleted when out of scope of _outer_test_count_memo_dict(), and e_obj.__del__()
    #     method calls recursively_remove_deleted_objs(id_e). No more references left to a, b, c, d, and e.
    # d_obj was fully deleted when e_obj is deleted.
    _assert_values_in_memo(ref_count_memo_dict, all_ids, (False, False, False, False, False))


class HasContentsMixin(Generic[_ContentT]):
    @property
    def contents(self) -> _ContentT:
        return self.data  # type: ignore[attr-defined]

    #
    # def __deepcopy__(self, memo=None):
    #     print(f'__deepcopy__() called for {id(self)}: {self}')
    #     ret = self.__class__(deepcopy(self.data, memo))
    #     # memo[id(self)] = ret
    #     print(f'  memo: {memo}, {type(memo)}')
    #     return ret

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.contents})'


class MyList(HasContentsMixin[list], UserList):
    ...


class MyDict(HasContentsMixin[dict], UserDict):
    ...


def test_weak_key_ref_container() -> None:
    class SomeObject:
        def __init__(self, name: str) -> None:
            self.name = name

    weak_key_ref_container = WeakKeyRefContainer[MyList | MyDict, SomeObject]()

    a_list = MyList([1, 3, 5])

    assert a_list not in weak_key_ref_container
    assert weak_key_ref_container.get(a_list) is None

    with pytest.raises(KeyError):
        weak_key_ref_container[a_list]

    assert len(weak_key_ref_container) == 0

    weak_key_ref_container[a_list] = SomeObject('a_list')

    assert a_list in weak_key_ref_container
    assert weak_key_ref_container.get(a_list) is weak_key_ref_container[a_list]
    assert isinstance(weak_key_ref_container[a_list], SomeObject)
    some_object_a = weak_key_ref_container[a_list]
    assert some_object_a.name == 'a_list'

    b_list = MyList([a_list])
    a_list.append(7)
    assert a_list == MyList([1, 3, 5, 7])
    assert b_list == MyList([[1, 3, 5, 7]])

    b_dict = MyDict({1: 2, 3: 4})

    assert b_dict not in weak_key_ref_container
    weak_key_ref_container[b_dict] = SomeObject('b_dict')
    assert isinstance(weak_key_ref_container[b_dict], SomeObject)
    some_object_b = weak_key_ref_container[b_dict]
    assert some_object_b.name == 'b_dict'

    assert len(weak_key_ref_container) == 2

    del b_dict
    assert len(weak_key_ref_container) == 1

    assert a_list in weak_key_ref_container
    del a_list
    assert len(weak_key_ref_container) == 1

    a_list = b_list[0]
    assert a_list in weak_key_ref_container

    del a_list
    del b_list
    assert len(weak_key_ref_container) == 0


def test_snapshots() -> None:
    snapshot_holder = SnapshotHolder[MyList | MyDict, list | dict]()

    my_list = MyList([1, 3, 5])
    assert my_list.contents == [1, 3, 5]

    assert my_list not in snapshot_holder
    assert snapshot_holder.get(my_list) is None

    with pytest.raises(KeyError):
        snapshot_holder[my_list]

    with pytest.raises(TypeError):
        snapshot_holder[my_list] = my_list  # type: ignore[assignment]

    assert len(snapshot_holder) == 0

    snapshot_holder.take_snapshot(my_list)

    assert my_list in snapshot_holder
    assert snapshot_holder.get(my_list) is snapshot_holder[my_list]
    assert isinstance(snapshot_holder[my_list], Snapshot)

    snapshot = snapshot_holder[my_list]
    assert snapshot.id == id(my_list)
    assert snapshot.taken_of_same_obj(my_list) is True

    assert snapshot.obj_copy == my_list.contents
    assert snapshot.differs_from(my_list) is False

    assert id(snapshot.obj_copy) != id(my_list)

    assert snapshot.taken_of_same_obj(copy(my_list)) is False
    assert snapshot.differs_from(copy(my_list)) is False

    my_other_list = MyList([my_list])
    my_list.append(7)
    assert snapshot.taken_of_same_obj(my_list) is True
    assert snapshot.differs_from(my_list) is True
    assert my_list == MyList([1, 3, 5, 7])
    assert my_other_list == MyList([[1, 3, 5, 7]])

    my_list_from_snapshot = snapshot.obj_copy
    assert my_list_from_snapshot == [1, 3, 5]

    # the snapshot is a (preferably deep) copy of the old object
    assert my_list_from_snapshot is not my_list.contents

    my_dict = MyDict({1: 2, 3: 4})

    my_dict[5] = my_list_from_snapshot
    assert my_dict == MyDict({1: 2, 3: 4, 5: [1, 3, 5]})

    assert my_dict not in snapshot_holder
    snapshot_holder.take_snapshot(my_dict)
    assert snapshot_holder[my_dict].taken_of_same_obj(my_dict) is True
    assert snapshot_holder[my_dict].differs_from(my_dict) is False

    del my_dict[5]
    assert my_dict == MyDict({1: 2, 3: 4})
    assert snapshot_holder[my_dict].taken_of_same_obj(my_dict) is True
    assert snapshot_holder[my_dict].differs_from(my_dict) is True

    assert len(snapshot_holder) == 2

    del my_dict
    assert len(snapshot_holder) == 1

    del my_list
    assert len(snapshot_holder) == 1

    my_list = my_other_list[0]
    assert my_list in snapshot_holder

    del my_list
    del my_other_list
    assert len(snapshot_holder) == 0


def test_snapshot_deepcopy_reuse_objects() -> None:
    snapshot_holder = SnapshotHolder['MyMemoDeletingList', list]()

    class MyMemoDeletingList(MyList):
        def __del__(self) -> None:
            if snapshot_holder is not None:
                contents_id = id(self.contents)
                # self_id = id(self)
                self.data = []
                try:
                    # snapshot_holder.recursively_remove_deleted_obj_from_deepcopy_memo(contents_id)
                    snapshot_holder.keys_for_deleted_objs.append(contents_id)
                except (AttributeError) as exp:
                    print(exp)
                    print(snapshot_holder._deepcopy_memo)

    def _inner_test_snapshot_deepcopy_reuse_objects(
            snapshot_holder: SnapshotHolder[MyMemoDeletingList, list]) -> None:

        inner = MyMemoDeletingList([2, 4])
        middle = MyMemoDeletingList([1, 3, inner])
        outer = MyMemoDeletingList([0, middle, 5])

        snapshot_holder.take_snapshot(outer)
        snapshot_holder.take_snapshot(middle)
        snapshot_holder.take_snapshot(inner)

        assert type(outer[1][-1]) == type(middle[-1]) == type(inner) == MyMemoDeletingList
        assert id(outer[1][-1]) == id(middle[-1]) == id(inner)

        assert type(snapshot_holder[outer].obj_copy[1][-1]) \
               == type(snapshot_holder[middle].obj_copy[-1]) \
               == MyMemoDeletingList
        assert id(snapshot_holder[outer].obj_copy[1][-1]) \
               == id(snapshot_holder[middle].obj_copy[-1])

        assert type(outer[1][-1].contents) == type(middle[-1].contents) == type(
            inner.contents) == list
        assert id(outer[1][-1].contents) == id(middle[-1].contents) == id(inner.contents)

        assert type(snapshot_holder[outer].obj_copy[1][-1].contents) \
               == type(snapshot_holder[middle].obj_copy[-1].contents) \
               == type(snapshot_holder[inner].obj_copy) \
               == list
        assert id(snapshot_holder[outer].obj_copy[1][-1].contents) \
               == id(snapshot_holder[middle].obj_copy[-1].contents) \
               == id(snapshot_holder[inner].obj_copy)

        assert type(outer[1].contents) == type(middle.contents) == list
        assert id(outer[1].contents) == id(middle.contents)

        assert type(snapshot_holder[outer].obj_copy[1].contents) \
               == type(snapshot_holder[middle].obj_copy) \
               == list
        assert id(snapshot_holder[outer].obj_copy[1].contents) \
               == id(snapshot_holder[middle].obj_copy)

    # snapshot_holder = SnapshotHolder[MyMemoDeletingList, list]()
    _inner_test_snapshot_deepcopy_reuse_objects(snapshot_holder)
    assert len(snapshot_holder._deepcopy_memo) == 0


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
