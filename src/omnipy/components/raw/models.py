"""Raw text and binary models for encoding, splitting, joining, and filtering content."""

import os
from textwrap import dedent
from typing import Callable, cast, Generic, Protocol, TypeAlias

from typing_extensions import TypeVar

from omnipy.data.model import Model
from omnipy.data.param import bind_adjust_model_func, params_dataclass, ParamsBase
from omnipy.shared.protocols.content import (IsBytesContent,
                                             IsListContent,
                                             IsListOfListsContent,
                                             IsStrContent)
from omnipy.shared.typing import TYPE_CHECKING
from omnipy.util.helpers import is_package_editable
import omnipy.util.pydantic as pyd

if TYPE_CHECKING:
    from omnipy.data._typing.mimic_models import PlainModel


if is_package_editable('omnipy'):  # Only define environment variables when developing
    os.environ['OMNIPY_MACRO_SPLIT_PARAMS_VARIANT_SUMMARY'] = dedent("""\
        Split-parameter variant.

        Attributes:
            delimiter: Delimiter used when splitting item strings.
    """)

    os.environ['OMNIPY_MACRO_JOIN_PARAMS_VARIANT_SUMMARY'] = dedent("""\
        Join-parameter variant.

        Attributes:
            delimiter: Delimiter used when joining item strings.
    """)


class _EncodingParamsMixin:
    @params_dataclass
    class Params(ParamsBase):
        """Configure text/binary conversion encoding.

        Attributes:
            encoding: Codec used when coercing between ``str`` and ``bytes``.
        """

        encoding: str = 'utf-8'


if TYPE_CHECKING:

    class _BytesModel(PlainModel[bytes], IsBytesContent, _EncodingParamsMixin):
        ...
else:

    class _BytesModel(Model[bytes | str], _EncodingParamsMixin):
        @classmethod
        def _parse_data(cls, data: bytes | str) -> bytes:
            if isinstance(data, bytes):
                return data

            return data.encode(cls.Params.encoding)


class BytesModel(_BytesModel):
    """Store binary content with optional string-to-bytes coercion.

    This model accepts either ``bytes`` or ``str`` input. String input is
    encoded using the configured ``encoding`` parameter before storage.
    """

    adjust = bind_adjust_model_func(
        _BytesModel.clone_model_cls,
        _EncodingParamsMixin.Params,
    )


if TYPE_CHECKING:

    class StrictBytesModel(PlainModel[bytes], IsBytesContent):
        """Store binary content without implicit coercion.

        This type-checking variant mirrors the runtime ``StrictBytesModel`` and
        accepts values that are already bytes-compatible.
        """

        ...
else:

    class StrictBytesModel(Model[pyd.StrictBytes]):
        """Store binary content without string coercion.

        Unlike :class:`BytesModel`, this model only accepts values already
        provided as bytes-compatible input.
        """

        ...


if TYPE_CHECKING:

    class _StrModel(PlainModel[str], IsStrContent, _EncodingParamsMixin):
        ...
else:

    class _StrModel(Model[str | bytes], _EncodingParamsMixin):
        Params = _EncodingParamsMixin.Params

        @classmethod
        def _parse_data(cls, data: str | bytes) -> str:
            if isinstance(data, str):
                return data

            return data.decode(cls.Params.encoding)


class StrModel(_StrModel):
    """Store text content with optional bytes-to-string coercion.

    This model accepts either ``str`` or ``bytes`` input. Bytes input is
    decoded using the configured ``encoding`` parameter before storage.
    """

    adjust = bind_adjust_model_func(
        _StrModel.clone_model_cls,
        _EncodingParamsMixin.Params,
    )


if TYPE_CHECKING:

    class StrictStrModel(PlainModel[str], IsStrContent):
        """Store text content without implicit coercion.

        This type-checking variant mirrors the runtime ``StrictStrModel`` and
        accepts values that are already strict strings.
        """

        ...
else:

    class StrictStrModel(Model[pyd.StrictStr]):
        """Store text content without implicit coercion.

        Unlike :class:`StrModel`, this model only accepts strict string input
        and does not decode bytes automatically.
        """

        ...


# Protocols for split mixins


class _HasSplitParams(Protocol):
    class Params:
        """Protocol for split-model parameter access.

        Attributes:
            strip: Whether leading and trailing characters are stripped.
            strip_chars: Optional character set passed to ``str.strip``.
            delimiter: Delimiter used to split incoming text.
        """

        strip: bool
        strip_chars: str | None
        delimiter: str


# Function to split line


def _split_line(model_cls: type[_HasSplitParams], data: str) -> list[str]:
    strip = model_cls.Params.strip
    strip_chars = model_cls.Params.strip_chars
    delimiter = model_cls.Params.delimiter

    if strip:
        data = data.strip(strip_chars)

    items = data.split(delimiter)
    return [item.strip(strip_chars) for item in items] if strip else items


# Mixins for split models


@params_dataclass
class _SplitParamsBase(ParamsBase):
    strip: bool = True
    strip_chars: str | None = None


class _SplitByCommaParamsMixin:
    @params_dataclass
    class Params(_SplitParamsBase):
        """{{SPLIT_PARAMS_VARIANT_SUMMARY}}"""

        delimiter: str = ','


class _SplitByTabParamsMixin:
    @params_dataclass
    class Params(_SplitParamsBase):
        """{{SPLIT_PARAMS_VARIANT_SUMMARY}}"""

        delimiter: str = '\t'


class _SplitByNewlineParamsMixin:
    @params_dataclass
    class Params(_SplitParamsBase):
        """{{SPLIT_PARAMS_VARIANT_SUMMARY}}"""

        delimiter: str = '\n'


# Split models

if TYPE_CHECKING:

    class SplitToItemsModelBase(PlainModel[list[str]], IsListContent[str]):
        """Normalize text input into a flat list of string items.

        Input may be provided either as an existing list of strings or as one
        delimited string that should be split according to active parameters.
        """

        ...

else:

    class SplitToItemsModelBase(Model[list[str] | str]):
        """Normalize text input into a flat list of string items.

        Input may already be a list of strings or a single delimited string,
        which is split according to the active split-parameter mixin.
        """

        @classmethod
        def _parse_data(cls: type[_HasSplitParams], data: list[str] | str) -> list[str]:
            if isinstance(data, list):
                return data

            return _split_line(cls, data)


class SplitToItemsModel(_SplitByCommaParamsMixin, SplitToItemsModelBase):
    """Split a delimiter-separated string into items.

    By default this variant uses commas as delimiters and strips surrounding
    whitespace from each item.
    """

    adjust = bind_adjust_model_func(
        SplitToItemsModelBase.clone_model_cls,
        _SplitByCommaParamsMixin.Params,
    )


class SplitToItemsByTabModel(_SplitByTabParamsMixin, SplitToItemsModelBase):
    """Split tab-delimited text into a flat list of items.

    This variant uses tab delimiters and optional stripping behavior inherited
    from shared split parameters.
    """

    adjust = bind_adjust_model_func(
        SplitToItemsModelBase.clone_model_cls,
        _SplitByTabParamsMixin.Params,
    )


class SplitToLinesModel(_SplitByNewlineParamsMixin, SplitToItemsModelBase):
    """Split text into a list of lines.

    This variant uses newline delimiters by default and can optionally strip
    each line.
    """

    adjust = bind_adjust_model_func(
        SplitToItemsModelBase.clone_model_cls,
        _SplitByNewlineParamsMixin.Params,
    )


if TYPE_CHECKING:

    class SplitItemsToSubitemsModelBase(
            PlainModel[list[list[str]]],
            IsListOfListsContent[list[str], str],
    ):
        """Normalize input into a two-dimensional list of string items.

        Input may be provided as nested lists directly or as flat strings that
        are split into subitems.
        """

        ...

else:

    class SplitItemsToSubitemsModelBase(Model[list[list[str]] | list[str] | list[StrModel]]):
        """Normalize input into a two-dimensional list of string items.

        Input may be provided as already nested lists or as a list of strings
        that should each be split into subitems.
        """

        @classmethod
        def _parse_data(cls: type[_HasSplitParams],
                        data: list[list[str]] | list[str] | list[StrModel]) -> list[list[str]]:
            if isinstance(data, list) and (len(data) == 0 or isinstance(data[0], list)):
                return cast(list[list[str]], data)

            return [_split_line(cls, cast(str, line)) for line in data]


class SplitItemsToSubitemsModel(_SplitByCommaParamsMixin, SplitItemsToSubitemsModelBase):
    """Split each item into comma-delimited subitems.

    This model accepts either pre-split nested lists or a list of text items
    and returns a two-dimensional list representation.
    """

    adjust = bind_adjust_model_func(
        SplitItemsToSubitemsModelBase.clone_model_cls,
        _SplitByCommaParamsMixin.Params,
    )


class SplitLinesToColumnsModel(_SplitByTabParamsMixin, SplitItemsToSubitemsModelBase):
    """Split each line of text into tab-delimited columns.

    This model is useful for parsing TSV-like line collections into row/column
    structures.
    """

    adjust = bind_adjust_model_func(
        SplitItemsToSubitemsModelBase.clone_model_cls,
        _SplitByTabParamsMixin.Params,
    )


class SplitLinesToColumnsByCommaModel(_SplitByCommaParamsMixin, SplitItemsToSubitemsModelBase):
    """Split each line of text into comma-delimited columns.

    This model is useful for parsing CSV-like line collections into row/column
    structures.
    """

    adjust = bind_adjust_model_func(
        SplitItemsToSubitemsModelBase.clone_model_cls,
        _SplitByCommaParamsMixin.Params,
    )


# Protocols for join mixins


class _HasJoinParams(Protocol):
    class Params:
        """Protocol for join-model parameter access.

        Attributes:
            delimiter: Delimiter used to join string elements.
        """

        delimiter: str


# Function to join items


def _join_items(model_cls: type[_HasJoinParams], data: list[str]) -> str:
    return model_cls.Params.delimiter.join(data)


# Mixins for join models


class _JoinByCommaParamsMixin:
    @params_dataclass
    class Params(ParamsBase):
        """{{JOIN_PARAMS_VARIANT_SUMMARY}}"""

        delimiter: str = ','


class _JoinByTabParamsMixin:
    @params_dataclass
    class Params(ParamsBase):
        """{{JOIN_PARAMS_VARIANT_SUMMARY}}"""

        delimiter: str = '\t'


class _JoinByNewlineParamsMixin:
    @params_dataclass
    class Params(ParamsBase):
        """{{JOIN_PARAMS_VARIANT_SUMMARY}}"""

        delimiter: str = '\n'


# Join models

if TYPE_CHECKING:

    class JoinItemsModelBase(PlainModel[str], IsStrContent):
        """Normalize string-list input into one joined string.

        Input may already be a string or a list of strings that should be
        joined using the active delimiter parameters.
        """

        ...

else:

    class JoinItemsModelBase(Model[str | list[str]]):
        """Normalize string lists into a single joined string.

        Input may already be a string or a list of strings that should be
        joined according to the active join-parameter mixin.
        """

        @classmethod
        def _parse_data(cls: type[_HasJoinParams], data: str | list[str]) -> str:
            if isinstance(data, str):
                return data

            return _join_items(cls, data)


class JoinItemsModel(_JoinByCommaParamsMixin, JoinItemsModelBase):
    """Join a list of items into one string.

    This variant uses commas as delimiters by default.
    """

    adjust = bind_adjust_model_func(
        JoinItemsModelBase.clone_model_cls,
        _JoinByCommaParamsMixin.Params,
    )


class JoinLinesModel(_JoinByNewlineParamsMixin, JoinItemsModelBase):
    """Join items into newline-delimited text.

    This variant is useful for reconstructing multi-line text from an ordered
    list of line fragments.
    """

    adjust = bind_adjust_model_func(
        JoinItemsModelBase.clone_model_cls,
        _JoinByNewlineParamsMixin.Params,
    )


if TYPE_CHECKING:

    class JoinSubitemsToItemsModelBase(PlainModel[list[str]], IsListContent[str]):
        """Normalize nested string lists into a flat list of joined items.

        Input may already be flat or may contain nested lists that should be
        joined per sublist.
        """

        ...

else:

    class JoinSubitemsToItemsModelBase(Model[list[str] | list[list[str]]]):
        """Normalize nested string lists into a flat list of joined items.

        Input may already be a flat list of strings or nested lists where each
        sublist should be joined into one string item.
        """

        @classmethod
        def _parse_data(cls: type[_HasJoinParams], data: list[str] | list[list[str]]) -> list[str]:
            if isinstance(data, list) and (len(data) == 0 or not isinstance(data[0], list)):
                return cast(list[str], data)

            return [_join_items(cls, cast(list[str], cols)) for cols in data]


class JoinSubitemsToItemsModel(_JoinByCommaParamsMixin, JoinSubitemsToItemsModelBase):
    """Join nested subitem lists into flat comma-delimited items.

    This model accepts a list of lists and joins each inner list into one
    string item.
    """

    adjust = bind_adjust_model_func(
        JoinSubitemsToItemsModelBase.clone_model_cls,
        _JoinByCommaParamsMixin.Params,
    )


class JoinColumnsToLinesModel(_JoinByTabParamsMixin, JoinSubitemsToItemsModelBase):
    """Join column lists into tab-delimited lines.

    This model turns row/column table fragments into TSV-like line strings.
    """

    adjust = bind_adjust_model_func(
        JoinSubitemsToItemsModelBase.clone_model_cls,
        _JoinByTabParamsMixin.Params,
    )


class JoinColumnsByCommaToLinesModel(_JoinByCommaParamsMixin, JoinSubitemsToItemsModelBase):
    """Join column lists into comma-delimited lines.

    This model turns row/column table fragments into CSV-like line strings.
    """

    adjust = bind_adjust_model_func(
        JoinSubitemsToItemsModelBase.clone_model_cls,
        _JoinByCommaParamsMixin.Params,
    )


_NestedListsOfStrT = TypeVar('_NestedListsOfStrT', bound='NestedListsOfStr', default='str')

if TYPE_CHECKING:

    class ListOfNestedListsOfStrModel(
            PlainModel[list[_NestedListsOfStrT]],
            IsListContent[_NestedListsOfStrT],
            Generic[_NestedListsOfStrT],
    ):
        """Represent recursive list nesting for string-based structures.

        This generic wrapper models lists where elements may themselves be
        recursively nested list structures containing strings.
        """

        ...
else:

    class ListOfNestedListsOfStrModel(
            Model[list[_NestedListsOfStrT]],
            Generic[_NestedListsOfStrT],
    ):
        """Represent lists that recursively contain nested string lists.

        This generic wrapper supports recursive string-list type composition
        used by nested split/join models.
        """

        ...


NestedListsOfStr: TypeAlias = str | ListOfNestedListsOfStrModel


class NestedListsOfStrModel(Model[NestedListsOfStr]):
    """Represent either a string or recursively nested lists of strings.

    This union model normalizes recursive list/string input before nested split
    and join transformations.
    """

    ...


ListOfNestedListsOfStrModel.update_forward_refs()

ListOfNestedPlainListsOfStr: TypeAlias = list['NestedPlainListsOfStr']
NestedPlainListsOfStr: TypeAlias = str | ListOfNestedPlainListsOfStr

# Hack to support recursive types in Pydantic v1.10.x. Should not be needed in Pydantic v2.
_NestedPlainListsOfStrT = TypeVar(
    '_NestedPlainListsOfStrT', default=str | list[NestedPlainListsOfStr])


class _NestedItemsParamsMixin:
    @params_dataclass
    class Params(ParamsBase):
        """Configure delimiter hierarchy for nested split/join operations.

        Attributes:
            delimiters: Ordered delimiter tuple applied by nesting level.
        """

        delimiters: tuple[str, ...] = ()

    @classmethod
    def _split_data_according_to_delimiters(
        cls,
        data: NestedListsOfStr,
        level: int = 0,
    ) -> list[str] | ListOfNestedPlainListsOfStr:

        raw_data = data if isinstance(data, str) else data.content

        num_delimiters = len(cls.Params.delimiters)

        if level == 0 and len(raw_data) == 0:
            return []

        if isinstance(raw_data, str):
            if num_delimiters == 0:
                return [raw_data]

            split_data = raw_data.split(cls.Params.delimiters[level])
        else:
            split_data = raw_data

        next_level = level + 1

        if num_delimiters == next_level:
            assert len(split_data) > 1, \
                (f'Data at bottom level (level {level}) must contain at '
                 f'least one delimiter or equivalently be pre-split into '
                 f'more than one item (bottom delimiter: '
                 f'{cls.Params.delimiters[level]}): {split_data}')
        if num_delimiters > next_level:
            split_data_no_list_models = [
                cls._split_data_according_to_delimiters(item, level=next_level)
                for item in split_data
            ]
            return cast(ListOfNestedPlainListsOfStr, split_data_no_list_models)
        else:
            if num_delimiters == 0:
                assert isinstance(data, str), \
                    'Data must be an string if no delimiters are provided.'
            else:  # 0 < num_delimiters <= next_level
                assert all(isinstance(item, str) for item in raw_data), \
                    (f'Data is nested higher than permitted by the number of delimiters in '
                     f'Params (={num_delimiters}).')

            return split_data


if TYPE_CHECKING:

    class _NestedSplitToItemsModel(
            PlainModel[list[_NestedPlainListsOfStrT]],
            IsListContent[_NestedPlainListsOfStrT],
            Generic[_NestedPlainListsOfStrT],
            _NestedItemsParamsMixin,
    ):
        ...

else:

    class _NestedSplitToItemsModel(
            Model[list[_NestedPlainListsOfStrT] | str],
            Generic[_NestedPlainListsOfStrT],
            _NestedItemsParamsMixin,
    ):
        @classmethod
        def _parse_data(
                cls,
                data: list[_NestedPlainListsOfStrT] | str) -> list[_NestedPlainListsOfStrT] | str:
            str_parsed_data = NestedListsOfStrModel(data).content
            return cls._split_data_according_to_delimiters(
                str_parsed_data,  # type: ignore[return-value]
            )


class NestedSplitToItemsModel(_NestedSplitToItemsModel):
    """Recursively split string content using a delimiter hierarchy.

    Delimiters are applied level by level so text can be transformed into a
    nested list shape.
    """

    adjust = bind_adjust_model_func(
        cast(Callable[..., type[_NestedSplitToItemsModel]],
             _NestedSplitToItemsModel.clone_model_cls),
        _NestedSplitToItemsModel.Params,
    )


if TYPE_CHECKING:

    class _NestedJoinItemsModel(
            PlainModel[str],
            IsStrContent,
            Generic[_NestedPlainListsOfStrT],
            _NestedItemsParamsMixin,
    ):
        ...

else:

    class _NestedJoinItemsModel(Model[str | list[_NestedPlainListsOfStrT]],
                                Generic[_NestedPlainListsOfStrT],
                                _NestedItemsParamsMixin):
        @classmethod
        def _join_data_according_to_delimiters(cls,
                                               data: str | list[_NestedPlainListsOfStrT],
                                               level: int = 0) -> str:
            if isinstance(data, str):
                return data

            num_delimiters = len(cls.Params.delimiters)
            next_level = level + 1
            raw_data: list[str]
            if num_delimiters > next_level:
                raw_data = [
                    cls._join_data_according_to_delimiters(
                        cast(str | list[_NestedPlainListsOfStrT], item), level=next_level)
                    for item in data
                ]
            else:
                raw_data = cast(list[str], data)

            if num_delimiters == 0:
                return ''.join(raw_data)
            else:
                return cls.Params.delimiters[level].join(raw_data)

        @classmethod
        def _parse_data(cls, data: str | list[_NestedPlainListsOfStrT]) -> str:
            str_parsed_data = NestedListsOfStrModel(data).content
            return cls._join_data_according_to_delimiters(
                cls._split_data_according_to_delimiters(str_parsed_data),  # type: ignore[arg-type]
            )


class NestedJoinItemsModel(_NestedJoinItemsModel):
    """Recursively join nested string lists using a delimiter hierarchy.

    Delimiters are applied by nesting level to collapse structured list content
    into a single string.
    """

    adjust = bind_adjust_model_func(
        cast(Callable[..., type[_NestedJoinItemsModel]], _NestedJoinItemsModel.clone_model_cls),
        _NestedItemsParamsMixin.Params,
    )


# TODO: Make MatchItemsModel Generic. Generics are currently not supported by Parametrized Models.


class _MatchItemsParamsMixin:
    @params_dataclass
    class Params(ParamsBase):
        """Configure predicate-based filtering for string item lists.

        Attributes:
            match_functions: Predicate callables evaluated per item.
            invert_matches: Whether to invert predicate outcomes.
            match_all: Whether all predicates must match (otherwise any).
        """

        match_functions: tuple[Callable[[str], bool], ...] = ()
        invert_matches: bool = False
        match_all: bool = True


if TYPE_CHECKING:

    class _MatchItemsModel(
            PlainModel[list[str]],
            IsListContent[str],
            _MatchItemsParamsMixin,
    ):
        ...
else:

    class _MatchItemsModel(
            Model[list[str]],
            _MatchItemsParamsMixin,
    ):
        @classmethod
        def _parse_data(cls, data: list[str]) -> list[str]:
            match_functions = cls.Params.match_functions
            invert_matches = cls.Params.invert_matches

            if len(match_functions) == 0:
                return data

            logic_operator = all if cls.Params.match_all else any

            return [
                item for item in data
                if (logic_operator(match_func(item) for match_func in match_functions) is True)
                ^ invert_matches
            ]


class MatchItemsModel(_MatchItemsModel):
    """Filter a list of strings with configurable predicate functions.

    Matching behavior is controlled by configured predicate callables, optional
    inversion, and all-vs-any composition semantics.
    """

    adjust = bind_adjust_model_func(
        _MatchItemsModel.clone_model_cls,
        _MatchItemsModel.Params,
    )
