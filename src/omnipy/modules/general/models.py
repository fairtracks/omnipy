from typing import Generic, get_args, Hashable, TypeAlias

from typing_extensions import TypeVar

from omnipy.data.helpers import TypeVarStore
from omnipy.data.model import Model
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
        assert isinstance(data, str) or isinstance(data, bytes) or not is_iterable(data), \
            f'Data of type {type(data)} is iterable'
        return data


#
# Exportable models
#

# General

U = TypeVar('U', bound=Model, default=Model[object])
V = TypeVar('V', bound=Model, default=Model[object])
W = TypeVar('W', bound=Model, default=Model[object])
X = TypeVar('X', bound=Model, default=Model[object])
Y = TypeVar('Y', bound=Model, default=Model[object])
Z = TypeVar('Z', bound=Model, default=Model[object])


class ChainMixin:
    @classmethod
    def _parse_data(cls, data) -> object:
        stores = get_args(cls.outer_type(with_args=True))[:-1]
        for store in stores:
            model = get_args(store)[0]
            data = model(data)
        return data


class Chain2(ChainMixin, Model[TypeVarStore[U] | TypeVarStore[V] | object], Generic[U, V]):
    ...


class Chain3(ChainMixin,
             Model[TypeVarStore[U] | TypeVarStore[V] | TypeVarStore[W] | object],
             Generic[U, V, W]):
    ...


class Chain4(ChainMixin,
             Model[TypeVarStore[U] | TypeVarStore[V] | TypeVarStore[W] | TypeVarStore[X] | object],
             Generic[U, V, W, X]):
    ...


class Chain5(ChainMixin,
             Model[TypeVarStore[U] | TypeVarStore[V] | TypeVarStore[W] | TypeVarStore[X]
                   | TypeVarStore[Y] | object],
             Generic[U, V, W, X, Y]):
    ...


class Chain6(ChainMixin,
             Model[TypeVarStore[U] | TypeVarStore[V] | TypeVarStore[W] | TypeVarStore[X]
                   | TypeVarStore[Y] | TypeVarStore[Z] | object],
             Generic[U, V, W, X, Y, Z]):
    ...
