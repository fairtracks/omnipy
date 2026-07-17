from typing import Any, Callable, cast, Generic, ParamSpec

import pytest
from typing_extensions import TypeVar

from omnipy.util.callable_decorator import callable_decorator_cls

from ..helpers.functions import assert_func_wrapper

# Note:
#
# Due to the following bug:
#
# https://github.com/python/mypy/issues/3135
#
# mypy is not correctly considering the types of the class decorator. As a consequence, it reports
# a bunch of errors on MockClass and MockClassNotCallableArg that should clear up once bug is fixed

CallP = ParamSpec('CallP')
RetT = TypeVar('RetT', bound=dict)


class MockClassBase(Generic[CallP, RetT]):
    def __init__(self, func: Callable[CallP, RetT], *args: object, **kwargs: object) -> None:
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *args: CallP.args, **kwargs: CallP.kwargs) -> RetT:
        return cast(RetT, dict(call_args=args, call_kwargs=kwargs))


class NoConfigMockClassBase(MockClassBase[CallP, RetT]):
    def __init__(self, func: Callable[CallP, RetT]) -> None:
        super().__init__(func)


class KeywordConfigMockClassBase(MockClassBase[CallP, RetT]):
    def __init__(self, func: Callable[CallP, RetT], *, param: int, other: bool) -> None:
        super().__init__(func, param=param, other=other)


class PositionalKeywordConfigMockClassBase(MockClassBase[CallP, RetT]):
    def __init__(
        self,
        func: Callable[CallP, RetT],
        number: int,
        enabled: bool,
        *,
        param: int,
        other: bool,
    ) -> None:
        super().__init__(func, number, enabled, param=param, other=other)


class CallablePositionalKeywordConfigMockClassBase(MockClassBase[CallP, RetT]):
    def __init__(
        self,
        func: Callable[CallP, RetT],
        init_callable: Callable[[], None],
        number: int,
        enabled: bool,
        *,
        param: int,
        other: bool,
    ) -> None:
        super().__init__(func, init_callable, number, enabled, param=param, other=other)


NoConfigMockClass = callable_decorator_cls(NoConfigMockClassBase)
KeywordConfigMockClass = callable_decorator_cls(KeywordConfigMockClassBase)
PositionalKeywordConfigMockClass = callable_decorator_cls(PositionalKeywordConfigMockClassBase)
CallablePositionalKeywordConfigMockClass = callable_decorator_cls(
    CallablePositionalKeywordConfigMockClassBase)


def test_fail_plain_decorator_not_callable_arg() -> None:
    @callable_decorator_cls  # type: ignore[arg-type]
    class MockClassNoCallableArg:
        def __init__(self) -> None:
            ...

    with pytest.raises(TypeError):

        @MockClassNoCallableArg  # type: ignore[call-arg]
        def my_func(*args: object, **kwargs: object) -> dict[str, Any]:
            return dict(args=args, kwargs=kwargs)


def _assert_func_decoration(my_func):
    assert_func_wrapper(my_func, my_func.func)


def _assert_call_func(my_func):
    """Provide assert call func for test reuse."""
    assert my_func(1, 'b', c=True) == dict(call_args=(1, 'b'), call_kwargs=dict(c=True))


def test_plain_decorator() -> None:
    @NoConfigMockClass  # type: ignore[call-arg]
    def my_func_1(*args: object, **kwargs: object) -> dict[str, object]:
        return dict(args=args, kwargs=kwargs)

    decorated_my_func_1 = my_func_1

    assert type(decorated_my_func_1) is NoConfigMockClass
    _assert_func_decoration(decorated_my_func_1)
    _assert_call_func(decorated_my_func_1)

    assert decorated_my_func_1.args == ()  # type:ignore [attr-defined]
    assert decorated_my_func_1.kwargs == {}  # type:ignore [attr-defined]
    assert (decorated_my_func_1.func(1, 'b', c=True)  # type:ignore [attr-defined]
            == dict(args=(1, 'b'), kwargs=dict(c=True)))


def test_plain_decorator_parentheses() -> None:
    @NoConfigMockClass()
    def my_func_2(*args: object, **kwargs: object) -> dict[str, object]:
        return dict(args=args, kwargs=kwargs)

    assert type(my_func_2) is NoConfigMockClass
    _assert_func_decoration(my_func_2)  # noqa
    _assert_call_func(my_func_2)

    assert my_func_2.args == ()
    assert my_func_2.kwargs == {}
    assert my_func_2.func(1, 'b', c=True) == dict(args=(1, 'b'), kwargs=dict(c=True))


def test_decorator_with_kwargs() -> None:
    @KeywordConfigMockClass(param=123, other=True)
    def my_func_3(*args: object, **kwargs: object) -> dict[str, object]:
        return dict(args=args, kwargs=kwargs)

    assert type(my_func_3) is KeywordConfigMockClass
    _assert_func_decoration(my_func_3)
    _assert_call_func(my_func_3)

    assert my_func_3.args == ()
    assert my_func_3.kwargs == dict(param=123, other=True)
    assert my_func_3.func(1, 'b', c=True) == dict(args=(1, 'b'), kwargs=dict(c=True))


def test_decorator_with_args_and_kwargs() -> None:
    @PositionalKeywordConfigMockClass(123, True, param=123, other=True)
    def my_func_4(*args: object, **kwargs: object) -> dict[str, object]:
        return dict(args=args, kwargs=kwargs)

    assert type(my_func_4) is PositionalKeywordConfigMockClass
    _assert_func_decoration(my_func_4)
    _assert_call_func(my_func_4)

    assert my_func_4.args == (123, True)
    assert my_func_4.kwargs == dict(param=123, other=True)
    assert my_func_4.func(1, 'b', c=True) == dict(args=(1, 'b'), kwargs=dict(c=True))


def test_decorator_with_args_and_kwargs_first_arg_func() -> None:
    def other_func():
        pass

    @CallablePositionalKeywordConfigMockClass(other_func, 123, True, param=123, other=True)
    def my_func_5(*args: object, **kwargs: object) -> dict[str, Any]:
        return dict(args=args, kwargs=kwargs)

    assert type(my_func_5) is CallablePositionalKeywordConfigMockClass
    _assert_func_decoration(my_func_5)
    _assert_call_func(my_func_5)

    assert my_func_5.args == (other_func, 123, True)
    assert my_func_5.kwargs == dict(param=123, other=True)
    assert my_func_5.func(1, 'b', c=True) == dict(args=(1, 'b'), kwargs=dict(c=True))


def test_double_decorator_with_args_and_kwargs() -> None:
    @PositionalKeywordConfigMockClass(234, False, param=234, other=False)
    @PositionalKeywordConfigMockClass(123, True, param=123, other=True)
    def my_func_6(*args: object, **kwargs: object) -> dict[str, Any]:
        return dict(args=args, kwargs=kwargs)

    assert type(my_func_6) is PositionalKeywordConfigMockClass
    _assert_func_decoration(my_func_6)
    _assert_call_func(my_func_6)

    assert my_func_6.args == (234, False)
    assert my_func_6.kwargs == dict(param=234, other=False)
    assert my_func_6.func(1, 'b', c=True) == dict(call_args=(1, 'b'), call_kwargs=dict(c=True))


def test_fail_decorator_with_single_callable_arg() -> None:
    @callable_decorator_cls
    class MockClassSingleCallableArg:
        def __init__(self, decorated_func: Callable, other_func: Callable) -> None:
            ...

    def extra_func():
        ...

    with pytest.raises(TypeError):

        @MockClassSingleCallableArg(extra_func)  # type: ignore[call-arg, operator]
        def my_func(*args: object, **kwargs: object) -> dict[str, Any]:
            return dict(args=args, kwargs=kwargs)


def my_fancy_func(*args: int | str, **kwargs: bool) -> dict[str, Any]:
    """
    Documentation of myfunc()
    """
    return dict(args=args, kwargs=kwargs)


def test_decorator_as_function_fancy_func() -> None:
    my_func = NoConfigMockClass()(my_fancy_func)

    assert type(my_func) is NoConfigMockClass
    _assert_func_decoration(my_func)
    _assert_call_func(my_func)

    assert my_func.args == ()
    assert my_func.kwargs == {}
    assert my_func.func(1, 'b', c=True) == dict(args=(1, 'b'), kwargs=dict(c=True))


def test_decorator_as_function_callable_class() -> None:
    class MyCallableClass:
        def __call__(self, *args: object, **kwargs: object) -> dict[str, object]:
            return dict(args=args, kwargs=kwargs)

    my_callable_obj = MyCallableClass()
    my_func = NoConfigMockClass()(my_callable_obj)

    assert type(my_func) is NoConfigMockClass
    _assert_call_func(my_func)

    assert my_func.args == ()
    assert my_func.kwargs == {}
    assert my_func.func() != my_func
    assert my_func.func is my_callable_obj
    assert my_func.func() == dict(args=(), kwargs={})


def test_decorator_with_single_callable_arg_disambiguation_hook() -> None:
    class MockClassWithHookBase:
        def __init__(self, func: Callable[..., dict[str, object]], *args: object,
                     **kwargs: object) -> None:
            self.func = func
            self.args = args
            self.kwargs = kwargs

    def _single_callable_arg_is_decorator_arg(arg: object) -> bool:
        return isinstance(arg, type)

    MockClassWithHook = callable_decorator_cls(
        MockClassWithHookBase,
        single_callable_arg_is_decorator_arg=_single_callable_arg_is_decorator_arg)

    class MyCallableClass:
        def __call__(self, *args: object, **kwargs: object) -> dict[str, object]:
            return dict(args=args, kwargs=kwargs)

    def my_func(*args: object, **kwargs: object) -> dict[str, object]:
        return dict(args=args, kwargs=kwargs)

    decorator = MockClassWithHook(MyCallableClass)
    decorated_func = decorator(my_func)

    assert type(decorated_func) is MockClassWithHook
    assert decorated_func.func is my_func
    assert decorated_func.args == (MyCallableClass,)
    assert decorated_func.kwargs == {}


def test_decorator_as_function_fancy_func_args_kwargs() -> None:
    my_func = PositionalKeywordConfigMockClass(123, True, param=123, other=True)(my_fancy_func)

    assert type(my_func) is PositionalKeywordConfigMockClass
    _assert_func_decoration(my_func)
    _assert_call_func(my_func)

    assert my_func.args == (123, True)
    assert my_func.kwargs == dict(param=123, other=True)
    assert my_func.func(1, 'b', c=True) == dict(args=(1, 'b'), kwargs=dict(c=True))


def test_fail_decorator_as_function_no_args_no_func() -> None:
    my_func = NoConfigMockClass()

    assert type(my_func) is NoConfigMockClass

    with pytest.raises(TypeError):
        my_func()  # type:ignore [call-arg]
    with pytest.raises(AttributeError):
        assert my_func.args == ()  # type:ignore [attr-defined]
    with pytest.raises(AttributeError):
        assert my_func.kwargs == {}  # type:ignore [attr-defined]


def test_fail_decorator_as_function_args_and_kwargs_no_func() -> None:
    my_func = PositionalKeywordConfigMockClass(123, True, param=123, other=True)

    assert type(my_func) is PositionalKeywordConfigMockClass

    with pytest.raises(TypeError):
        my_func()  # type:ignore [call-arg]
    with pytest.raises(AttributeError):
        assert my_func.args == ()  # type:ignore [attr-defined]
    with pytest.raises(AttributeError):
        assert my_func.kwargs == {}  # type:ignore [attr-defined]
