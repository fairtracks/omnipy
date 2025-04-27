from collections import UserDict, UserList

import pytest

from omnipy.util.weak import WeakKeyRefContainer

from .helpers.classes import SomeObject


class MyList(UserList):
    ...


class MyDict(UserDict):
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
