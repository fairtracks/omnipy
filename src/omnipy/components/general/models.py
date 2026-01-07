import typing
from typing import Any, Generic, get_args, Protocol

from typing_extensions import TypeVar

from omnipy.data.dataset import Dataset
from omnipy.data.helpers import TypeVarStore1, TypeVarStore2, TypeVarStore3, TypeVarStore4
from omnipy.data.model import Model
from omnipy.shared.typedefs import TypeForm
from omnipy.util.helpers import is_iterable


class NotIterableExceptStrOrBytesModel(Model[object | None]):
    """
    Model describing any object that is not iterable, except for `str` and `bytes` types.
    As strings and bytes are iterable (over the characters/bytes) but also generally useful and
    often considered singular (or scalar) types, they are specifically allowed by this model.

    Examples:
        >>> from omnipy import NotIterableExceptStrOrBytesModel, print_exception
        >>>
        >>> NotIterableExceptStrOrBytesModel(1234)
        NotIterableExceptStrOrBytesModel(1234)
        >>> NotIterableExceptStrOrBytesModel('1234')
        NotIterableExceptStrOrBytesModel(1234)
        >>> with print_exception:
        ...     NotIterableExceptStrOrBytesModel((1, 2, 3, 4))
        ValidationError: 1 validation error for NotIterableExceptStrOrBytesModel

    Note:
        JsonScalarModel is a strict submodel of NotIterableExceptStrOrBytesModel in that all objects
        allowed by JsonScalarModel are also allowed by NotIterableExceptStrOrBytesModel.
    """
    @classmethod
    def _parse_data(cls, data: object) -> object:
        if isinstance(data, NotIterableExceptStrOrBytesModel):
            return data

        assert isinstance(data, str) or isinstance(data, bytes) or not is_iterable(data), \
            f'Data of type {type(data)} is iterable'

        return data


#
# Exportable models
#

# General

_U = TypeVar('_U', bound=Model | Dataset, default=Model[object])
_V = TypeVar('_V', bound=Model | Dataset, default=Model[object])
_W = TypeVar('_W', bound=Model | Dataset, default=Model[object])
_X = TypeVar('_X', bound=Model | Dataset, default=Model[object])
_Y = TypeVar('_Y', bound=Model | Dataset, default=Model[object])
_Z = TypeVar('_Z', bound=Model | Dataset, default=Model[object])


class HasOuterType(Protocol):
    @classmethod
    def outer_type(cls, with_args: bool = False) -> TypeForm:
        ...


class _ChainMixin:
    @classmethod
    def _parse_data(cls: type[HasOuterType], data: Any) -> Any:
        type_args = get_args(cls.outer_type(with_args=True))
        store_models = [get_args(store)[0] for store in type_args[1:-1]]
        all_types = [type_args[0]] + store_models + [type_args[-1]]

        # To revert type reversal in ChainX class definition. After
        # reversal, `all_types` will be in the order specified by the user
        all_types.reverse()

        if isinstance(data, all_types[-1]):
            return data

        assert isinstance(data, all_types[0]), \
            f'Expected data of type {all_types[0]}, got {type(data)}'

        # Run through the pipeline
        for _type in all_types[1:]:
            data = _type(data)

        return data


if typing.TYPE_CHECKING:

    class Chain2(_ChainMixin, Model[_V], Generic[_U, _V]):
        ...

    class Chain3(_ChainMixin, Model[_W], Generic[_U, _V, _W]):
        ...

    class Chain4(_ChainMixin, Model[_X], Generic[_U, _V, _W, _X]):
        ...

    class Chain5(
            _ChainMixin,
            Model[_Y],
            Generic[_U, _V, _W, _X, _Y],
    ):
        ...

    class Chain6(
            _ChainMixin,
            Model[_Z],
            Generic[_U, _V, _W, _X, _Y, _Z],
    ):
        ...

else:

    class Chain2(_ChainMixin, Model[_V | _U], Generic[_U, _V]):
        ...

    class Chain3(_ChainMixin, Model[_W | TypeVarStore1[_V] | _U], Generic[_U, _V, _W]):
        ...

    class Chain4(_ChainMixin,
                 Model[_X | TypeVarStore2[_W] | TypeVarStore1[_V] | _U],
                 Generic[_U, _V, _W, _X]):
        ...

    class Chain5(
            _ChainMixin,
            Model[_Y | TypeVarStore3[_X] | TypeVarStore2[_W] | TypeVarStore1[_V] | _U],
            Generic[_U, _V, _W, _X, _Y],
    ):
        ...

    class Chain6(
            _ChainMixin,
            Model[_Z | TypeVarStore4[_Y] | TypeVarStore3[_X] | TypeVarStore2[_W] | TypeVarStore1[_V]
                  | _U],
            Generic[_U, _V, _W, _X, _Y, _Z],
    ):
        ...
