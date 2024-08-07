from collections import deque
from contextlib import suppress
from itertools import chain
import sys
from timeit import timeit

import pytest

from omnipy.util.setdeque import SetDeque


def test_setdeque_init_getitem_empty() -> None:
    setdeque_empty = SetDeque[str]()
    assert isinstance(setdeque_empty, deque)
    assert len(setdeque_empty) == 0
    with pytest.raises(IndexError):
        setdeque_empty[0]


def test_setdeque_append() -> None:
    setdeque = SetDeque[int]()

    setdeque.append(2)
    assert setdeque == SetDeque[int]([2])

    setdeque.append(3)
    assert setdeque == SetDeque[int]([2, 3])

    setdeque.append(3)
    setdeque.append(2)
    assert setdeque == SetDeque[int]([2, 3])

    setdeque.append(1)
    setdeque.append(2)
    setdeque.append(3)
    assert setdeque == SetDeque[int]([2, 3, 1])


def _assert_len3_setdeque_unique_vals(setdeque: SetDeque[int]) -> None:
    def _assert_len3_setdeque(setdeque: SetDeque[int]) -> None:
        assert len(setdeque) == 3

        assert setdeque[0] == 1
        assert setdeque[1] == 2
        assert setdeque[2] == 3

        with pytest.raises(IndexError):
            setdeque[3]

    _assert_len3_setdeque(setdeque)

    setdeque.append(1)
    setdeque.append(2)
    setdeque.append(3)

    _assert_len3_setdeque(setdeque)

    setdeque.append(0)
    assert setdeque[-1] == 0


def test_setdeque_init_getitem_iterator() -> None:
    _assert_len3_setdeque_unique_vals(SetDeque[int]([1, 2, 3, 1, 2, 3]))
    _assert_len3_setdeque_unique_vals(SetDeque[int]([0, 1, 2, 3, 0, 1, 2, 3], maxlen=3))
    _assert_len3_setdeque_unique_vals(SetDeque[int](chain(range(1, 4), range(1, 4))))
    _assert_len3_setdeque_unique_vals(SetDeque[int](chain(range(4), range(4)), maxlen=3))
    _assert_len3_setdeque_unique_vals(SetDeque[int]([1, 2, 3, 1, 2, 3].__iter__()))
    _assert_len3_setdeque_unique_vals(SetDeque[int]([0, 1, 2, 3, 0, 1, 2, 3].__iter__(), maxlen=3))


def test_setdeque_appendleft() -> None:
    setdeque = SetDeque[str]()

    setdeque.appendleft('b')
    assert setdeque == SetDeque[int](['b'])

    setdeque.appendleft('c')
    assert setdeque == SetDeque[int](['c', 'b'])

    setdeque.appendleft('c')
    setdeque.appendleft('b')
    assert setdeque == SetDeque[int](['c', 'b'])

    setdeque.appendleft('a')
    setdeque.appendleft('b')
    setdeque.appendleft('c')
    assert setdeque == SetDeque[int](['a', 'c', 'b'])


def test_setdeque_extend() -> None:
    setdeque = SetDeque[str]()

    setdeque.extend(['b'])
    assert setdeque == SetDeque[int](['b'])

    setdeque.extend(['c', 'd'])
    assert setdeque == SetDeque[int](['b', 'c', 'd'])

    setdeque.extend(['c', 'e', 'f', 'g', 'b', 'h'])
    assert setdeque == SetDeque[int](['b', 'c', 'd', 'e', 'f', 'g', 'h'])

    setdeque.extend(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])
    assert setdeque == SetDeque[int](['b', 'c', 'd', 'e', 'f', 'g', 'h', 'a'])


def test_setdeque_extendleft() -> None:
    setdeque = SetDeque[int]()

    setdeque.extendleft([2])
    assert setdeque == SetDeque[int]([2])

    setdeque.extendleft([1, 3])
    assert setdeque == SetDeque[int]([3, 1, 2])

    setdeque.extendleft([1, 2, 3, 4, 5, 6, 7])
    assert setdeque == SetDeque[int]([7, 6, 5, 4, 3, 1, 2])

    setdeque.extendleft([1, 2, 3, 4, 5, 6, 7, 8])
    assert setdeque == SetDeque[int]([8, 7, 6, 5, 4, 3, 1, 2])


def test_setdeque_insert() -> None:
    setdeque = SetDeque[int]()

    setdeque.insert(0, 4)
    assert setdeque == SetDeque[int]([4])

    setdeque.insert(0, 1)
    setdeque.insert(1, 2)
    assert setdeque == SetDeque[int]([1, 2, 4])

    setdeque.insert(-1, 3)
    assert setdeque == SetDeque[int]([1, 2, 3, 4])

    setdeque.insert(4, 5)
    assert setdeque == SetDeque[int]([1, 2, 3, 4, 5])

    setdeque.insert(40, 6)
    assert setdeque == SetDeque[int]([1, 2, 3, 4, 5, 6])

    setdeque.insert(-40, 0)
    assert setdeque == SetDeque[int]([0, 1, 2, 3, 4, 5, 6])

    setdeque.insert(0, 4)
    setdeque.insert(1, 5)
    setdeque.insert(2, 6)
    setdeque.insert(3, 0)
    setdeque.insert(4, 1)
    setdeque.insert(5, 2)
    setdeque.insert(6, 3)
    assert setdeque == SetDeque[int]([0, 1, 2, 3, 4, 5, 6])


def test_setdeque_setitem() -> None:
    setdeque_empty = SetDeque[int]()

    with pytest.raises(IndexError):
        setdeque_empty[0] = 1

    setdeque = SetDeque[int]([1, 2, 3])

    setdeque[0] = 4
    assert setdeque == SetDeque[int]([4, 2, 3])

    setdeque[-1] = 1
    assert setdeque == SetDeque[int]([4, 2, 1])

    setdeque[2] = 3
    assert setdeque == SetDeque[int]([4, 2, 3])

    setdeque[1] = 3
    assert setdeque == SetDeque[int]([4, 2, 3])

    setdeque[2] = 4
    assert setdeque == SetDeque[int]([4, 2, 3])

    with pytest.raises(IndexError):
        setdeque[3] = 5

    with pytest.raises(IndexError):
        setdeque[-4] = 5


def test_setdeque_add_iadd() -> None:
    setdeque_empty = SetDeque[str]()

    setdeque_1 = SetDeque[str](['a', 'b', 'c'])

    assert setdeque_empty + setdeque_1 == setdeque_1 + setdeque_empty == \
           SetDeque[str](['a', 'b', 'c'])
    assert setdeque_empty == SetDeque[str]()
    assert setdeque_1 == SetDeque[str](['a', 'b', 'c'])

    setdeque_empty += setdeque_1
    assert setdeque_empty == setdeque_1 == SetDeque[str](['a', 'b', 'c'])

    setdeque_2 = SetDeque[str](['b', 'd', 'e', 'c'])
    assert setdeque_1 + setdeque_2 == SetDeque[str](['a', 'b', 'c', 'd', 'e'])
    assert setdeque_2 + setdeque_1 == SetDeque[str](['b', 'd', 'e', 'c', 'a'])
    assert setdeque_1 == SetDeque[str](['a', 'b', 'c'])
    assert setdeque_2 == SetDeque[str](['b', 'd', 'e', 'c'])

    setdeque_1 += setdeque_2
    assert setdeque_1 == SetDeque[str](['a', 'b', 'c', 'd', 'e'])
    assert setdeque_2 == SetDeque[str](['b', 'd', 'e', 'c'])

    setdeque_2 += setdeque_1
    assert setdeque_2 == SetDeque[str](['b', 'd', 'e', 'c', 'a'])


def test_setdeque_add_iadd_other_types() -> None:
    setdeque_empty = SetDeque[str]()

    class OtherClass:
        def __radd__(self, other):
            return 42

    with pytest.raises(TypeError):
        setdeque_empty + 1  # type: ignore[operator]

    with pytest.raises(TypeError):
        setdeque_empty += 1  # type: ignore[arg-type]

    assert setdeque_empty + OtherClass() == 42

    with pytest.raises(TypeError):
        setdeque_empty += OtherClass()  # type: ignore[arg-type]

    with pytest.raises(TypeError):
        setdeque_empty + 'abc'  # type: ignore[operator]

    setdeque_empty += 'abc'
    assert setdeque_empty == SetDeque[str](['a', 'b', 'c'])


def test_setdeque_pop() -> None:
    setdeque = SetDeque[int]([1, 2, 3])

    assert setdeque.pop() == 3
    assert setdeque == SetDeque[int]([1, 2])

    setdeque.append(3)
    assert setdeque == SetDeque[int]([1, 2, 3])

    assert setdeque.pop() == 3
    assert setdeque.pop() == 2
    assert setdeque.pop() == 1
    assert setdeque == SetDeque[int]()

    with pytest.raises(IndexError):
        setdeque.pop()


def test_setdeque_popleft() -> None:
    setdeque = SetDeque[int]([1, 2, 3])

    assert setdeque.popleft() == 1
    assert setdeque == SetDeque[int]([2, 3])

    setdeque.append(1)
    assert setdeque == SetDeque[int]([2, 3, 1])

    assert setdeque.popleft() == 2
    assert setdeque.popleft() == 3
    assert setdeque.popleft() == 1
    assert setdeque == SetDeque[int]()

    with pytest.raises(IndexError):
        setdeque.popleft()


def test_setdeque_remove() -> None:
    setdeque = SetDeque[int]([1, 2, 3])

    with pytest.raises(ValueError):
        setdeque.remove(4)

    setdeque.remove(2)
    assert setdeque == SetDeque[int]([1, 3])

    with pytest.raises(ValueError):
        setdeque.remove(2)

    setdeque.append(2)
    assert setdeque == SetDeque[int]([1, 3, 2])

    setdeque.remove(2)
    assert setdeque == SetDeque[int]([1, 3])

    with pytest.raises(ValueError):
        setdeque.remove(2)


def test_setdeque_delitem() -> None:
    setdeque = SetDeque[int]([1, 2, 3])

    with pytest.raises(IndexError):
        del setdeque[3]

    with pytest.raises(IndexError):
        del setdeque[-4]

    del setdeque[0]
    assert setdeque == SetDeque[int]([2, 3])

    setdeque.append(1)
    assert setdeque == SetDeque[int]([2, 3, 1])

    del setdeque[-1]
    assert setdeque == SetDeque[int]([2, 3])

    del setdeque[0]
    del setdeque[0]
    assert setdeque == SetDeque[int]()

    with pytest.raises(IndexError):
        del setdeque[0]

    setdeque.extend([1, 2, 3])
    assert setdeque == SetDeque[int]([1, 2, 3])


def test_setdeque_clear() -> None:
    setdeque = SetDeque[int]([1, 2, 3])

    setdeque.clear()
    assert setdeque == SetDeque[int]()

    setdeque.extend([1, 2, 3])
    assert setdeque == SetDeque[int]([1, 2, 3])


def test_setdeque_copy_deepcopy() -> None:
    class MyClass:
        def __init__(self, a: int, b: str):
            self.a = a
            self.b = b

        def __hash__(self):
            return hash((self.a, self.b))

        def __eq__(self, other):
            return self.a == other.a and self.b == other.b

    my_obj_1 = MyClass(1, 'a')
    my_obj_2 = MyClass(2, 'b')

    setdeque = SetDeque[MyClass]([my_obj_1, my_obj_2])

    from copy import copy, deepcopy
    for setdeque_copy, deep in \
            [(setdeque.copy(), False), (copy(setdeque), False), (deepcopy(setdeque), True),]:
        assert setdeque_copy == setdeque
        assert setdeque_copy is not setdeque

        assert setdeque_copy[0] == setdeque[0]
        assert setdeque_copy[1] == setdeque[1]

        if deep:
            assert setdeque_copy[0] is not setdeque[0]
            assert setdeque_copy[1] is not setdeque[1]
        else:
            assert setdeque_copy[0] is setdeque[0]
            assert setdeque_copy[1] is setdeque[1]

        assert setdeque_copy == setdeque == SetDeque[int]([my_obj_1, my_obj_2])

        setdeque.append(my_obj_1)
        setdeque_copy.append(my_obj_2)
        assert setdeque_copy == setdeque == SetDeque[int]([my_obj_1, my_obj_2])


def test_setdeque_count() -> None:

    setdeque = SetDeque[int]()

    assert setdeque.count(1) == 0
    assert type(setdeque.count(1)) is int

    setdeque.extend([1, 2, 3, 1, 2, 3, 1, 2, 3])
    assert setdeque.count(1) == 1
    assert setdeque.count(2) == 1
    assert setdeque.count(3) == 1
    assert setdeque.count(4) == 0


def test_setdeque_count_speed() -> None:
    define_numbers = 'numbers = tuple(range(10000))'

    time_setdeque_count = timeit(
        stmt='tuple(setdeque.count(i + 1000) for i in numbers)',
        setup=f'{define_numbers}; setdeque = SetDeque(numbers)',
        number=100,
        globals=globals(),
    )

    time_set_contains = timeit(
        stmt='tuple(i + 1000 in set_compare for i in numbers)',
        setup=f'{define_numbers}; set_compare = set(numbers)',
        number=100,
        globals=globals(),
    )

    # `SetDeque.count()` seems to be between 2 and 3 times slower than `set.__contains__()` (for
    # some reason). Setting threshold ratio to 5 to make test more robust, as `deque.count()`
    # in any case is an order of magnitude slower

    print(time_setdeque_count, time_set_contains)
    assert time_setdeque_count < 5 * time_set_contains


def test_setdeque_index() -> None:
    setdeque = SetDeque[str]()

    with pytest.raises(ValueError):
        setdeque.index('a')

    setdeque.extend(['c', 'b', 'a'])
    assert setdeque.index('a') == 2
    assert setdeque.index('b') == 1
    assert setdeque.index('c') == 0

    with pytest.raises(ValueError):
        setdeque.index('c', 2)

    with pytest.raises(ValueError):
        setdeque.index('a', 0, 2)

    with pytest.raises(ValueError):
        setdeque.index('d')


def test_setdeque_index_missing_speed() -> None:
    # Surprisingly, the default implementation of `deque.index()` for missing values is faster than
    # a set-based implementation based on `__contains__`

    stmt_prefix = 'with suppress(ValueError): '
    define_numbers = 'numbers = tuple(range(10000))'

    time_setdeque_index = timeit(
        stmt=stmt_prefix + 'tuple(setdeque.index(i + 10000) for i in numbers)',
        setup=f'{define_numbers}; setdeque = SetDeque(numbers)',
        number=100,
        globals=globals(),
    )

    time_set_contains = timeit(
        stmt=stmt_prefix + 'tuple(i + 10000 in set_compare for i in numbers)',
        setup=f'{define_numbers}; set_compare = set(numbers)',
        number=100,
        globals=globals(),
    )

    assert time_setdeque_index < time_set_contains


def test_setdeque_contains() -> None:
    setdeque = SetDeque[int]([1, 2, 3])

    assert 0 not in setdeque
    assert 1 in setdeque

    assert 4 not in setdeque
    setdeque.append(4)
    assert 4 in setdeque

    setdeque.remove(1)
    assert 1 not in setdeque


def test_setdeque_contains_speed() -> None:
    define_numbers = 'numbers = tuple(range(10000))'
    stmt_template = 'tuple(i + 5000 in {} for i in numbers)'

    time_setdeque_contains = timeit(
        stmt=stmt_template.format('setdeque'),
        setup=f'{define_numbers}; setdeque = SetDeque(numbers)',
        number=100,
        globals=globals(),
    )
    time_set_contains = timeit(
        stmt=stmt_template.format('set_compare'),
        setup=f'{define_numbers}; set_compare = set(numbers)',
        number=100,
        globals=globals(),
    )

    # `SetDeque.__contains__()` seems to be between 2 and 3 times slower than `set.__contains__()`
    # (for some reason). Setting threshold ratio to 5 to make test more robust, as
    # `deque.__contains__()` in any case is an order of magnitude slower

    assert time_setdeque_contains < 5 * time_set_contains


def test_setdeque_mul_rmul() -> None:
    setdeque = SetDeque[int]([1, 2, 3])

    assert setdeque * 1 == 1 * setdeque == SetDeque[int]([1, 2, 3])
    assert setdeque * 2 == 2 * setdeque == SetDeque[int]([1, 2, 3])
    assert setdeque * 10 == 10 * setdeque == SetDeque[int]([1, 2, 3])

    assert setdeque * 0 == 0 * setdeque == SetDeque[int]()
    assert setdeque * -1 == -1 * setdeque == SetDeque[int]()
    assert setdeque * -15 == -15 * setdeque == SetDeque[int]()

    new_setdeque = setdeque * 0
    new_setdeque.append(1)
    assert new_setdeque == SetDeque[int]([1])

    newer_setdeque = -1 * new_setdeque
    newer_setdeque.append(1)
    assert newer_setdeque == SetDeque[int]([1])


def test_setdeque_imul() -> None:
    setdeque_1 = SetDeque[int]([1, 2, 3])

    setdeque_1 *= 1
    assert setdeque_1 == SetDeque[int]([1, 2, 3])

    setdeque_1 *= 2
    assert setdeque_1 == SetDeque[int]([1, 2, 3])

    setdeque_1 *= 15
    assert setdeque_1 == SetDeque[int]([1, 2, 3])

    setdeque_1 *= 0
    assert setdeque_1 == SetDeque[int]()
    setdeque_1.append(1)
    assert setdeque_1 == SetDeque[int]([1])

    setdeque_2 = SetDeque[int]([1, 2, 3])
    setdeque_2 *= -10
    assert setdeque_2 == SetDeque[int]()
    setdeque_2.append(3)
    assert setdeque_2 == SetDeque[int]([3])


def test_setdeque_repr() -> None:
    assert repr(SetDeque[int]()) == 'SetDeque[int]([])'
    assert repr(SetDeque[str](('a', 'b', 'c'))) == "SetDeque[str](['a', 'b', 'c'])"

    setdeque = SetDeque[int | str]((1, 2, 'a'), maxlen=2)
    assert repr(setdeque) == "SetDeque[int | str]([2, 'a'], maxlen=2)"

    del setdeque.__orig_class__  # type: ignore[attr-defined]
    assert repr(setdeque) == "SetDeque([2, 'a'], maxlen=2)"


def test_setdeque_sizeof() -> None:
    setdeque = SetDeque[int]([1, 2, 3])
    deque_compare = deque[int]([1, 2, 3])
    set_compare = set[int]([1, 2, 3])

    sizeof_setdeque = sys.getsizeof(setdeque)
    sizeof_deque = sys.getsizeof(deque_compare)
    sizeof_set = sys.getsizeof(set_compare)

    assert sizeof_setdeque > sizeof_deque + sizeof_set
