from copy import deepcopy
from typing import Any
import weakref

import pytest
from typing_extensions import TypeAlias

from omnipy import Model
import omnipy.util._pydantic as pyd
from omnipy.util.memo import RefCountMemoDict
from omnipy.util.setdeque import SetDeque

from .helpers.classes import SomeObject

BasicType: TypeAlias = list | tuple | dict | set | str | float | int | complex | bool | SomeObject


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
        def __init__(self, content: object) -> None:
            self.content = content

        def __del__(self) -> None:
            content_id = id(self.content)

            # print(f'__del__() called for {self} (id(self.content)={content_id})')
            # print(ref_count_memo_dict)

            self.content = pyd.Undefined
            ref_count_memo_dict.recursively_remove_deleted_objs(SetDeque((content_id,)))

        def __repr__(self) -> str:
            return f'MyClass({self.content})'

        def __eq__(self, other):
            if isinstance(other, MyClass):
                return self.content == other.content
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

            for obj in (a_list, c_set, b_tuple, d_dict, e_obj.content, f_obj.content):
                _deepcopy_obj_with_memodict(ref_count_memo_dict, obj)

            id_a = id(a_list)
            id_b = id(b_tuple)
            id_c = id(c_set)
            id_d = id(d_dict)
            id_e_c = id(e_obj.content)
            id_f_c = id(f_obj.content)
            all_ids = (id_a, id_b, id_c, id_d, id_e_c, id_f_c)

            assert ref_count_memo_dict[id_a] == a_list
            assert id_b not in ref_count_memo_dict  # tuples are not memoized
            assert ref_count_memo_dict[id_c] == c_set
            assert ref_count_memo_dict[id_d] == d_dict
            assert ref_count_memo_dict[id_e_c] == e_obj.content
            assert ref_count_memo_dict[id_f_c] == f_obj.content

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
        def _parse_data(cls, data):
            return data.upper()

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
                  'validation of Model.content is always run before taking a snapshot if the '
                  'content has changed, returning a new object to be taken snapshot of. '
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
