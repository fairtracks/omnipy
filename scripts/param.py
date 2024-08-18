from typing import Generic, get_args, get_origin, Literal

from pydantic.fields import UndefinedType
from typing_extensions import TypeVar

from omnipy import Model

D = TypeVar('D', default=object)
S = TypeVar('S', default=object)
T = TypeVar('T', default=Literal[','])


class Param(Model[UndefinedType | S | D], Generic[S, D]):
    @classmethod
    def _parse_data(cls, data: UndefinedType | S | D):
        override, default = get_args(cls.outer_type(with_args=True))[1:3]
        print(f'default: {repr(default)}, override: {repr(override)}, data: {repr(data)}')
        assert get_origin(default) == Literal
        target = override if get_origin(override) == Literal else default
        print(
            f'data: {repr(data)}, target: {repr(target)}, check: {type(data) is not UndefinedType and data != target}'
        )
        if type(data) is not UndefinedType and data != target:
            print('I am asserting!')
            raise AssertionError(
                f'Data other than the default or override literals are not allowed: {data}')
        return target


DefaultDelim = Literal[',']


class DelimitParam(Param[S, DefaultDelim], Generic[S]):
    ...


class Y(Model[list[str] | tuple[str, DelimitParam]]):
    ...


class ValueWithParam(Model[tuple[DelimitParam[S], T]], Generic[T, S]):
    @classmethod
    def _parse_data(cls, data: tuple[T, DelimitParam[S]]):
        print(f'data: {repr(data)}')
        return data


class D(Model[T], Generic[T]):
    ...


D[Literal['asd']]()


class Splitter(Model[list[str] | str | Model[T]], Generic[T]):
    ...


class A(Model[tuple[T, S]], Generic[T, S]):
    ...
