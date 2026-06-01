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
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{CHAIN_DOC_2}}
        """Convert data through a two-model chain.

``Chain2[U, V]`` transforms data of type ``U`` into type ``V``
by creating a model instance of the first type, then recasting the
result into the second model type.  This provides a lightweight
inline dataflow pipeline within a single model object.

Type Args:
    U: The input model type.
    V: The output model type.

Examples:
    >>> from omnipy import Chain2
    >>> from omnipy.components.json.models import JsonScalarModel
    >>> chain = Chain2[str, int]
    >>> chain('42')
    Chain2[str, int](42)

"""
        ...

    class Chain3(_ChainMixin, Model[_W], Generic[_U, _V, _W]):
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{CHAIN_DOC_3}}
        """Convert data through a three-model chain.

``Chain3[U, V, W]`` transforms data of type ``U`` into type ``W``
by sequentially creating model instances of ``U``, then ``V``, then
``W``.  Each step recasts the previous result into the next model type.

Type Args:
    U: The input model type.
    V: The first intermediate model type.
    W: The output model type.

"""
        ...

    class Chain4(_ChainMixin, Model[_X], Generic[_U, _V, _W, _X]):
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{CHAIN_DOC_4}}
        """Convert data through a four-model chain.

``Chain4[U, V, W, X]`` transforms data of type ``U`` into type ``X``
through two intermediate model types ``V`` and ``W``.

Type Args:
    U: The input model type.
    V: The first intermediate model type.
    W: The second intermediate model type.
    X: The output model type.

"""
        ...

    class Chain5(
            _ChainMixin,
            Model[_Y],
            Generic[_U, _V, _W, _X, _Y],
    ):
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{CHAIN_DOC_5}}
        """Convert data through a five-model chain.

``Chain5[U, V, W, X, Y]`` transforms data of type ``U`` into type ``Y``
through three intermediate model types.

Type Args:
    U: The input model type.
    V: The first intermediate model type.
    W: The second intermediate model type.
    X: The third intermediate model type.
    Y: The output model type.

"""
        ...

    class Chain6(
            _ChainMixin,
            Model[_Z],
            Generic[_U, _V, _W, _X, _Y, _Z],
    ):
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{CHAIN_DOC_6}}
        """Convert data through a six-model chain.

``Chain6[U, V, W, X, Y, Z]`` transforms data of type ``U`` into type
``Z`` through four intermediate model types.

Type Args:
    U: The input model type.
    V: The first intermediate model type.
    W: The second intermediate model type.
    X: The third intermediate model type.
    Y: The fourth intermediate model type.
    Z: The output model type.

"""
        ...

else:

    class Chain2(_ChainMixin, Model[_V | _U], Generic[_U, _V]):
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{CHAIN_DOC_2}}
        """Convert data through a two-model chain.

``Chain2[U, V]`` transforms data of type ``U`` into type ``V``
by creating a model instance of the first type, then recasting the
result into the second model type.  This provides a lightweight
inline dataflow pipeline within a single model object.

Type Args:
    U: The input model type.
    V: The output model type.

Examples:
    >>> from omnipy import Chain2
    >>> from omnipy.components.json.models import JsonScalarModel
    >>> chain = Chain2[str, int]
    >>> chain('42')
    Chain2[str, int](42)

"""
        ...

    class Chain3(_ChainMixin, Model[_W | TypeVarStore1[_V] | _U], Generic[_U, _V, _W]):
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{CHAIN_DOC_3}}
        """Convert data through a three-model chain.

``Chain3[U, V, W]`` transforms data of type ``U`` into type ``W``
by sequentially creating model instances of ``U``, then ``V``, then
``W``.  Each step recasts the previous result into the next model type.

Type Args:
    U: The input model type.
    V: The first intermediate model type.
    W: The output model type.

"""
        ...

    class Chain4(_ChainMixin,
                 Model[_X | TypeVarStore2[_W] | TypeVarStore1[_V] | _U],
                 Generic[_U, _V, _W, _X]):
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{CHAIN_DOC_4}}
        """Convert data through a four-model chain.

``Chain4[U, V, W, X]`` transforms data of type ``U`` into type ``X``
through two intermediate model types ``V`` and ``W``.

Type Args:
    U: The input model type.
    V: The first intermediate model type.
    W: The second intermediate model type.
    X: The output model type.

"""
        ...

    class Chain5(
            _ChainMixin,
            Model[_Y | TypeVarStore3[_X] | TypeVarStore2[_W] | TypeVarStore1[_V] | _U],
            Generic[_U, _V, _W, _X, _Y],
    ):
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{CHAIN_DOC_5}}
        """Convert data through a five-model chain.

``Chain5[U, V, W, X, Y]`` transforms data of type ``U`` into type ``Y``
through three intermediate model types.

Type Args:
    U: The input model type.
    V: The first intermediate model type.
    W: The second intermediate model type.
    X: The third intermediate model type.
    Y: The output model type.

"""
        ...

    class Chain6(
            _ChainMixin,
            Model[_Z | TypeVarStore4[_Y] | TypeVarStore3[_X] | TypeVarStore2[_W] | TypeVarStore1[_V]
                  | _U],
            Generic[_U, _V, _W, _X, _Y, _Z],
    ):
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{CHAIN_DOC_6}}
        """Convert data through a six-model chain.

``Chain6[U, V, W, X, Y, Z]`` transforms data of type ``U`` into type
``Z`` through four intermediate model types.

Type Args:
    U: The input model type.
    V: The first intermediate model type.
    W: The second intermediate model type.
    X: The third intermediate model type.
    Y: The fourth intermediate model type.
    Z: The output model type.

"""
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
