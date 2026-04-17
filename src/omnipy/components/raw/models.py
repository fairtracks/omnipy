from typing import Callable, cast, Generic, Protocol, TypeAlias

from typing_extensions import TypeVar

from omnipy.data.model import Model
from omnipy.data.param import bind_adjust_model_func, params_dataclass, ParamsBase
from omnipy.shared.protocols.content import (IsBytesContent,
                                             IsListContent,
                                             IsListOfListsContent,
                                             IsStrContent)
from omnipy.shared.typing import TYPE_CHECKING
import omnipy.util.pydantic as pyd

if TYPE_CHECKING:
    from omnipy.data.model import PlainModel


class _EncodingParamsMixin:
    @params_dataclass
    class Params(ParamsBase):
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
    adjust = bind_adjust_model_func(
        _BytesModel.clone_model_cls,
        _EncodingParamsMixin.Params,
    )


if TYPE_CHECKING:

    class StrictBytesModel(PlainModel[bytes], IsBytesContent):
        ...
else:

    class StrictBytesModel(Model[pyd.StrictBytes]):
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
    adjust = bind_adjust_model_func(
        _StrModel.clone_model_cls,
        _EncodingParamsMixin.Params,
    )


if TYPE_CHECKING:

    class StrictStrModel(PlainModel[str], IsStrContent):
        ...
else:

    class StrictStrModel(Model[pyd.StrictStr]):
        ...


# Protocols for split mixins


class _HasSplitParams(Protocol):
    class Params:
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
        delimiter: str = ','


class _SplitByTabParamsMixin:
    @params_dataclass
    class Params(_SplitParamsBase):
        delimiter: str = '\t'


class _SplitByNewlineParamsMixin:
    @params_dataclass
    class Params(_SplitParamsBase):
        delimiter: str = '\n'


# Split models

if TYPE_CHECKING:

    class SplitToItemsModelBase(PlainModel[list[str]], IsListContent[str]):
        ...

else:

    class SplitToItemsModelBase(Model[list[str] | str]):
        @classmethod
        def _parse_data(cls: type[_HasSplitParams], data: list[str] | str) -> list[str]:
            if isinstance(data, list):
                return data

            return _split_line(cls, data)


class SplitToItemsModel(_SplitByCommaParamsMixin, SplitToItemsModelBase):
    adjust = bind_adjust_model_func(
        SplitToItemsModelBase.clone_model_cls,
        _SplitByCommaParamsMixin.Params,
    )


class SplitToItemsByTabModel(_SplitByTabParamsMixin, SplitToItemsModelBase):
    adjust = bind_adjust_model_func(
        SplitToItemsModelBase.clone_model_cls,
        _SplitByTabParamsMixin.Params,
    )


class SplitToLinesModel(_SplitByNewlineParamsMixin, SplitToItemsModelBase):
    adjust = bind_adjust_model_func(
        SplitToItemsModelBase.clone_model_cls,
        _SplitByNewlineParamsMixin.Params,
    )


if TYPE_CHECKING:

    class SplitItemsToSubitemsModelBase(
            PlainModel[list[list[str]]],
            IsListOfListsContent[list[str], str],
    ):
        ...

else:

    class SplitItemsToSubitemsModelBase(Model[list[list[str]] | list[str] | list[StrModel]]):
        @classmethod
        def _parse_data(cls: type[_HasSplitParams],
                        data: list[list[str]] | list[str] | list[StrModel]) -> list[list[str]]:
            if isinstance(data, list) and (len(data) == 0 or isinstance(data[0], list)):
                return cast(list[list[str]], data)

            return [_split_line(cls, cast(str, line)) for line in data]


class SplitItemsToSubitemsModel(_SplitByCommaParamsMixin, SplitItemsToSubitemsModelBase):
    adjust = bind_adjust_model_func(
        SplitItemsToSubitemsModelBase.clone_model_cls,
        _SplitByCommaParamsMixin.Params,
    )


class SplitLinesToColumnsModel(_SplitByTabParamsMixin, SplitItemsToSubitemsModelBase):
    adjust = bind_adjust_model_func(
        SplitItemsToSubitemsModelBase.clone_model_cls,
        _SplitByTabParamsMixin.Params,
    )


class SplitLinesToColumnsByCommaModel(_SplitByCommaParamsMixin, SplitItemsToSubitemsModelBase):
    adjust = bind_adjust_model_func(
        SplitItemsToSubitemsModelBase.clone_model_cls,
        _SplitByCommaParamsMixin.Params,
    )


# Protocols for join mixins


class _HasJoinParams(Protocol):
    class Params:
        delimiter: str


# Function to join items


def _join_items(model_cls: type[_HasJoinParams], data: list[str]) -> str:
    return model_cls.Params.delimiter.join(data)


# Mixins for join models


class _JoinByCommaParamsMixin:
    @params_dataclass
    class Params(ParamsBase):
        delimiter: str = ','


class _JoinByTabParamsMixin:
    @params_dataclass
    class Params(ParamsBase):
        delimiter: str = '\t'


class _JoinByNewlineParamsMixin:
    @params_dataclass
    class Params(ParamsBase):
        delimiter: str = '\n'


# Join models

if TYPE_CHECKING:

    class JoinItemsModelBase(PlainModel[str], IsStrContent):
        ...

else:

    class JoinItemsModelBase(Model[str | list[str]]):
        @classmethod
        def _parse_data(cls: type[_HasJoinParams], data: str | list[str]) -> str:
            if isinstance(data, str):
                return data

            return _join_items(cls, data)


class JoinItemsModel(_JoinByCommaParamsMixin, JoinItemsModelBase):
    adjust = bind_adjust_model_func(
        JoinItemsModelBase.clone_model_cls,
        _JoinByCommaParamsMixin.Params,
    )


class JoinLinesModel(_JoinByNewlineParamsMixin, JoinItemsModelBase):
    adjust = bind_adjust_model_func(
        JoinItemsModelBase.clone_model_cls,
        _JoinByNewlineParamsMixin.Params,
    )


if TYPE_CHECKING:

    class JoinSubitemsToItemsModelBase(PlainModel[list[str]], IsListContent[str]):
        ...

else:

    class JoinSubitemsToItemsModelBase(Model[list[str] | list[list[str]]]):
        @classmethod
        def _parse_data(cls: type[_HasJoinParams], data: list[str] | list[list[str]]) -> list[str]:
            if isinstance(data, list) and (len(data) == 0 or not isinstance(data[0], list)):
                return cast(list[str], data)

            return [_join_items(cls, cast(list[str], cols)) for cols in data]


class JoinSubitemsToItemsModel(_JoinByCommaParamsMixin, JoinSubitemsToItemsModelBase):
    adjust = bind_adjust_model_func(
        JoinSubitemsToItemsModelBase.clone_model_cls,
        _JoinByCommaParamsMixin.Params,
    )


class JoinColumnsToLinesModel(_JoinByTabParamsMixin, JoinSubitemsToItemsModelBase):
    adjust = bind_adjust_model_func(
        JoinSubitemsToItemsModelBase.clone_model_cls,
        _JoinByTabParamsMixin.Params,
    )


class JoinColumnsByCommaToLinesModel(_JoinByCommaParamsMixin, JoinSubitemsToItemsModelBase):
    adjust = bind_adjust_model_func(
        JoinSubitemsToItemsModelBase.clone_model_cls,
        _JoinByCommaParamsMixin.Params,
    )


_NestedListsAndStrsWithModelsT = TypeVar(
    '_NestedListsAndStrsWithModelsT', bound='NestedListsAndStrsWithModels', default='str')

if TYPE_CHECKING:

    class ListOfNestedListsAndStrsModel(
            PlainModel[list[_NestedListsAndStrsWithModelsT]],
            IsListContent[_NestedListsAndStrsWithModelsT],
            Generic[_NestedListsAndStrsWithModelsT],
    ):
        ...
else:

    class ListOfNestedListsAndStrsModel(
            Model[list[_NestedListsAndStrsWithModelsT]],
            Generic[_NestedListsAndStrsWithModelsT],
    ):
        ...


NestedListsAndStrsWithModels: TypeAlias = str | ListOfNestedListsAndStrsModel

ListOfNestedListsAndStrsModel.update_forward_refs()

ListOfNestedListsAndStrsNoModels: TypeAlias = list['NestedListsAndStrsNoModels']
NestedListsAndStrsNoModels: TypeAlias = str | ListOfNestedListsAndStrsNoModels

# Hack to support recursive types in Pydantic v1.10.x. Should not bee needed in Pydantic v2.
_NestedListsAndStrsNoModelsT = TypeVar(
    '_NestedListsAndStrsNoModelsT', default=str | list[NestedListsAndStrsNoModels])


class _NestedItemsParamsMixin:
    @params_dataclass
    class Params(ParamsBase):
        delimiters: tuple[str, ...] = ()

    @classmethod
    def _split_data_according_to_delimiters(
            cls,
            data: NestedListsAndStrsWithModels,
            level: int = 0) -> list[str] | ListOfNestedListsAndStrsNoModels:

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
            return cast(ListOfNestedListsAndStrsNoModels, split_data_no_list_models)
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
            PlainModel[list[_NestedListsAndStrsNoModelsT]],
            IsListContent[_NestedListsAndStrsNoModelsT],
            Generic[_NestedListsAndStrsNoModelsT],
            _NestedItemsParamsMixin,
    ):
        ...

else:

    class _NestedSplitToItemsModel(
            Model[list[_NestedListsAndStrsNoModelsT] | str],
            Generic[_NestedListsAndStrsNoModelsT],
            _NestedItemsParamsMixin,
    ):
        @classmethod
        def _parse_data(
            cls, data: list[_NestedListsAndStrsNoModelsT] | str
        ) -> list[_NestedListsAndStrsNoModelsT] | str:
            str_parsed_data = Model[NestedListsAndStrsWithModels](data).content
            return cls._split_data_according_to_delimiters(
                str_parsed_data,  # type: ignore[return-value]
            )


class NestedSplitToItemsModel(_NestedSplitToItemsModel):
    adjust = bind_adjust_model_func(
        cast(Callable[..., type[_NestedSplitToItemsModel]],
             _NestedSplitToItemsModel.clone_model_cls),
        _NestedSplitToItemsModel.Params,
    )


if TYPE_CHECKING:

    class _NestedJoinItemsModel(
            PlainModel[str],
            IsStrContent,
            Generic[_NestedListsAndStrsNoModelsT],
            _NestedItemsParamsMixin,
    ):
        ...

else:

    class _NestedJoinItemsModel(Model[str | list[_NestedListsAndStrsNoModelsT]],
                                Generic[_NestedListsAndStrsNoModelsT],
                                _NestedItemsParamsMixin):
        @classmethod
        def _join_data_according_to_delimiters(cls,
                                               data: str | list[_NestedListsAndStrsNoModelsT],
                                               level: int = 0) -> str:
            if isinstance(data, str):
                return data

            num_delimiters = len(cls.Params.delimiters)
            next_level = level + 1
            raw_data: list[str]
            if num_delimiters > next_level:
                raw_data = [
                    cls._join_data_according_to_delimiters(
                        cast(str | list[_NestedListsAndStrsNoModelsT], item), level=next_level)
                    for item in data
                ]
            else:
                raw_data = cast(list[str], data)

            if num_delimiters == 0:
                return ''.join(raw_data)
            else:
                return cls.Params.delimiters[level].join(raw_data)

        @classmethod
        def _parse_data(cls, data: str | list[_NestedListsAndStrsNoModelsT]) -> str:
            str_parsed_data = Model[NestedListsAndStrsWithModels](data).content
            return cls._join_data_according_to_delimiters(
                cls._split_data_according_to_delimiters(str_parsed_data),  # type: ignore[arg-type]
            )


class NestedJoinItemsModel(_NestedJoinItemsModel):
    adjust = bind_adjust_model_func(
        cast(Callable[..., type[_NestedJoinItemsModel]], _NestedJoinItemsModel.clone_model_cls),
        _NestedItemsParamsMixin.Params,
    )


# TODO: Make MatchItemsModel Generic. Generics are currently not supported by Parametrized Models.


class _MatchItemsParamsMixin:
    @params_dataclass
    class Params(ParamsBase):
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
    adjust = bind_adjust_model_func(
        _MatchItemsModel.clone_model_cls,
        _MatchItemsModel.Params,
    )
