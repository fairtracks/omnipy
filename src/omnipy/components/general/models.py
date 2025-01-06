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

U = TypeVar('U', bound=Model, default=Model[object])
V = TypeVar('V', bound=Model, default=Model[object])
W = TypeVar('W', bound=Model, default=Model[object])
X = TypeVar('X', bound=Model, default=Model[object])
Y = TypeVar('Y', bound=Model, default=Model[object])
Z = TypeVar('Z', bound=Model, default=Model[object])


class ChainMixin:
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


class Chain2(ChainMixin, Model[V | U], Generic[U, V]):
    ...


class Chain3(ChainMixin, Model[W | TypeVarStore1[V] | U], Generic[U, V, W]):
    ...


class Chain4(ChainMixin, Model[X | TypeVarStore2[W] | TypeVarStore1[V] | U], Generic[U, V, W, X]):
    ...


class Chain5(
        ChainMixin,
        Model[Y | TypeVarStore3[X] | TypeVarStore2[W] | TypeVarStore1[V] | U],
        Generic[U, V, W, X, Y],
):
    ...


class Chain6(
        ChainMixin,
        Model[Z | TypeVarStore4[Y] | TypeVarStore3[X] | TypeVarStore2[W] | TypeVarStore1[V] | U],
        Generic[U, V, W, X, Y, Z],
):
    ...
