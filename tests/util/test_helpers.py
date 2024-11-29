from collections import UserDict, UserList
from copy import copy, deepcopy
import gc
from types import MethodType, NoneType, UnionType
from typing import (Annotated,
                    Any,
                    ForwardRef,
                    Generic,
                    get_args,
                    Iterator,
                    Literal,
                    Optional,
                    TypeAlias,
                    TypeVar,
                    Union)
import weakref

from pydantic import BaseModel
from pydantic.fields import Undefined
from pydantic.generics import GenericModel
import pytest

from omnipy.api.protocols.private.util import HasContents, IsSnapshotHolder
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
                                 is_non_omnipy_pydantic_model,
                                 is_non_str_byte_iterable,
                                 is_optional,
                                 is_pure_pydantic_model,
                                 is_strict_subclass,
                                 is_union,
                                 is_unreserved_identifier,
                                 RefCountMemoDict,
                                 SnapshotHolder,
                                 SnapshotWrapper,
                                 transfer_generic_args_to_cls,
                                 WeakKeyRefContainer)
from omnipy.util.setdeque import SetDeque

T = TypeVar('T')
U = TypeVar('U')
_ContentsT = TypeVar('_ContentsT', bound=object)


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

    my_typed_dict = my_typed_dict_cls({'b': 234})

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


def test_is_unreserved_identifier():
    assert is_unreserved_identifier('MyClass') is True
    assert is_unreserved_identifier('myobj_1') is True
    assert is_unreserved_identifier('123_a') is False
    assert is_unreserved_identifier('abc def') is False
    assert is_unreserved_identifier('class') is False
    assert is_unreserved_identifier('match') is False


def _assert_values_in_memo(memo: RefCountMemoDict,
                           all_ids: tuple[int, ...],
                           contained: tuple[bool, ...],
                           total_len: int) -> None:
    for id_, is_contained in zip(all_ids, contained):
        assert (id_ in memo) == is_contained
        assert (id_ in memo.get_deepcopy_object_ids()) == is_contained
    assert len(memo) == total_len


def test_ref_count_memo_dict_basics() -> None:
    ref_count_memo_dict: RefCountMemoDict = RefCountMemoDict()

    my_list = [1, 2, 3]
    my_dict = {1: my_list, 2: 3}

    ref_count_memo_dict[id(my_list)] = my_list
    ref_count_memo_dict[id(my_dict)] = my_dict

    assert len(ref_count_memo_dict) == 2

    ref_count_memo_dict.clear()

    assert ref_count_memo_dict.all_are_empty()


def test_ref_count_memo_dict_atomic_types() -> None:
    ref_count_memo_dict: RefCountMemoDict = RefCountMemoDict()

    def my_func():
        ...

    atomic_objs = [
        None,
        ...,
        NotImplemented,
        5,
        3.14,
        True,
        3 + 4j,
        b'abc',
        'abc',
        (1, 2, 3),
        my_func.__code__,
        int,
        range(5),
        open,
        my_func,
        weakref.ref(my_func),
    ]

    for obj in atomic_objs:
        ref_count_memo_dict[id(obj)] = obj
        assert ref_count_memo_dict.all_are_empty()


def test_ref_count_memo_dict_non_atomic_types() -> None:
    ref_count_memo_dict: RefCountMemoDict = RefCountMemoDict()

    class MyClass:
        ...

    non_atomic_type_objs = [[1, 2, 3], {1: 2, 3: 4}, {2, 4, 6}, MyClass()]

    for obj in non_atomic_type_objs:
        ref_count_memo_dict[id(obj)] = obj
        assert len(ref_count_memo_dict) == 1

        del ref_count_memo_dict[id(obj)]
        assert ref_count_memo_dict.all_are_empty()


def _deepcopy_obj_with_memodict(ref_count_memo_dict: RefCountMemoDict, tmp_obj: object):
    ref_count_memo_dict.setup_deepcopy(tmp_obj)
    deepcopy(tmp_obj, ref_count_memo_dict)  # type: ignore[arg-type]
    ref_count_memo_dict.keep_alive_after_deepcopy()
    ref_count_memo_dict.teardown_deepcopy()


def test_ref_count_memo_dict_deepcopy_obj() -> None:
    ref_count_memo_dict: RefCountMemoDict = RefCountMemoDict()

    assert len(ref_count_memo_dict) == 0
    assert ref_count_memo_dict.get_deepcopy_object_ids() == SetDeque()
    assert ref_count_memo_dict.all_are_empty()

    my_list = [1, 2, 3]
    id_my_list = id(my_list)

    _deepcopy_obj_with_memodict(ref_count_memo_dict, my_list)

    assert len(ref_count_memo_dict) == 1
    assert ref_count_memo_dict.get_deepcopy_object_ids() == SetDeque((id_my_list,))
    assert not ref_count_memo_dict.all_are_empty()

    id_my_list = id(my_list)
    del my_list

    assert len(ref_count_memo_dict) == 1
    assert ref_count_memo_dict.get_deepcopy_object_ids() == SetDeque((id_my_list,))
    assert not ref_count_memo_dict.all_are_empty()

    ref_count_memo_dict.recursively_remove_deleted_objs(SetDeque((id_my_list,)))

    assert len(ref_count_memo_dict) == 0
    assert ref_count_memo_dict.get_deepcopy_object_ids() == SetDeque()
    assert ref_count_memo_dict.all_are_empty()


def test_ref_count_memo_dict_complex_object_deletion() -> None:
    # Note: WeakValueDictionary cannot be used here, as most basic types do not support weak refs.

    ref_count_memo_dict: RefCountMemoDict = RefCountMemoDict()

    class MyClass:
        def __init__(self, contents: object) -> None:
            self.contents = contents

        def __del__(self) -> None:
            contents_id = id(self.contents)

            # print(f'__del__() called for {self} (id(self.contents)={contents_id})')
            # print(ref_count_memo_dict)

            self.contents = Undefined
            ref_count_memo_dict.recursively_remove_deleted_objs(SetDeque((contents_id,)))

        def __repr__(self) -> str:
            return f'MyClass({self.contents})'

        def __eq__(self, other):
            if isinstance(other, MyClass):
                return self.contents == other.contents
            return False

    def _outer_test_count_memo_dict() -> tuple:
        def _inner_test_count_memo_dict() -> tuple[MyClass, tuple]:
            a_list = [1, 2, 3]
            # creating tuple through list to not add a reference to the tuple in the code object
            b_tuple = tuple(['I want my...', 'I want my...', 'I want my MTV'])
            c_set = {1, 2}
            d_dict = {1: 2, 3: a_list}
            e_obj = MyClass({2: 4, 6: a_list})
            f_obj = MyClass({1: e_obj, 2: e_obj})

            for obj in (a_list, c_set, b_tuple, d_dict, e_obj.contents, f_obj.contents):
                _deepcopy_obj_with_memodict(ref_count_memo_dict, obj)

            id_a = id(a_list)
            id_b = id(b_tuple)
            id_c = id(c_set)
            id_d = id(d_dict)
            id_e_c = id(e_obj.contents)
            id_f_c = id(f_obj.contents)
            all_ids = (id_a, id_b, id_c, id_d, id_e_c, id_f_c)

            assert ref_count_memo_dict[id_a] == a_list
            assert id_b not in ref_count_memo_dict  # tuples are not memoized
            assert ref_count_memo_dict[id_c] == c_set
            assert ref_count_memo_dict[id_d] == d_dict
            assert ref_count_memo_dict[id_e_c] == e_obj.contents
            assert ref_count_memo_dict[id_f_c] == f_obj.contents

            _assert_values_in_memo(
                ref_count_memo_dict,
                all_ids,
                contained=(True, False, True, True, True, True),
                total_len=8,
            )

            del a_list
            del b_tuple
            del c_set

            # a_list was deleted, but is still referenced from d_dict and e_obj
            # b_tuple was deleted, but is not memoized
            ref_count_memo_dict.recursively_remove_deleted_objs(SetDeque((id_a, id_b)))
            _assert_values_in_memo(
                ref_count_memo_dict,
                all_ids,
                contained=(True, False, True, True, True, True),
                total_len=8,
            )

            return f_obj, all_ids

        f_obj, all_ids = _inner_test_count_memo_dict()
        id_a, id_b, id_c, id_d, id_e_c, id_f_c = all_ids

        # a_list is still referenced from e_obj
        # c_set was already deleted, but not checked for ref count until now. The extra list object
        #     created by deepcopy() of a set() is also deleted
        # d_dict was deleted when out of scope of_inner_test_count_memo_dict() and not referenced
        #     from anywhere else
        # e_obj was deleted when out of scope of_inner_test_count_memo_dict(), but f_obj still
        #     references it
        ref_count_memo_dict.recursively_remove_deleted_objs(SetDeque((id_c, id_d)))
        _assert_values_in_memo(
            ref_count_memo_dict,
            all_ids,
            contained=(True, False, False, False, True, True),
            total_len=5,
        )

        return all_ids

    all_ids = _outer_test_count_memo_dict()

    # f_obj is deleted when out of scope of _outer_test_count_memo_dict(), and f_obj.__del__()
    #     method calls recursively_remove_deleted_objs([id_f_c]).
    # e_obj was fully deleted when f_obj was deleted. The extra MyClass object and MyClass.__dict__
    #     instances created by deepcopy() of a non-builtin object were also deleted
    # c_set was fully deleted when f_obj was deleted
    # a_list was fully deleted when e_obj was deleted
    _assert_values_in_memo(
        ref_count_memo_dict,
        all_ids,
        contained=(False, False, False, False, False, False),
        total_len=0,
    )

    assert ref_count_memo_dict.all_are_empty()


class SomeObject:
    def __init__(self, name: str) -> None:
        self.name = name

    def __eq__(self, other):
        if isinstance(other, SomeObject):
            return self.name == other.name
        return False


BasicType: TypeAlias = list | tuple | dict | set | str | float | int | complex | bool | SomeObject


def test_ref_count_memo_dict_deepcopy_keep_alive() -> None:
    ref_count_memo_dict = RefCountMemoDict[Any]()

    def _register_all_basic_objs_to_be_deleted_and_return_ids() -> SetDeque[int]:
        tmp_obj: BasicType
        all_memoized_basic_objs: list[BasicType] = [
            [1, 3, 5],
            {
                1: 2, 3: 4
            },
            {2, 4, 6},
            SomeObject('some_object'),
        ]
        all_non_memoized_basic_objs: list[BasicType] = [
            (1, 3, 5),
            'abc',
            3.14,
            42,
            3 + 4j,
            True,
        ]
        all_basic_objs = all_memoized_basic_objs + all_non_memoized_basic_objs

        all_memoized_basic_objs_copy: list[BasicType] = deepcopy(all_memoized_basic_objs)

        assert isinstance(all_memoized_basic_objs_copy[2], set)
        all_memoized_basic_objs_copy.append(list(all_memoized_basic_objs_copy[2]))

        assert isinstance(all_memoized_basic_objs_copy[3], SomeObject)
        all_memoized_basic_objs_copy.append(all_memoized_basic_objs_copy[3].__dict__)

        all_basic_objs_copy: list[BasicType] = deepcopy(all_basic_objs)

        memo_target: list[BasicType | list[BasicType]] = \
            [all_basic_objs_copy[i:] for i in range(len(all_basic_objs_copy))] \
            + all_memoized_basic_objs_copy

        tmp_obj_ids: SetDeque[int] = SetDeque()

        # To test whether the RefCountMemoDict keeps the temporary objects alive, we need to
        # make sure that new objects are not reusing the same memory locations, and thus the same
        # ids as the old ones. Since the time of deletion by the python garbage controller is not
        # deterministic (at least across different Python implementations), we run the same test
        # multiple times to increase the likelihood of the objects being deleted and their
        # memory locations being reused, given that the RefCountMemoDict is not keeping the
        # objects alive.

        for i in range(100):
            ref_count_memo_dict.clear()
            tmp_obj_ids.clear()

            for start_idx in range(len(all_basic_objs)):
                tmp_obj = all_basic_objs[start_idx:]

                _deepcopy_obj_with_memodict(ref_count_memo_dict, tmp_obj)

                tmp_obj_ids.append(id(tmp_obj))

            assert len(ref_count_memo_dict) == len(memo_target)

            for value in ref_count_memo_dict.values():
                assert value in memo_target

        del all_basic_objs
        return tmp_obj_ids

    all_tmp_obj_ids = _register_all_basic_objs_to_be_deleted_and_return_ids()
    ref_count_memo_dict.recursively_remove_deleted_objs(all_tmp_obj_ids)

    assert ref_count_memo_dict.all_are_empty()


def test_ref_count_memo_dict_deepcopy_tuple_of_list_keepalive() -> None:
    ref_count_memo_dict = RefCountMemoDict[tuple]()

    tuple_of_list: tuple[int, list[int | tuple[int, list]]] = (1, [2, (3, [])])
    id_tuple_of_list = id(tuple_of_list)

    _deepcopy_obj_with_memodict(ref_count_memo_dict, tuple_of_list)

    del tuple_of_list
    ref_count_memo_dict.recursively_remove_deleted_objs(SetDeque((id_tuple_of_list,)))

    assert ref_count_memo_dict.all_are_empty()


def test_ref_count_memo_dict_deepcopy_pydantic_model_with_parsing() -> None:
    ref_count_memo_dict = RefCountMemoDict[tuple]()

    class MyUpperStrModel(Model[str]):
        @classmethod
        def _parse_data(cls, v):
            return v.upper()

    class ListOfUpperStrModel(Model[list[MyUpperStrModel]]):
        ...

    my_model = ListOfUpperStrModel(['abc'])
    id_my_model = id(my_model)

    _deepcopy_obj_with_memodict(ref_count_memo_dict, id_my_model)

    del my_model
    ref_count_memo_dict.recursively_remove_deleted_objs(SetDeque((id_my_model,)))

    assert ref_count_memo_dict.all_are_empty()


@pytest.mark.skip(reason='Repeated deepcopy of the same object is not supported. Changes to the '
                  'object between deepcopies might result in fragments of the old object '
                  'being kept alive. While there at least partial solutions to this '
                  'problem commented out in the code, they are not needed in practice, as'
                  'validation of Model.contents is always run before taking a snapshot if the '
                  'contents has changed, returning a new object to be taken snapshot of. '
                  'Then SnapshotHolder replaces the old snapshot with the new one, and the old '
                  'snapshot is scheduled for deletion, in order to correctly remove all '
                  'unreferenced fragments that are still being kept alive. The test is kept '
                  'here for documentation purposes.')
def test_ref_count_memo_dict_repeated_deepcopy_same_obj_not_needed() -> None:
    ref_count_memo_dict = RefCountMemoDict[Any]()

    a_list = [1, 3, 5]
    b_list = [2, 4, 6]
    c_list = [3, 5, 7]
    c_parent_list = [a_list, b_list]
    id_c_parent_list = id(c_parent_list)

    _deepcopy_obj_with_memodict(ref_count_memo_dict, c_parent_list)

    del c_parent_list[0]
    c_parent_list.append(c_list)

    _deepcopy_obj_with_memodict(ref_count_memo_dict, c_parent_list)

    del c_parent_list
    del c_list
    del b_list
    del a_list

    ref_count_memo_dict.recursively_remove_deleted_objs(SetDeque((id_c_parent_list,)))
    assert ref_count_memo_dict.all_are_empty()


class HasContentsMixin(Generic[_ContentsT]):
    @property
    def contents(self) -> _ContentsT:
        return self.data

    @contents.setter
    def contents(self, value: _ContentsT) -> None:
        self.data = value

    #
    # def __deepcopy__(self, memo=None):
    #     print(f'__deepcopy__() called for {id(self)}: {self}')
    #     ret = self.__class__(deepcopy(self.data, memo))
    #     # memo[id(self)] = ret
    #     print(f'  memo: {memo}, {type(memo)}')
    #     return ret

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.contents})'


class MyList(HasContentsMixin[list], UserList):  # type: ignore[misc]
    ...


class MyDict(HasContentsMixin[dict], UserDict):  # type: ignore[misc]
    ...


def test_weak_key_ref_container() -> None:
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


def test_weak_key_ref_container_clear() -> None:
    weak_key_ref_container = WeakKeyRefContainer[MyList, SomeObject]()

    a_list = MyList([1, 3, 5])
    b_list = MyList([a_list])
    weak_key_ref_container[a_list] = SomeObject('a_list')
    weak_key_ref_container[b_list] = SomeObject('b_list')

    assert len(weak_key_ref_container) == 2

    weak_key_ref_container.clear()

    assert len(weak_key_ref_container) == 0


def _take_snapshot(snapshot_holder: IsSnapshotHolder, obj: HasContents) -> None:
    snapshot_holder.take_snapshot_setup()
    snapshot_holder.take_snapshot(obj)
    snapshot_holder.take_snapshot_teardown()


def test_snapshot_holder_all_are_empty_and_clear() -> None:
    snapshot_holder = SnapshotHolder[MyList, list]()
    assert snapshot_holder.all_are_empty()

    my_list = MyList([123, 234])

    snapshot_holder.take_snapshot(my_list)
    assert not snapshot_holder.all_are_empty()
    assert len(snapshot_holder) == 1

    snapshot_holder.clear()
    assert snapshot_holder.all_are_empty()

    my_other_list = MyList([234, 345])

    snapshot_holder.take_snapshot(my_other_list)
    assert not snapshot_holder.all_are_empty()
    assert len(snapshot_holder) == 1

    id_my_other_list_contents = id(my_other_list.contents)

    del my_other_list

    assert not snapshot_holder.all_are_empty()
    assert len(snapshot_holder) == 0

    snapshot_holder.schedule_deepcopy_content_ids_for_deletion(id_my_other_list_contents)
    snapshot_holder.delete_scheduled_deepcopy_content_ids()

    assert snapshot_holder.all_are_empty()

    something_else = [2, 3, 4]
    snapshot_holder.take_snapshot(my_list)
    snapshot_holder.schedule_deepcopy_content_ids_for_deletion(
        *[id(my_list.contents), id(something_else)])

    del my_list
    snapshot_holder.delete_scheduled_deepcopy_content_ids()

    assert snapshot_holder.all_are_empty()


# TODO: Refactor into smaller tests
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

    _take_snapshot(snapshot_holder, my_list)

    assert my_list in snapshot_holder
    assert snapshot_holder.get(my_list) is snapshot_holder[my_list]
    assert isinstance(snapshot_holder[my_list], SnapshotWrapper)

    snapshot = snapshot_holder[my_list]
    assert snapshot.id == id(my_list)
    assert snapshot.taken_of_same_obj(my_list) is True

    assert snapshot.snapshot == my_list.contents
    assert snapshot.differs_from(my_list) is False

    assert id(snapshot.snapshot) != id(my_list)

    assert snapshot.taken_of_same_obj(copy(my_list)) is False
    assert snapshot.differs_from(copy(my_list)) is False

    my_other_list = MyList([my_list])
    my_list.append(7)
    assert snapshot.taken_of_same_obj(my_list) is True
    assert snapshot.differs_from(my_list) is True
    assert my_list == MyList([1, 3, 5, 7])
    assert my_other_list == MyList([[1, 3, 5, 7]])

    my_list_from_snapshot = snapshot.snapshot
    assert my_list_from_snapshot == [1, 3, 5]

    # the snapshot is a (preferably deep) copy of the old object
    assert my_list_from_snapshot is not my_list.contents

    my_dict = MyDict({1: 2, 3: 4})

    my_dict[5] = my_list_from_snapshot
    assert my_dict == MyDict({1: 2, 3: 4, 5: [1, 3, 5]})

    assert my_dict not in snapshot_holder
    _take_snapshot(snapshot_holder, my_dict)
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
    snapshot_holder = SnapshotHolder['MyMemoDeletingList', list | dict]()

    # def finalize(contents_id: int) -> None:
    #     print(f'finalize() called for {contents_id}')
    #     if snapshot_holder is not None:
    #         # self_id = id(self)
    #         # obj.contents = []
    #         try:
    #             # snapshot_holder.recursively_remove_deleted_obj_from_deepcopy_memo(contents_id)
    #             snapshot_holder.schedule_deepcopy_content_ids_for_deletion(contents_id)
    #         except (AttributeError) as exp:
    #             print(exp)
    #             print(snapshot_holder._deepcopy_memo)

    class MyMemoDeletingList(MyList):
        def __init__(self, contents: list) -> None:
            super().__init__(contents)
            # weakref.finalize(self, finalize, contents_id=id(self.contents))

        def __del__(self):
            contents_id = id(self.contents)
            # print(f'__del__ called for {contents_id}')
            self.contents = Undefined
            if snapshot_holder is not None:
                snapshot_holder.schedule_deepcopy_content_ids_for_deletion(contents_id)

    class MyPydanticModel(BaseModel):
        my_list: MyMemoDeletingList

        class Config:
            arbitrary_types_allowed = True

    def _inner_test_snapshot_deepcopy_reuse_objects(
            snapshot_holder: SnapshotHolder[MyMemoDeletingList, list | dict]) -> None:

        inner = MyMemoDeletingList([2, 4])
        middle = MyMemoDeletingList([{1, 3}, inner])
        outer = MyMemoDeletingList([0, MyPydanticModel(my_list=middle), 5])

        _take_snapshot(snapshot_holder, outer)
        _take_snapshot(snapshot_holder, middle)
        _take_snapshot(snapshot_holder, inner)

        assert type(outer[1].my_list[-1]) is type(middle[-1]) is type(inner) is MyMemoDeletingList
        assert id(outer[1].my_list[-1]) == id(middle[-1]) == id(inner)

        assert type(snapshot_holder[outer].snapshot[1].my_list[-1]) \
               is type(snapshot_holder[middle].snapshot[-1]) \
               is MyMemoDeletingList
        assert id(snapshot_holder[outer].snapshot[1].my_list[-1]) \
               == id(snapshot_holder[middle].snapshot[-1])

        assert type(outer[1].my_list[-1].contents) is type(middle[-1].contents) is type(
            inner.contents) is list
        assert id(outer[1].my_list[-1].contents) == id(middle[-1].contents) == id(inner.contents)

        assert type(snapshot_holder[outer].snapshot[1].my_list[-1].contents) \
               is type(snapshot_holder[middle].snapshot[-1].contents) \
               is type(snapshot_holder[inner].snapshot) \
               is list
        assert id(snapshot_holder[outer].snapshot[1].my_list[-1].contents) \
               == id(snapshot_holder[middle].snapshot[-1].contents) \
               == id(snapshot_holder[inner].snapshot)

        assert type(outer[1].my_list.contents) is type(middle.contents) is list
        assert id(outer[1].my_list.contents) == id(middle.contents)

        assert type(snapshot_holder[outer].snapshot[1].my_list.contents) \
               is type(snapshot_holder[middle].snapshot) \
               is list
        assert id(snapshot_holder[outer].snapshot[1].my_list.contents) \
               == id(snapshot_holder[middle].snapshot)

    # snapshot_holder = SnapshotHolder[MyMemoDeletingList, list]()
    _inner_test_snapshot_deepcopy_reuse_objects(snapshot_holder)
    snapshot_holder.delete_scheduled_deepcopy_content_ids()
    assert len(snapshot_holder.get_deepcopy_content_ids()) == 0


def test_snapshot_deepcopy_exception_cleanup() -> None:
    class Dynamite:
        def __deepcopy__(self, memo={}):
            memo[id(memo)].append(self)
            memo[id(self)] = copy(self)
            raise RuntimeError('Boom!')

    class DynamiteCrate(HasContentsMixin[Dynamite]):
        def __init__(self, data: Dynamite) -> None:
            self.data = data

    snapshot_holder = SnapshotHolder[DynamiteCrate | MyList, Dynamite | list]()

    my_list = MyList([1, 3, 5])
    assert snapshot_holder.all_are_empty()

    _take_snapshot(snapshot_holder, my_list)

    assert len(snapshot_holder) == 1
    assert snapshot_holder.get_deepcopy_content_ids() == SetDeque((id(my_list.contents),))
    # assert len(snapshot_holder._deepcopy_memo._keep_alive_dict) == 1

    try:
        dynamite_crate = DynamiteCrate(Dynamite())
        _take_snapshot(snapshot_holder, dynamite_crate)
    except RuntimeError:
        pass

    assert len(snapshot_holder) == 1
    assert snapshot_holder.get_deepcopy_content_ids() == SetDeque((id(my_list.contents),))
    # assert len(snapshot_holder._deepcopy_memo._keep_alive_dict) == 1


def test_snapshot_holder_deepcopy_memo_status_delete_and_clear() -> None:
    snapshot_holder = SnapshotHolder[MyList, list | dict]()

    my_first_list = MyList([1, 3, 5])
    my_second_list = MyList([2, 4, 6])
    my_third_list = MyList([my_second_list, my_second_list])

    content_id_first_list = id(my_first_list.contents)
    content_id_second_list = id(my_second_list.contents)
    content_id_third_list = id(my_third_list.contents)

    _take_snapshot(snapshot_holder, my_first_list)
    _take_snapshot(snapshot_holder, my_third_list)

    assert len(snapshot_holder) == 2
    assert snapshot_holder.get_deepcopy_content_ids() == SetDeque((
        content_id_first_list,
        content_id_third_list,
    ))
    assert snapshot_holder.get_deepcopy_content_ids_scheduled_for_deletion() == SetDeque()

    snapshot_holder.schedule_deepcopy_content_ids_for_deletion(content_id_first_list)

    assert len(snapshot_holder) == 2
    assert snapshot_holder.get_deepcopy_content_ids() == SetDeque((
        content_id_first_list,
        content_id_third_list,
    ))
    assert snapshot_holder.get_deepcopy_content_ids_scheduled_for_deletion() == SetDeque(
        (content_id_first_list,))

    # Duplicates are ignored
    snapshot_holder.schedule_deepcopy_content_ids_for_deletion(content_id_first_list)

    assert len(snapshot_holder) == 2
    assert snapshot_holder.get_deepcopy_content_ids() == SetDeque((
        content_id_first_list,
        content_id_third_list,
    ))
    assert snapshot_holder.get_deepcopy_content_ids_scheduled_for_deletion() == SetDeque(
        (content_id_first_list,))

    # Not deleted if there are still references to the content object. Object is still
    # scheduled for deletion, just in case
    snapshot_holder.delete_scheduled_deepcopy_content_ids()

    assert len(snapshot_holder) == 2
    assert snapshot_holder.get_deepcopy_content_ids() == SetDeque((
        content_id_first_list,
        content_id_third_list,
    ))
    assert snapshot_holder.get_deepcopy_content_ids_scheduled_for_deletion() == SetDeque(
        (content_id_first_list,))

    # Automatic deletion of snapshots from snapshot_holder, but no automatic deletion of
    # objects from deepcopy_memo, even if already scheduled for deletion
    del my_first_list

    gc.collect()

    assert len(snapshot_holder) == 1
    assert snapshot_holder.get_deepcopy_content_ids() == SetDeque((
        content_id_first_list,
        content_id_third_list,
    ))
    assert snapshot_holder.get_deepcopy_content_ids_scheduled_for_deletion() == SetDeque(
        (content_id_first_list,))

    # Delete scheduled object at controlled places
    snapshot_holder.delete_scheduled_deepcopy_content_ids()

    assert len(snapshot_holder) == 1
    assert snapshot_holder.get_deepcopy_content_ids() == SetDeque((content_id_third_list,))
    assert snapshot_holder.get_deepcopy_content_ids_scheduled_for_deletion() == SetDeque()

    # Content ids for non-snapshot objects are ignored, even if cached in the deepcopy_memo, here
    # as a result of deepcopy() of my_third_list
    snapshot_holder.schedule_deepcopy_content_ids_for_deletion(content_id_second_list)

    assert len(snapshot_holder) == 1
    assert snapshot_holder.get_deepcopy_content_ids() == SetDeque((content_id_third_list,))
    assert snapshot_holder.get_deepcopy_content_ids_scheduled_for_deletion() == SetDeque()

    # Clear() should remove all snapshots, deepcopy_memo objects and scheduled deletions
    snapshot_holder.schedule_deepcopy_content_ids_for_deletion(content_id_third_list)

    assert len(snapshot_holder) == 1
    assert snapshot_holder.get_deepcopy_content_ids() == SetDeque((content_id_third_list,))
    assert snapshot_holder.get_deepcopy_content_ids_scheduled_for_deletion() == SetDeque(
        (content_id_third_list,))

    snapshot_holder.clear()

    assert len(snapshot_holder) == 0
    assert snapshot_holder.get_deepcopy_content_ids() == SetDeque()
    assert snapshot_holder.get_deepcopy_content_ids_scheduled_for_deletion() == SetDeque()


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
