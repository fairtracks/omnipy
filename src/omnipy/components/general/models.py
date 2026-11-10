from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Iterable, Iterator, Mapping, Sequence
from types import GenericAlias, UnionType
from typing import Any, cast, Generic, get_args, Protocol, Union

from typing_extensions import override, TypeVar

from omnipy.data.dataset import Dataset, is_dataset_instance
from omnipy.data.helpers import (
    TypeVarStore,
    TypeVarStore1,
    TypeVarStore2,
    TypeVarStore3,
    TypeVarStore4,
)
from omnipy.data.model import Model
from omnipy.data.primary_key import PrimaryKey, PrimaryKeyModelMetaclass, serialize_primary_key
from omnipy.shared.protocols.data import IsModel
from omnipy.shared.protocols.vendored.typeshed import SupportsItems
from omnipy.shared.typedefs import TypeForm
from omnipy.shared.typing import TYPE_CHECKING
from omnipy.util.helpers import (
    all_type_variants,
    has_items_method,
    is_iterable,
    is_non_str_byte_iterable,
    is_package_editable,
    is_union,
)
import omnipy.util.pydantic as pyd

from .protocols import SupportsAdd

if TYPE_CHECKING:
    from omnipy.data.typing.model import PlainModel

if is_package_editable('omnipy'):
    import os
    from textwrap import dedent

    os.environ['OMNIPY_MACRO_CHAIN_TYPEARG_INPUT'] = 'The input model or dataset type.'

    os.environ['OMNIPY_MACRO_CHAIN_TYPEARG_FIRST_INTERMEDIATE'] = (
        'The first intermediate model or dataset type.'
    )

    os.environ['OMNIPY_MACRO_CHAIN_TYPEARG_SECOND_INTERMEDIATE'] = (
        'The second intermediate model or dataset type.'
    )

    os.environ['OMNIPY_MACRO_CHAIN_TYPEARG_THIRD_INTERMEDIATE'] = (
        'The third intermediate model or dataset type.'
    )

    os.environ['OMNIPY_MACRO_CHAIN_TYPEARG_FOURTH_INTERMEDIATE'] = (
        'The fourth intermediate model or dataset type.'
    )

    os.environ['OMNIPY_MACRO_CHAIN_TYPEARG_OUTPUT'] = 'The output model or dataset type.'

    os.environ['OMNIPY_MACRO_CHAIN_GENERAL_BEHAVIOR'] = dedent("""\
        This provides a lightweight inline dataflow pipeline within a single
        model.

        Chain type parameters must be model or dataset types. Input data may
        be any content that validates directly against the output type or,
        if that fails, against the first type in the chain. When the input
        validates against the output type, the chain short-circuits
        immediately. Otherwise, the data is validated against the first type
        and then validated forward through each subsequent model or dataset
        type until the output type is reached. The final result conforms to
        the output type unless validation fails during the chain.
    """)


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

_FromT = TypeVar('_FromT', bound=object | UnionType)
_ToT = TypeVar('_ToT')
_KeyT = TypeVar('_KeyT')
_ItemT = TypeVar('_ItemT', default=object)
_PrimaryKeyT = TypeVar('_PrimaryKeyT', bound=PrimaryKey)
_RecordT = TypeVar('_RecordT', bound=pyd.BaseModel)


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

        assert isinstance(data, all_types[0]), (
            f'Expected data of type {all_types[0]}, got {type(data)}'
        )

        # Run through the pipeline
        for _type in all_types[1:]:
            data = _type(data)

        return data


if TYPE_CHECKING:

    class Chain2(_ChainMixin, Model[_V], Generic[_U, _V]):
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # Convert data through a two-model chain.
        #
        # ``Chain2[U, V]`` produces output of type ``V`` by first parsing the
        # input as ``U`` and then as ``V``, unless the input already parses
        # directly with ``V``.
        #
        # {{CHAIN_GENERAL_BEHAVIOR}}
        #
        # Type Args:
        #     U: {{CHAIN_TYPEARG_INPUT}}
        #     V: {{CHAIN_TYPEARG_OUTPUT}}
        #
        # Examples:
        #     >>> import omnipy as om
        #     >>> from collections.abc import Iterable
        #     >>> chain = om.Chain2[om.Model[Iterable[str]], om.Model[list[str]]]
        #     >>> chain('abc')
        #     Chain2[Model[Iterable[str]], Model[list[str]]](Model[list[str]](['a', 'b', 'c']))
        """Convert data through a two-model chain.

        ``Chain2[U, V]`` produces output of type ``V`` by first parsing the
        input as ``U`` and then as ``V``, unless the input already parses
        directly with ``V``.

        This provides a lightweight inline dataflow pipeline within a single
        model.

        Chain type parameters must be model or dataset types. Input data may
        be any content that validates directly against the output type or,
        if that fails, against the first type in the chain. When the input
        validates against the output type, the chain short-circuits
        immediately. Otherwise, the data is validated against the first type
        and then validated forward through each subsequent model or dataset
        type until the output type is reached. The final result conforms to
        the output type unless validation fails during the chain.


        Type Args:
            U: The input model or dataset type.
            V: The output model or dataset type.

        Examples:
            >>> import omnipy as om
            >>> from collections.abc import Iterable
            >>> chain = om.Chain2[om.Model[Iterable[str]], om.Model[list[str]]]
            >>> chain('abc')
            Chain2[Model[Iterable[str]], Model[list[str]]](Model[list[str]](['a', 'b', 'c']))"""

        ...

    class Chain3(_ChainMixin, Model[_W], Generic[_U, _V, _W]):
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # Convert data through a three-model chain.
        #
        # ``Chain3[U, V, W]`` produces output of type ``W`` by first parsing
        # the input as ``U`` and then through the intermediate type ``V``,
        # unless the input already parses directly with ``W``.
        #
        # {{CHAIN_GENERAL_BEHAVIOR}}
        #
        # Type Args:
        #     U: {{CHAIN_TYPEARG_INPUT}}
        #     V: {{CHAIN_TYPEARG_FIRST_INTERMEDIATE}}
        #     W: {{CHAIN_TYPEARG_OUTPUT}}
        #
        # See [`Chain2`][omnipy.components.general.models.Chain2] for an example.
        """Convert data through a three-model chain.

        ``Chain3[U, V, W]`` produces output of type ``W`` by first parsing
        the input as ``U`` and then through the intermediate type ``V``,
        unless the input already parses directly with ``W``.

        This provides a lightweight inline dataflow pipeline within a single
        model.

        Chain type parameters must be model or dataset types. Input data may
        be any content that validates directly against the output type or,
        if that fails, against the first type in the chain. When the input
        validates against the output type, the chain short-circuits
        immediately. Otherwise, the data is validated against the first type
        and then validated forward through each subsequent model or dataset
        type until the output type is reached. The final result conforms to
        the output type unless validation fails during the chain.


        Type Args:
            U: The input model or dataset type.
            V: The first intermediate model or dataset type.
            W: The output model or dataset type.

        See [`Chain2`][omnipy.components.general.models.Chain2] for an example."""

        ...

    class Chain4(_ChainMixin, Model[_X], Generic[_U, _V, _W, _X]):
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # Convert data through a four-model chain.
        #
        # ``Chain4[U, V, W, X]`` produces output of type ``X`` by first
        # parsing the input as ``U`` and then through the intermediate types
        # ``V`` and ``W``, unless the input already parses directly with
        # ``X``.
        #
        # {{CHAIN_GENERAL_BEHAVIOR}}
        #
        # Type Args:
        #     U: {{CHAIN_TYPEARG_INPUT}}
        #     V: {{CHAIN_TYPEARG_FIRST_INTERMEDIATE}}
        #     W: {{CHAIN_TYPEARG_SECOND_INTERMEDIATE}}
        #     X: {{CHAIN_TYPEARG_OUTPUT}}
        #
        # See [`Chain2`][omnipy.components.general.models.Chain2] for an example.
        """Convert data through a four-model chain.

        ``Chain4[U, V, W, X]`` produces output of type ``X`` by first
        parsing the input as ``U`` and then through the intermediate types
        ``V`` and ``W``, unless the input already parses directly with
        ``X``.

        This provides a lightweight inline dataflow pipeline within a single
        model.

        Chain type parameters must be model or dataset types. Input data may
        be any content that validates directly against the output type or,
        if that fails, against the first type in the chain. When the input
        validates against the output type, the chain short-circuits
        immediately. Otherwise, the data is validated against the first type
        and then validated forward through each subsequent model or dataset
        type until the output type is reached. The final result conforms to
        the output type unless validation fails during the chain.


        Type Args:
            U: The input model or dataset type.
            V: The first intermediate model or dataset type.
            W: The second intermediate model or dataset type.
            X: The output model or dataset type.

        See [`Chain2`][omnipy.components.general.models.Chain2] for an example."""

        ...

    class Chain5(
        _ChainMixin,
        Model[_Y],
        Generic[_U, _V, _W, _X, _Y],
    ):
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # Convert data through a five-model chain.
        #
        # ``Chain5[U, V, W, X, Y]`` produces output of type ``Y`` by first
        # parsing the input as ``U`` and then through three intermediate
        # types, unless the input already parses directly with ``Y``.
        #
        # {{CHAIN_GENERAL_BEHAVIOR}}
        #
        # Type Args:
        #     U: {{CHAIN_TYPEARG_INPUT}}
        #     V: {{CHAIN_TYPEARG_FIRST_INTERMEDIATE}}
        #     W: {{CHAIN_TYPEARG_SECOND_INTERMEDIATE}}
        #     X: {{CHAIN_TYPEARG_THIRD_INTERMEDIATE}}
        #     Y: {{CHAIN_TYPEARG_OUTPUT}}
        #
        # See [`Chain2`][omnipy.components.general.models.Chain2] for an example.
        """Convert data through a five-model chain.

        ``Chain5[U, V, W, X, Y]`` produces output of type ``Y`` by first
        parsing the input as ``U`` and then through three intermediate
        types, unless the input already parses directly with ``Y``.

        This provides a lightweight inline dataflow pipeline within a single
        model.

        Chain type parameters must be model or dataset types. Input data may
        be any content that validates directly against the output type or,
        if that fails, against the first type in the chain. When the input
        validates against the output type, the chain short-circuits
        immediately. Otherwise, the data is validated against the first type
        and then validated forward through each subsequent model or dataset
        type until the output type is reached. The final result conforms to
        the output type unless validation fails during the chain.


        Type Args:
            U: The input model or dataset type.
            V: The first intermediate model or dataset type.
            W: The second intermediate model or dataset type.
            X: The third intermediate model or dataset type.
            Y: The output model or dataset type.

        See [`Chain2`][omnipy.components.general.models.Chain2] for an example."""

        ...

    class Chain6(
        _ChainMixin,
        Model[_Z],
        Generic[_U, _V, _W, _X, _Y, _Z],
    ):
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # Convert data through a six-model chain.
        #
        # ``Chain6[U, V, W, X, Y, Z]`` produces output of type ``Z`` by first
        # parsing the input as ``U`` and then through four intermediate
        # types, unless the input already parses directly with ``Z``.
        #
        # {{CHAIN_GENERAL_BEHAVIOR}}
        #
        # Type Args:
        #     U: {{CHAIN_TYPEARG_INPUT}}
        #     V: {{CHAIN_TYPEARG_FIRST_INTERMEDIATE}}
        #     W: {{CHAIN_TYPEARG_SECOND_INTERMEDIATE}}
        #     X: {{CHAIN_TYPEARG_THIRD_INTERMEDIATE}}
        #     Y: {{CHAIN_TYPEARG_FOURTH_INTERMEDIATE}}
        #     Z: {{CHAIN_TYPEARG_OUTPUT}}
        #
        # See [`Chain2`][omnipy.components.general.models.Chain2] for an example.
        """Convert data through a six-model chain.

        ``Chain6[U, V, W, X, Y, Z]`` produces output of type ``Z`` by first
        parsing the input as ``U`` and then through four intermediate
        types, unless the input already parses directly with ``Z``.

        This provides a lightweight inline dataflow pipeline within a single
        model.

        Chain type parameters must be model or dataset types. Input data may
        be any content that validates directly against the output type or,
        if that fails, against the first type in the chain. When the input
        validates against the output type, the chain short-circuits
        immediately. Otherwise, the data is validated against the first type
        and then validated forward through each subsequent model or dataset
        type until the output type is reached. The final result conforms to
        the output type unless validation fails during the chain.


        Type Args:
            U: The input model or dataset type.
            V: The first intermediate model or dataset type.
            W: The second intermediate model or dataset type.
            X: The third intermediate model or dataset type.
            Y: The fourth intermediate model or dataset type.
            Z: The output model or dataset type.

        See [`Chain2`][omnipy.components.general.models.Chain2] for an example."""

        ...

else:

    class Chain2(_ChainMixin, Model[_V | _U], Generic[_U, _V]):
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # Convert data through a two-model chain.
        #
        # ``Chain2[U, V]`` produces output of type ``V`` by first parsing the
        # input as ``U`` and then as ``V``, unless the input already parses
        # directly with ``V``.
        #
        # {{CHAIN_GENERAL_BEHAVIOR}}
        #
        # Type Args:
        #     U: {{CHAIN_TYPEARG_INPUT}}
        #     V: {{CHAIN_TYPEARG_OUTPUT}}
        #
        # Examples:
        #     >>> import omnipy as om
        #     >>> from collections.abc import Iterable
        #     >>> chain = om.Chain2[om.Model[Iterable[str]], om.Model[list[str]]]
        #     >>> chain('abc')
        #     Chain2[Model[Iterable[str]], Model[list[str]]](Model[list[str]](['a', 'b', 'c']))
        """Convert data through a two-model chain.

        ``Chain2[U, V]`` produces output of type ``V`` by first parsing the
        input as ``U`` and then as ``V``, unless the input already parses
        directly with ``V``.

        This provides a lightweight inline dataflow pipeline within a single
        model.

        Chain type parameters must be model or dataset types. Input data may
        be any content that validates directly against the output type or,
        if that fails, against the first type in the chain. When the input
        validates against the output type, the chain short-circuits
        immediately. Otherwise, the data is validated against the first type
        and then validated forward through each subsequent model or dataset
        type until the output type is reached. The final result conforms to
        the output type unless validation fails during the chain.


        Type Args:
            U: The input model or dataset type.
            V: The output model or dataset type.

        Examples:
            >>> import omnipy as om
            >>> from collections.abc import Iterable
            >>> chain = om.Chain2[om.Model[Iterable[str]], om.Model[list[str]]]
            >>> chain('abc')
            Chain2[Model[Iterable[str]], Model[list[str]]](Model[list[str]](['a', 'b', 'c']))"""

        ...

    class Chain3(_ChainMixin, Model[_W | TypeVarStore1[_V] | _U], Generic[_U, _V, _W]):
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # Convert data through a three-model chain.
        #
        # ``Chain3[U, V, W]`` produces output of type ``W`` by first parsing
        # the input as ``U`` and then through the intermediate type ``V``,
        # unless the input already parses directly with ``W``.
        #
        # {{CHAIN_GENERAL_BEHAVIOR}}
        #
        # Type Args:
        #     U: {{CHAIN_TYPEARG_INPUT}}
        #     V: {{CHAIN_TYPEARG_FIRST_INTERMEDIATE}}
        #     W: {{CHAIN_TYPEARG_OUTPUT}}
        #
        # See [`Chain2`][omnipy.components.general.models.Chain2] for an example.
        """Convert data through a three-model chain.

        ``Chain3[U, V, W]`` produces output of type ``W`` by first parsing
        the input as ``U`` and then through the intermediate type ``V``,
        unless the input already parses directly with ``W``.

        This provides a lightweight inline dataflow pipeline within a single
        model.

        Chain type parameters must be model or dataset types. Input data may
        be any content that validates directly against the output type or,
        if that fails, against the first type in the chain. When the input
        validates against the output type, the chain short-circuits
        immediately. Otherwise, the data is validated against the first type
        and then validated forward through each subsequent model or dataset
        type until the output type is reached. The final result conforms to
        the output type unless validation fails during the chain.


        Type Args:
            U: The input model or dataset type.
            V: The first intermediate model or dataset type.
            W: The output model or dataset type.

        See [`Chain2`][omnipy.components.general.models.Chain2] for an example."""

        ...

    class Chain4(
        _ChainMixin, Model[_X | TypeVarStore2[_W] | TypeVarStore1[_V] | _U], Generic[_U, _V, _W, _X]
    ):
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # Convert data through a four-model chain.
        #
        # ``Chain4[U, V, W, X]`` produces output of type ``X`` by first
        # parsing the input as ``U`` and then through the intermediate types
        # ``V`` and ``W``, unless the input already parses directly with
        # ``X``.
        #
        # {{CHAIN_GENERAL_BEHAVIOR}}
        #
        # Type Args:
        #     U: {{CHAIN_TYPEARG_INPUT}}
        #     V: {{CHAIN_TYPEARG_FIRST_INTERMEDIATE}}
        #     W: {{CHAIN_TYPEARG_SECOND_INTERMEDIATE}}
        #     X: {{CHAIN_TYPEARG_OUTPUT}}
        #
        # See [`Chain2`][omnipy.components.general.models.Chain2] for an example.
        """Convert data through a four-model chain.

        ``Chain4[U, V, W, X]`` produces output of type ``X`` by first
        parsing the input as ``U`` and then through the intermediate types
        ``V`` and ``W``, unless the input already parses directly with
        ``X``.

        This provides a lightweight inline dataflow pipeline within a single
        model.

        Chain type parameters must be model or dataset types. Input data may
        be any content that validates directly against the output type or,
        if that fails, against the first type in the chain. When the input
        validates against the output type, the chain short-circuits
        immediately. Otherwise, the data is validated against the first type
        and then validated forward through each subsequent model or dataset
        type until the output type is reached. The final result conforms to
        the output type unless validation fails during the chain.


        Type Args:
            U: The input model or dataset type.
            V: The first intermediate model or dataset type.
            W: The second intermediate model or dataset type.
            X: The output model or dataset type.

        See [`Chain2`][omnipy.components.general.models.Chain2] for an example."""

        ...

    class Chain5(
        _ChainMixin,
        Model[_Y | TypeVarStore3[_X] | TypeVarStore2[_W] | TypeVarStore1[_V] | _U],
        Generic[_U, _V, _W, _X, _Y],
    ):
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # Convert data through a five-model chain.
        #
        # ``Chain5[U, V, W, X, Y]`` produces output of type ``Y`` by first
        # parsing the input as ``U`` and then through three intermediate
        # types, unless the input already parses directly with ``Y``.
        #
        # {{CHAIN_GENERAL_BEHAVIOR}}
        #
        # Type Args:
        #     U: {{CHAIN_TYPEARG_INPUT}}
        #     V: {{CHAIN_TYPEARG_FIRST_INTERMEDIATE}}
        #     W: {{CHAIN_TYPEARG_SECOND_INTERMEDIATE}}
        #     X: {{CHAIN_TYPEARG_THIRD_INTERMEDIATE}}
        #     Y: {{CHAIN_TYPEARG_OUTPUT}}
        #
        # See [`Chain2`][omnipy.components.general.models.Chain2] for an example.
        """Convert data through a five-model chain.

        ``Chain5[U, V, W, X, Y]`` produces output of type ``Y`` by first
        parsing the input as ``U`` and then through three intermediate
        types, unless the input already parses directly with ``Y``.

        This provides a lightweight inline dataflow pipeline within a single
        model.

        Chain type parameters must be model or dataset types. Input data may
        be any content that validates directly against the output type or,
        if that fails, against the first type in the chain. When the input
        validates against the output type, the chain short-circuits
        immediately. Otherwise, the data is validated against the first type
        and then validated forward through each subsequent model or dataset
        type until the output type is reached. The final result conforms to
        the output type unless validation fails during the chain.


        Type Args:
            U: The input model or dataset type.
            V: The first intermediate model or dataset type.
            W: The second intermediate model or dataset type.
            X: The third intermediate model or dataset type.
            Y: The output model or dataset type.

        See [`Chain2`][omnipy.components.general.models.Chain2] for an example."""

        ...

    class Chain6(
        _ChainMixin,
        Model[
            _Z | TypeVarStore4[_Y] | TypeVarStore3[_X] | TypeVarStore2[_W] | TypeVarStore1[_V] | _U
        ],
        Generic[_U, _V, _W, _X, _Y, _Z],
    ):
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # Convert data through a six-model chain.
        #
        # ``Chain6[U, V, W, X, Y, Z]`` produces output of type ``Z`` by first
        # parsing the input as ``U`` and then through four intermediate
        # types, unless the input already parses directly with ``Z``.
        #
        # {{CHAIN_GENERAL_BEHAVIOR}}
        #
        # Type Args:
        #     U: {{CHAIN_TYPEARG_INPUT}}
        #     V: {{CHAIN_TYPEARG_FIRST_INTERMEDIATE}}
        #     W: {{CHAIN_TYPEARG_SECOND_INTERMEDIATE}}
        #     X: {{CHAIN_TYPEARG_THIRD_INTERMEDIATE}}
        #     Y: {{CHAIN_TYPEARG_FOURTH_INTERMEDIATE}}
        #     Z: {{CHAIN_TYPEARG_OUTPUT}}
        #
        # See [`Chain2`][omnipy.components.general.models.Chain2] for an example.
        """Convert data through a six-model chain.

        ``Chain6[U, V, W, X, Y, Z]`` produces output of type ``Z`` by first
        parsing the input as ``U`` and then through four intermediate
        types, unless the input already parses directly with ``Z``.

        This provides a lightweight inline dataflow pipeline within a single
        model.

        Chain type parameters must be model or dataset types. Input data may
        be any content that validates directly against the output type or,
        if that fails, against the first type in the chain. When the input
        validates against the output type, the chain short-circuits
        immediately. Otherwise, the data is validated against the first type
        and then validated forward through each subsequent model or dataset
        type until the output type is reached. The final result conforms to
        the output type unless validation fails during the chain.


        Type Args:
            U: The input model or dataset type.
            V: The first intermediate model or dataset type.
            W: The second intermediate model or dataset type.
            X: The third intermediate model or dataset type.
            Y: The fourth intermediate model or dataset type.
            Z: The output model or dataset type.

        See [`Chain2`][omnipy.components.general.models.Chain2] for an example."""

        ...


AllChainTypes: tuple[type[IsModel], ...] = (Chain2, Chain3, Chain4, Chain5, Chain6)


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
        {<class 'int'>: [1, 2], <class 'str'>: ['a'], list[int]: [[3]], list[str]: [['b']]}
    """

    @classmethod
    def _parse_data(cls, data: Model[list]) -> Model[dict[type | GenericAlias, list]]:
        grouped: dict[type, list] = defaultdict(list)

        def _iter_union_type(seq: Iterable):
            return Union[tuple(type(item) for item in seq)]  # noqa: UP007

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
        NotIterableExceptStrOrBytesModel('1234')
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

        assert isinstance(data, str) or isinstance(data, bytes) or not is_iterable(data), (
            f'Data of type {type(data)} is iterable'
        )

        return data


if TYPE_CHECKING:

    class ConverterModel(PlainModel[_ToT], Generic[_FromT, _ToT]):
        @property
        @override
        def content(self) -> _ToT: ...

        @content.setter
        @override
        def content(self, value: _FromT | _ToT) -> None: ...

        @classmethod
        def convert(cls, data: _FromT) -> _ToT: ...

        @classmethod
        def convert_all(cls, sequence_data: Sequence[_FromT]) -> Iterator[_ToT]: ...

        @classmethod
        def convert_all_items(
            cls,
            mapping_data: Mapping[_KeyT, _FromT],
        ) -> Iterator[tuple[_KeyT, _ToT]]: ...
else:

    class ConverterModel(Model[_FromT | _ToT], ABC, Generic[_FromT, _ToT]):
        @override
        def __class_getitem__(  # pyright: ignore[reportIncompatibleMethodOverride]
            cls,
            params: tuple[type[_FromT], type[_ToT]],
        ) -> type[Model[_FromT | _ToT]]:
            if cls is __class__:  # Only perform checks for the base class, not subclasses
                from_t, to_t = params
                for from_t_variant in all_type_variants(from_t):
                    if isinstance(from_t_variant, GenericAlias):
                        # Reject things like list[int], dict[str, int]
                        raise TypeError(
                            'Parameterized generics not allowed for FromT: '
                            f'{from_t_variant}. If you want to use a generic '
                            'type, wrap it in a Model subclass instead, e.g.:'
                            f'Model[{from_t_variant}].',
                        )
                    if from_t_variant == to_t:
                        raise TypeError(f'FromT and ToT cannot be the same type: {from_t_variant}.')
            return super().__class_getitem__(params)

        @property
        @override
        def content(self) -> _ToT:
            return cast(_ToT, super().content)

        @content.setter
        @override
        def content(self, value: _FromT | _ToT) -> None:
            super_cls = super(ConverterModel, ConverterModel)
            super_cls.content.fset(self, value)  # type: ignore[attr-defined]

        @classmethod
        @abstractmethod
        def _convert(cls, data: _FromT) -> _ToT: ...

        @classmethod
        def _parse_data(cls, data: _FromT | _ToT) -> _ToT:
            # Sanity check
            assert is_union(cls.outer_type()) and len(get_args(cls.full_type())) > 1
            from_classes = get_args(cls.full_type())[:-1]

            if isinstance(data, from_classes):
                converted_data = cls._convert(cast(_FromT, data))
                return converted_data
            else:
                return cast(_ToT, data)

        @classmethod
        def convert(cls, data: _FromT) -> _ToT:
            return cls(data).content

        @classmethod
        def convert_all(cls, sequence_data: Sequence[_FromT]) -> Iterator[_ToT]:
            for el in sequence_data:
                yield cls(el).content

        @classmethod
        def convert_all_items(
            cls,
            mapping_data: Mapping[_KeyT, _FromT],
        ) -> Iterator[tuple[_KeyT, _ToT]]:
            for key, val in mapping_data.items():
                yield key, cls(val).content


_AddT = TypeVar('_AddT', bound=SupportsAdd, default=SupportsAdd)


class AddAllValuesModel(
    ConverterModel[Model[SupportsItems[str, _AddT] | Iterable[_AddT]], _AddT],
    Generic[_AddT],
):
    """Add mapping values or iterable elements in their original order.

    The first value supplies the initial accumulator, so no numeric zero or other
    identity is assumed. Aggregation requires at least one value. Input already
    accepted as the output type passes through under ``ConverterModel`` semantics.
    Addition uses ``+`` rather than in-place addition to preserve input lists and
    other mutable values. The content is the added value itself.
    """

    @classmethod
    def _convert(cls, data: Model[SupportsItems[str, _AddT] | Iterable[_AddT]]) -> _AddT:
        result = None

        def _add_to_result(result: _AddT | None, item: _AddT) -> _AddT:
            if result is None:
                result = item
            else:
                result = result + item
            return result

        if has_items_method(data):
            for _key, value in data.items():
                result = _add_to_result(result, value)
        else:
            for item in cast(Iterable[_AddT], data):
                result = _add_to_result(result, item)

        if result is None:
            raise ValueError('Cannot add an empty iterable')

        return result


class EnumeratedListOfTuplesModel(Model[list[tuple[int, _ItemT]]], Generic[_ItemT]):
    """A Model for explicit list positions.

    Its data consists of ordered ``(index, value)`` pairs. The indices must
    form the contiguous sequence ``0, 1, ...``; validation rejects gaps,
    reordering, and a non-zero first index.

    This Model marks list data whose positions have already been made explicit.
    """

    @classmethod
    def _parse_data(cls, data: list[tuple[int, _ItemT]]) -> list[tuple[int, _ItemT]]:
        for expected_index, (actual_index, _) in enumerate(data):
            if expected_index != actual_index:
                raise ValueError(
                    f'Indices are not sequential starting from 0: '
                    f'expected {expected_index}, got {actual_index}'
                )
        return data


class EnumeratedListModel(
    Model[EnumeratedListOfTuplesModel | Model[list[_ItemT]] | list[dict[str, _ItemT]]],
    Generic[_ItemT],
):
    """A Model converting list or dict data items into a list of enumerated tuples

    Ordinary list and dict input items are given explicit zero-based
    positions in an ``EnumeratedListOfTuplesModel``. Input that is already
    an ``EnumeratedListOfTuplesModel`` is retained as such.
    """

    @classmethod
    def _parse_data(
        cls, data: EnumeratedListOfTuplesModel | Model[list[_ItemT]] | list[dict[str, _ItemT]]
    ) -> EnumeratedListOfTuplesModel:
        if not isinstance(data, EnumeratedListOfTuplesModel):
            return EnumeratedListOfTuplesModel(list(enumerate(data)))  # pyright: ignore
        else:
            return data


class EnumeratedDatasetModel(
    Chain2[EnumeratedListModel[_ItemT], Dataset[Model[_ItemT]]], Generic[_ItemT]
):
    """A Model convert list or dict data items into an enurmater Dataset.

    Ordinary list and dict input items are given explicit zero-based
    positions in an ``Dataset[Model[_ItemT]]``. Input that is already
    an ``Dataset[Model[_ItemT]]`` is retained as such.
    """


class PrimaryKeyDatasetModel(
    ConverterModel[
        Dataset[Model[_RecordT]] | Model[list[_RecordT]],
        TypeVarStore[_PrimaryKeyT] | Dataset[Model[_RecordT]],
    ],
    Generic[_PrimaryKeyT, _RecordT],
    metaclass=PrimaryKeyModelMetaclass,
):
    """Key validated Pydantic records by their declared primary-key fields.

    Keys are recomputed from visible record fields in declaration order. Duplicate
    serialized keys are rejected before a Dataset is constructed, including keys
    with different Python values that stringify identically.
    """

    @classmethod
    def _convert(
        cls, data: Dataset[Model[_RecordT]] | Model[list[_RecordT]]
    ) -> Dataset[Model[_RecordT]]:
        if is_dataset_instance(data):
            record_type = cast(type[_RecordT], data.get_type().inner_type())
            records = data.values()
        else:
            record_type = cast(type[_RecordT], data.inner_type())
            records = data

        key_fields = cls.primary_key

        for field in key_fields:
            if field not in record_type.__fields__:
                raise ValueError(f'Unknown primary-key field: {field!r}')

        keyed_records = {}
        for record in records:
            key = serialize_primary_key(getattr(record, field) for field in key_fields)
            if key in keyed_records:
                raise ValueError(f'Duplicate serialized primary key: {key!r}')
            keyed_records[key] = record

        return Dataset[Model[record_type]](keyed_records)  # type: ignore[valid-type]


class MergeListsOfRecordsIntoDatasetByPrimaryKeyModel(
    Chain2[AddAllValuesModel[list[_RecordT]], PrimaryKeyDatasetModel[_PrimaryKeyT, _RecordT]],
    Generic[_PrimaryKeyT, _RecordT],
):
    """Merge record-list pages into a Dataset with unique serialized primary keys."""


class MergeListsOfRecordsIntoDatasetByIndexModel(
    Chain2[AddAllValuesModel[list[_RecordT]], EnumeratedDatasetModel[_RecordT]],
    Generic[_RecordT],
):
    """Merge record-list pages into a Dataset with consecutive positional keys."""
