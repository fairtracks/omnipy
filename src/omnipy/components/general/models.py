from collections import defaultdict
from collections.abc import Iterable, Mapping
from types import GenericAlias
from typing import Any, Generic, get_args, Protocol, Union

from typing_extensions import TypeVar

from omnipy.data.dataset import Dataset
from omnipy.data.helpers import TypeVarStore1, TypeVarStore2, TypeVarStore3, TypeVarStore4
from omnipy.data.model import Model
from omnipy.shared.typedefs import TypeForm
from omnipy.shared.typing import TYPE_CHECKING
from omnipy.util.helpers import is_iterable, is_non_str_byte_iterable


class NotIterableExceptStrOrBytesModel(Model[object | None]):
    """Represent a non-iterable value while still allowing ``str`` and ``bytes``.

    Strings and bytes are accepted even though they are technically iterable because they are often
    used as scalar values.

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
        ``JsonScalarModel`` is a strict submodel because every JSON scalar also satisfies this
        model.
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
    """Protocol for generic model classes that expose their outer type form."""
    @classmethod
    def outer_type(cls, with_args: bool = False) -> TypeForm:
        """Return the model's declared outer type.

        Args:
            with_args: Whether to include resolved generic arguments in the
                returned type form.

        Returns:
            TypeForm: The outer type associated with the model class.
        """
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


if TYPE_CHECKING:

    class Chain2(_ChainMixin, Model[_V], Generic[_U, _V]):
        """{{CHAIN_DOC_2}}"""
        ...

    class Chain3(_ChainMixin, Model[_W], Generic[_U, _V, _W]):
        """{{CHAIN_DOC_3}}"""
        ...

    class Chain4(_ChainMixin, Model[_X], Generic[_U, _V, _W, _X]):
        """{{CHAIN_DOC_4}}"""
        ...

    class Chain5(
            _ChainMixin,
            Model[_Y],
            Generic[_U, _V, _W, _X, _Y],
    ):
        """{{CHAIN_DOC_5}}"""
        ...

    class Chain6(
            _ChainMixin,
            Model[_Z],
            Generic[_U, _V, _W, _X, _Y, _Z],
    ):
        """{{CHAIN_DOC_6}}"""
        ...

else:

    class Chain2(_ChainMixin, Model[_V | _U], Generic[_U, _V]):
        """{{CHAIN_DOC_2}}"""
        ...

    class Chain3(_ChainMixin, Model[_W | TypeVarStore1[_V] | _U], Generic[_U, _V, _W]):
        """{{CHAIN_DOC_3}}"""
        ...

    class Chain4(_ChainMixin,
                 Model[_X | TypeVarStore2[_W] | TypeVarStore1[_V] | _U],
                 Generic[_U, _V, _W, _X]):
        """{{CHAIN_DOC_4}}"""
        ...

    class Chain5(
            _ChainMixin,
            Model[_Y | TypeVarStore3[_X] | TypeVarStore2[_W] | TypeVarStore1[_V] | _U],
            Generic[_U, _V, _W, _X, _Y],
    ):
        """{{CHAIN_DOC_5}}"""
        ...

    class Chain6(
            _ChainMixin,
            Model[_Z | TypeVarStore4[_Y] | TypeVarStore3[_X] | TypeVarStore2[_W] | TypeVarStore1[_V]
                  | _U],
            Generic[_U, _V, _W, _X, _Y, _Z],
    ):
        """{{CHAIN_DOC_6}}"""
        ...


class GroupByTypeModel(Chain2[Model[list], Model[dict[type | GenericAlias, list]]]):
    """
    Group list items by their runtime type.

    The model converts a list into a dictionary mapping each inferred item
    type to the sublist of items having that type. For mappings and other
    non-string iterables, it attempts to preserve more detailed generic
    type information, such as key/value types for mappings and element
    types for tuples and other iterables, when those type forms can be
    constructed at runtime.

    Examples:
        >>> GroupByTypeModel([1, 'a', 2, [3], ['b']]).to_data()
        {int: [1, 2], str: ['a'], list[int]: [[3]], list[str]: [['b']]}
    """
    @classmethod
    def _parse_data(cls, data: Model[list]) -> Model[dict[type | GenericAlias, list]]:
        grouped: dict[type, list] = defaultdict(list)

        def _iter_union_type(seq: Iterable):
            return Union[tuple(type(item) for item in seq)]

        def _deduce_full_type(_item: object) -> type:
            try:
                if isinstance(_item, Mapping):
                    return type(_item)[  # type: ignore[index]
                        _iter_union_type(_item.keys()),
                        _iter_union_type(_item.values()),
                    ]
                elif isinstance(_item, tuple):
                    return tuple[tuple(type(_) for _ in _item)]
                elif is_non_str_byte_iterable(_item):
                    return type(_item)[_iter_union_type(_item)]  # type: ignore[index]
            except TypeError:
                pass
            return type(_item)

        for item in data.content:
            full_type = _deduce_full_type(item)
            grouped[full_type].append(item)  # pyright: ignore [reportArgumentType]
        return Model[dict[type | GenericAlias, list]](grouped)
