from collections.abc import AsyncGenerator, Awaitable, Generator
from contextlib import AbstractContextManager, nullcontext
import functools
import inspect
from types import AsyncGeneratorType, GeneratorType, MappingProxyType
from typing import Any, Callable, Literal, overload

from typing_extensions import ParamSpec, TypeVar

from omnipy.util.literal_enum import LiteralEnum

_P = ParamSpec('_P')
_R = TypeVar('_R')
_Y = TypeVar('_Y')
_S = TypeVar('_S')
_GR = TypeVar('_GR')


class _SyncFunctionType(LiteralEnum[str]):
    Literals = Literal['sync-function']
    SYNC_FUNCTION: Literal['sync-function'] = 'sync-function'


class _SyncGeneratorType(LiteralEnum[str]):
    Literals = Literal['sync-generator']
    SYNC_GENERATOR: Literal['sync-generator'] = 'sync-generator'


class _AsyncCoroutineType(LiteralEnum[str]):
    Literals = Literal['async-coroutine']
    ASYNC_COROUTINE: Literal['async-coroutine'] = 'async-coroutine'


class _AsyncGeneratorType(LiteralEnum[str]):
    Literals = Literal['async-generator']
    ASYNC_GENERATOR: Literal['async-generator'] = 'async-generator'


class SyncCallableType(_SyncFunctionType, _SyncGeneratorType):
    Literals = Literal[_SyncFunctionType.Literals, _SyncGeneratorType.Literals]


class AsyncCallableType(_AsyncCoroutineType, _AsyncGeneratorType):
    Literals = Literal[_AsyncCoroutineType.Literals, _AsyncGeneratorType.Literals]


class PlainCallableType(_SyncFunctionType, _AsyncCoroutineType):
    Literals = Literal[_SyncFunctionType.Literals, _AsyncCoroutineType.Literals]


class GeneratorCallableType(_SyncGeneratorType, _AsyncGeneratorType):
    Literals = Literal[_SyncGeneratorType.Literals, _AsyncGeneratorType.Literals]


class CallableType(SyncCallableType, AsyncCallableType):
    Literals = Literal[SyncCallableType.Literals, AsyncCallableType.Literals]


def get_callable_type(callable: Callable[..., Any]) -> CallableType.Literals:
    if inspect.isasyncgenfunction(callable):
        return CallableType.ASYNC_GENERATOR
    elif inspect.iscoroutinefunction(callable):
        return CallableType.ASYNC_COROUTINE
    elif inspect.isgeneratorfunction(callable):
        return CallableType.SYNC_GENERATOR
    else:
        return CallableType.SYNC_FUNCTION


def _noop() -> None:
    return None


def callable_type_from_flags(*, is_async: bool, is_generator: bool) -> CallableType.Literals:
    if is_async:
        if is_generator:
            return CallableType.ASYNC_GENERATOR
        else:
            return CallableType.ASYNC_COROUTINE
    else:
        if is_generator:
            return CallableType.SYNC_GENERATOR
        else:
            return CallableType.SYNC_FUNCTION


def decorate_callable_by_type(  # noqa: C901
    call_func: Callable[_P, Any],
    param_signatures: MappingProxyType[str, inspect.Parameter],
    return_type: type,
    call_type: CallableType.Literals,
    *,
    context_factory: Callable[[], AbstractContextManager[object]] | None = None,
    resolve_async_result: bool = False,
) -> Callable[_P, Any]:
    from omnipy.util.helpers import resolve

    make_context = context_factory or nullcontext
    signature = inspect.Signature(
        parameters=tuple(param_signatures.values()), return_annotation=return_type)

    if call_type is CallableType.SYNC_FUNCTION:

        def _sync_wrapper(*args: _P.args, **kwargs: _P.kwargs):
            with make_context():
                return call_func(*args, **kwargs)

        _sync_wrapper.__signature__ = signature
        return _sync_wrapper

    elif call_type is CallableType.SYNC_GENERATOR:

        def _sync_generator_wrapper(*args: _P.args, **kwargs: _P.kwargs):
            with make_context():
                yield from call_func(*args, **kwargs)

        _sync_generator_wrapper.__signature__ = signature
        return _sync_generator_wrapper

    elif call_type is CallableType.ASYNC_COROUTINE:

        async def _async_wrapper(*args: _P.args, **kwargs: _P.kwargs):
            with make_context():
                result = call_func(*args, **kwargs)
                if resolve_async_result:
                    return await resolve(result)
                return await result

        _async_wrapper.__signature__ = signature
        return _async_wrapper

    else:

        async def _async_generator_wrapper(*args: _P.args, **kwargs: _P.kwargs):
            with make_context():
                job_result = call_func(*args, **kwargs)
                sent = None
                try:
                    while True:
                        sent = yield await job_result.asend(sent)
                except StopAsyncIteration:
                    return

        _async_generator_wrapper.__signature__ = signature
        return _async_generator_wrapper


@overload
def _decorate_result_with_finished_callback(
    result: Generator[_Y, _S, _GR],
    register_finished: Callable[[], None],
) -> Generator[_Y, _S, _GR]:
    ...


@overload
def _decorate_result_with_finished_callback(
    result: AsyncGenerator[_Y, _S],
    register_finished: Callable[[], None],
) -> AsyncGenerator[_Y, _S]:
    ...


@overload
def _decorate_result_with_finished_callback(
    result: Awaitable[_R],
    register_finished: Callable[[], None],
) -> Awaitable[_R]:
    ...


@overload
def _decorate_result_with_finished_callback(
    result: _R,
    register_finished: Callable[[], None],
) -> _R:
    ...


def _decorate_result_with_finished_callback(
    result: Any,
    register_finished: Callable[[], None],
) -> Any:
    if isinstance(result, GeneratorType):

        def _detect_finished_generator_decorator():
            returned_result = yield from result
            register_finished()
            return returned_result

        return _detect_finished_generator_decorator()

    elif isinstance(result, AsyncGeneratorType):

        async def _detect_finished_async_generator_decorator():
            sent = None
            try:
                while True:
                    sent = yield await result.asend(sent)
            except StopAsyncIteration:
                register_finished()

        return _detect_finished_async_generator_decorator()

    elif inspect.isawaitable(result):

        async def _detect_finished_coroutine():
            resolved_result = await result
            register_finished()
            return resolved_result

        return _detect_finished_coroutine()

    else:
        register_finished()
        return result


def decorate_result_by_type(
    *,
    on_finished: Callable[[], None] | None = None,
) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
    register_finished = on_finished or _noop

    def _decorator(call_func: Callable[_P, _R]) -> Callable[_P, _R]:
        @functools.wraps(call_func)
        def _result_wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _R:
            return _decorate_result_with_finished_callback(
                call_func(*args, **kwargs),
                register_finished,
            )

        return _result_wrapper

    return _decorator
