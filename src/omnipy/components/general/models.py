from typing import Generic, get_args

from typing_extensions import TypeVar

from omnipy.data.helpers import TypeVarStore1, TypeVarStore2, TypeVarStore3, TypeVarStore4
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
        if isinstance(data, NotIterableExceptStrOrBytesModel):
            return data

        assert isinstance(data, str) or isinstance(data, bytes) or not is_iterable(data), \
            f'Data of type {type(data)} is iterable'

        return data


#
# Exportable models
#

# General

_U = TypeVar('_U', bound=Model, default=Model[object])
_V = TypeVar('_V', bound=Model, default=Model[object])
_W = TypeVar('_W', bound=Model, default=Model[object])
_X = TypeVar('_X', bound=Model, default=Model[object])
_Y = TypeVar('_Y', bound=Model, default=Model[object])
_Z = TypeVar('_Z', bound=Model, default=Model[object])


class _ChainMixin:
    @classmethod
    def _parse_data(cls, data: object) -> object:
        type_args = get_args(cls.outer_type(with_args=True))
        store_models = [get_args(store)[0] for store in type_args[1:-1]]
        all_models = [type_args[0]] + store_models + [type_args[-1]]
        all_models.reverse()

        if isinstance(data, all_models[-1]):
            return data

        assert isinstance(data, all_models[0]), \
            f'Expected data of type {all_models[0]}, got {type(data)}'

        for model in all_models[1:]:
            data = model(data)
        return data


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
