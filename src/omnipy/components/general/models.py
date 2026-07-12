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
from omnipy.util.helpers import is_package_editable, is_iterable, is_non_str_byte_iterable

if is_package_editable('omnipy'):
    import os
    from textwrap import dedent

    os.environ['OMNIPY_MACRO_CHAIN_TYPEARG_INPUT'] = 'The input model or dataset type.'

    os.environ['OMNIPY_MACRO_CHAIN_TYPEARG_FIRST_INTERMEDIATE'] = (
        'The first intermediate model or dataset type.')

    os.environ['OMNIPY_MACRO_CHAIN_TYPEARG_SECOND_INTERMEDIATE'] = (
        'The second intermediate model or dataset type.')

    os.environ['OMNIPY_MACRO_CHAIN_TYPEARG_THIRD_INTERMEDIATE'] = (
        'The third intermediate model or dataset type.')

    os.environ['OMNIPY_MACRO_CHAIN_TYPEARG_FOURTH_INTERMEDIATE'] = (
        'The fourth intermediate model or dataset type.')

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
        # Examples:
        #     >>> import omnipy as om
        #     >>> class SplitCharsModel(om.Model[list[str] | str]):
        #     ...     @classmethod
        #     ...     def _parse_data(cls, data):
        #     ...         return list(data) if isinstance(data, str) else data
        #     >>> class TupleCharsModel(om.Model[tuple[str, ...] | list[str]]):
        #     ...     @classmethod
        #     ...     def _parse_data(cls, data):
        #     ...         return tuple(data) if isinstance(data, list) else data
        #     >>> chain = om.Chain3[om.Model[str], SplitCharsModel, TupleCharsModel]
        #     >>> chain('abc')
        #     Chain3[Model[str], SplitCharsModel, TupleCharsModel](TupleCharsModel(('a', 'b', 'c')))
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

        Examples:
            >>> import omnipy as om
            >>> class SplitCharsModel(om.Model[list[str] | str]):
            ...     @classmethod
            ...     def _parse_data(cls, data):
            ...         return list(data) if isinstance(data, str) else data
            >>> class TupleCharsModel(om.Model[tuple[str, ...] | list[str]]):
            ...     @classmethod
            ...     def _parse_data(cls, data):
            ...         return tuple(data) if isinstance(data, list) else data
            >>> chain = om.Chain3[om.Model[str], SplitCharsModel, TupleCharsModel]
            >>> chain('abc')
            Chain3[Model[str], SplitCharsModel, TupleCharsModel](TupleCharsModel(('a', 'b', 'c')))

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
        # Examples:
        #     >>> import omnipy as om
        #     >>> class SplitCharsModel(om.Model[list[str] | str]):
        #     ...     @classmethod
        #     ...     def _parse_data(cls, data):
        #     ...         return list(data) if isinstance(data, str) else data
        #     >>> class TupleCharsModel(om.Model[tuple[str, ...] | list[str]]):
        #     ...     @classmethod
        #     ...     def _parse_data(cls, data):
        #     ...         return tuple(data) if isinstance(data, list) else data
        #     >>> chain = om.Chain3[om.Model[str], SplitCharsModel, TupleCharsModel]
        #     >>> chain('abc')
        #     Chain3[Model[str], SplitCharsModel, TupleCharsModel](TupleCharsModel(('a', 'b', 'c')))
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

        Examples:
            >>> import omnipy as om
            >>> class SplitCharsModel(om.Model[list[str] | str]):
            ...     @classmethod
            ...     def _parse_data(cls, data):
            ...         return list(data) if isinstance(data, str) else data
            >>> class TupleCharsModel(om.Model[tuple[str, ...] | list[str]]):
            ...     @classmethod
            ...     def _parse_data(cls, data):
            ...         return tuple(data) if isinstance(data, list) else data
            >>> chain = om.Chain3[om.Model[str], SplitCharsModel, TupleCharsModel]
            >>> chain('abc')
            Chain3[Model[str], SplitCharsModel, TupleCharsModel](TupleCharsModel(('a', 'b', 'c')))

        See [`Chain2`][omnipy.components.general.models.Chain2] for an example."""
        ...

    class Chain4(_ChainMixin,
                 Model[_X | TypeVarStore2[_W] | TypeVarStore1[_V] | _U],
                 Generic[_U, _V, _W, _X]):
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
            Model[_Z | TypeVarStore4[_Y] | TypeVarStore3[_X] | TypeVarStore2[_W] | TypeVarStore1[_V]
                  | _U],
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
