import asyncio
from contextlib import contextmanager
import inspect
from typing import Any, AsyncGenerator, Callable, NamedTuple, Protocol

import pytest
import pytest_cases as pc

from omnipy.util.callable_types import (callable_type_from_flags,
                                        CallableType,
                                        decorate_callable_by_type,
                                        decorate_result_by_type,
                                        get_callable_type)


class CallableTypeCase(NamedTuple):
    __test__ = False
    callable_type: CallableType.Literals
    create_call_func: Callable[[list[str]], Callable[..., Any]]
    call_arg: int
    expected_result: Any
    expected_events: list[str]


def _create_sync_callable(state: list[str]) -> Callable[[int], int]:
    def sync_func(value: int) -> int:
        state.append(f'call:{value}')
        return value + 1

    return sync_func


def _create_sync_generator_callable(state: list[str]) -> Callable[[int], Any]:
    def sync_generator_func(count: int):
        for num in range(count):
            state.append(f'yield:{num}')
            yield num

    return sync_generator_func


def _create_async_callable(state: list[str]) -> Callable[[int], Any]:
    async def async_func(value: int) -> int:
        state.append(f'call:{value}')
        return value + 1

    return async_func


def _create_async_generator_callable(state: list[str]) -> Callable[[int], Any]:
    async def async_generator_func(count: int):
        for num in range(count):
            state.append(f'yield:{num}')
            yield num

    return async_generator_func


@pc.case(id='sync', tags=['sync', 'function'])
def case_callable_sync() -> CallableTypeCase:
    return CallableTypeCase(
        callable_type=CallableType.SYNC_FUNCTION,
        create_call_func=_create_sync_callable,
        call_arg=4,
        expected_result=5,
        expected_events=['call:4'],
    )


@pc.case(id='sync_generator', tags=['sync', 'generator'])
def case_callable_sync_generator() -> CallableTypeCase:
    return CallableTypeCase(
        callable_type=CallableType.SYNC_GENERATOR,
        create_call_func=_create_sync_generator_callable,
        call_arg=3,
        expected_result=(0, 1, 2),
        expected_events=['yield:0', 'yield:1', 'yield:2'],
    )


@pc.case(id='async', tags=['async', 'function'])
def case_callable_async() -> CallableTypeCase:
    return CallableTypeCase(
        callable_type=CallableType.ASYNC_COROUTINE,
        create_call_func=_create_async_callable,
        call_arg=4,
        expected_result=5,
        expected_events=['call:4'],
    )


@pc.case(id='async_generator', tags=['async', 'generator'])
def case_callable_async_generator() -> CallableTypeCase:
    return CallableTypeCase(
        callable_type=CallableType.ASYNC_GENERATOR,
        create_call_func=_create_async_generator_callable,
        call_arg=3,
        expected_result=[0, 1, 2],
        expected_events=['yield:0', 'yield:1', 'yield:2'],
    )


class TrackedContext:
    def __init__(self) -> None:
        self.state: list[str] = []

    @contextmanager
    def context(self):
        self.state.append('enter')
        try:
            yield
        finally:
            self.state.append('exit')


def _execute_call(callable_case: CallableTypeCase, call_func: Callable[..., Any]) -> Any:
    async def _consume_async_generator(generator: AsyncGenerator) -> list[int]:
        return [item async for item in generator]

    arg = callable_case.call_arg

    match callable_case.callable_type:
        case CallableType.SYNC_FUNCTION:
            return call_func(arg)
        case CallableType.SYNC_GENERATOR:
            return tuple(call_func(arg))
        case CallableType.ASYNC_COROUTINE:
            return asyncio.run(call_func(arg))
        case CallableType.ASYNC_GENERATOR:
            return asyncio.run(_consume_async_generator(call_func(arg)))


@pc.parametrize_with_cases('case', cases='.')
def test_callable_type(case: CallableTypeCase) -> None:
    assert get_callable_type(case.create_call_func([])) is case.callable_type


@pytest.mark.parametrize(
    ('has_async', 'has_generator', 'expected_type'),
    [
        (False, False, CallableType.SYNC_FUNCTION),
        (False, True, CallableType.SYNC_GENERATOR),
        (True, False, CallableType.ASYNC_COROUTINE),
        (True, True, CallableType.ASYNC_GENERATOR),
    ],
)
def test_callable_type_from_flags(
    has_async: bool,
    has_generator: bool,
    expected_type: CallableType.Literals,
) -> None:
    assert callable_type_from_flags(is_async=has_async, is_generator=has_generator) is expected_type


@pc.parametrize_with_cases('case', cases='.', has_tag='function')
def test_decorate_callable_by_type_wrap_signature(case: CallableTypeCase,) -> None:
    call_func = case.create_call_func([])

    class CanAddInt(Protocol):
        def __add__(self, other: int) -> int:
            ...

    def func_int_add(value: CanAddInt) -> int:
        ...

    func_int_add_sign = inspect.signature(func_int_add)

    wrapped = decorate_callable_by_type(
        call_func,
        func_int_add_sign.parameters,
        func_int_add_sign.return_annotation,
        case.callable_type,
    )

    assert _execute_call(case, wrapped) == case.expected_result
    assert inspect.signature(wrapped) == func_int_add_sign


@pc.parametrize_with_cases('case', cases='.')
def test_decorate_callable_by_type_with_context(case: CallableTypeCase,) -> None:
    tracked_context = TrackedContext()
    call_func = case.create_call_func(tracked_context.state)

    wrapped = decorate_callable_by_type(
        call_func,
        inspect.signature(call_func).parameters,
        inspect.signature(call_func).return_annotation,
        case.callable_type,
        context_factory=tracked_context.context,
    )

    assert _execute_call(case, wrapped) == case.expected_result
    assert tracked_context.state == ['enter', *case.expected_events, 'exit']


def test_decorate_callable_by_type_async_resolve_async_result_with_non_awaitable() -> None:
    case = case_callable_sync()
    state: list[str] = []
    call_func = case.create_call_func(state)

    wrapped = decorate_callable_by_type(
        call_func,
        inspect.signature(call_func).parameters,
        inspect.signature(call_func).return_annotation,
        CallableType.ASYNC_COROUTINE,
        resolve_async_result=True,
    )

    assert asyncio.run(wrapped(case.call_arg)) == case.expected_result
    assert state == case.expected_events


def test_decorate_callable_by_type_async_without_resolve_async_result_raises() -> None:
    case = case_callable_sync()
    state: list[str] = []
    call_func = case.create_call_func(state)

    wrapped = decorate_callable_by_type(
        call_func,
        inspect.signature(call_func).parameters,
        inspect.signature(call_func).return_annotation,
        CallableType.ASYNC_COROUTINE,
        resolve_async_result=False,
    )

    with pytest.raises(TypeError):
        asyncio.run(wrapped(case.call_arg))


@pc.parametrize_with_cases('case', cases='.')
def test_decorate_result_by_type(case: CallableTypeCase) -> None:
    state: list[str] = []
    decorated_call = decorate_result_by_type(on_finished=lambda: state.append('finished'))(
        case.create_call_func(state))

    assert _execute_call(case, decorated_call) == case.expected_result
    assert state == [*case.expected_events, 'finished']
