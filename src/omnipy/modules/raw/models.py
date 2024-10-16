from typing import Callable, cast, Generic, TypeAlias

from typing_extensions import TypeVar

from omnipy.data.helpers import obj_or_model_contents_isinstance
from omnipy.data.model import Model
from omnipy.data.param import bind_adjust_model_func, params_dataclass, ParamsBase


class _EncodingParamsMixin:
    @params_dataclass
    class Params(ParamsBase):
        encoding: str = 'utf-8'


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


class _StrModel(Model[str | bytes], _EncodingParamsMixin):
    Params = _EncodingParamsMixin.Params

    @classmethod
    def _parse_data(cls, data: str | bytes) -> str:
        if isinstance(data, str):
            return data

        return data.decode(cls.Params.encoding)

    ...


class StrModel(_StrModel):
    adjust = bind_adjust_model_func(
        _StrModel.clone_model_cls,
        _EncodingParamsMixin.Params,
    )


class _SplitToItemsMixin:
    @params_dataclass
    class Params(ParamsBase):
        strip: bool = True
        strip_chars: str | None = None
        delimiter: str = ','

    @classmethod
    def _split_line(cls, data: str) -> list[str]:
        strip = cls.Params.strip
        strip_chars = cls.Params.strip_chars
        delimiter = cls.Params.delimiter

        if strip:
            data = data.strip(strip_chars)

        items = data.split(delimiter)
        return [item.strip(strip_chars) for item in items] if strip else items


class _SplitToItemsModel(
        Model[list[str] | str],
        _SplitToItemsMixin,
):
    @classmethod
    def _parse_data(cls, data: list[str] | str) -> list[str]:
        if isinstance(data, list):
            return data

        return cls._split_line(data)


class SplitToItemsModel(_SplitToItemsModel):
    adjust = bind_adjust_model_func(
        _SplitToItemsModel.clone_model_cls,
        _SplitToItemsModel.Params,
    )


class _SplitToLinesParamsMixin:
    @params_dataclass
    class Params(ParamsBase):
        strip: bool = True
        strip_chars: str | None = None
        delimiter: str = '\n'


class SplitToLinesModel(_SplitToLinesParamsMixin, _SplitToItemsModel):
    adjust = bind_adjust_model_func(
        _SplitToItemsModel.clone_model_cls,
        _SplitToLinesParamsMixin.Params,
    )


class _SplitItemsToSubitemsModel(
        Model[list[list[str]] | list[str] | list[StrModel]],
        _SplitToItemsMixin,
):
    @classmethod
    def _parse_data(cls, data: list[list[str]] | list[str] | list[StrModel]) -> list[list[str]]:
        if isinstance(data, list) and (len(data) == 0 or isinstance(data[0], list)):
            return cast(list[list[str]], data)

        return [cls._split_line(cast(str, line)) for line in data]


class SplitItemsToSubitemsModel(_SplitItemsToSubitemsModel):
    adjust = bind_adjust_model_func(
        _SplitItemsToSubitemsModel.clone_model_cls,
        _SplitItemsToSubitemsModel.Params,
    )


class _SplitLinesToColumnsParamsMixin:
    @params_dataclass
    class Params(ParamsBase):
        strip: bool = True
        strip_chars: str | None = None
        delimiter: str = '\t'


class SplitLinesToColumnsModel(_SplitLinesToColumnsParamsMixin, _SplitItemsToSubitemsModel):
    adjust = bind_adjust_model_func(
        _SplitItemsToSubitemsModel.clone_model_cls,
        _SplitLinesToColumnsParamsMixin.Params,
    )


class _JoinItemsMixin:
    @params_dataclass
    class Params(ParamsBase):
        delimiter: str = ','

    @classmethod
    def _join_items(cls, data: list[str]) -> str:
        return cls.Params.delimiter.join(data)


class _JoinItemsModel(Model[str | list[str]], _JoinItemsMixin):
    @classmethod
    def _parse_data(cls, data: str | list[str]) -> str:
        if isinstance(data, str):
            return data

        return cls._join_items(data)

    ...


class JoinItemsModel(_JoinItemsModel):
    adjust = bind_adjust_model_func(
        _JoinItemsModel.clone_model_cls,
        _JoinItemsModel.Params,
    )


class _JoinLinesParamsMixin:
    @params_dataclass
    class Params(ParamsBase):
        delimiter: str = '\n'


class JoinLinesModel(_JoinLinesParamsMixin, _JoinItemsModel):
    adjust = bind_adjust_model_func(
        _JoinItemsModel.clone_model_cls,
        _JoinLinesParamsMixin.Params,
    )


class _JoinSubitemsToItemsModel(
        Model[list[str] | list[list[str]]],
        _JoinItemsMixin,
):
    @classmethod
    def _parse_data(cls, data: list[str] | list[list[str]]) -> list[str]:
        if isinstance(data, list) and (len(data) == 0 or not isinstance(data[0], list)):
            return cast(list[str], data)

        return [cls._join_items(cast(list[str], cols)) for cols in data]


class JoinSubitemsToItemsModel(_JoinSubitemsToItemsModel):
    adjust = bind_adjust_model_func(
        _JoinSubitemsToItemsModel.clone_model_cls,
        _JoinSubitemsToItemsModel.Params,
    )


class _JoinItemsByTabParamsMixin:
    @params_dataclass
    class Params(ParamsBase):
        delimiter: str = ('\t')


class JoinColumnsToLinesModel(_JoinItemsByTabParamsMixin, _JoinSubitemsToItemsModel):
    adjust = bind_adjust_model_func(
        _JoinSubitemsToItemsModel.clone_model_cls,
        _JoinItemsByTabParamsMixin.Params,
    )


NestedStrWithListModelsT = TypeVar(
    'NestedStrWithListModelsT', bound='NestedStrWithListModels', default='str')


class ListOfNestedStrModel(Model[list[NestedStrWithListModelsT]],
                           Generic[NestedStrWithListModelsT]):
    ...


NestedStrWithListModels: TypeAlias = str | ListOfNestedStrModel

ListOfNestedStrModel.update_forward_refs()

NestedStrNoListModelsT = TypeVar(
    'NestedStrNoListModelsT', default=str | list['NestedStrNoListModelsT'])  # type: ignore[misc]


class _NestedItemsParamsMixin:
    @params_dataclass
    class Params(ParamsBase):
        delimiters: tuple[str, ...] = ()

    @classmethod
    def _split_data_according_to_delimiters(cls,
                                            data: NestedStrWithListModels,
                                            level: int = 0) -> str | list[NestedStrNoListModelsT]:

        raw_data = cast(str | list[NestedStrWithListModels],
                        data if isinstance(data, str) else data.contents)

        num_delimiters = len(cls.Params.delimiters)

        if level == 0 and len(raw_data) == 0:
            return [] if num_delimiters > 0 else ''

        split_data: list[NestedStrWithListModels]
        if isinstance(raw_data, str):
            if num_delimiters == 0:
                return raw_data

            split_data = cast(list[NestedStrWithListModels],
                              raw_data.split(cls.Params.delimiters[level]))
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
            return cast(list[NestedStrNoListModelsT], split_data_no_list_models)
        else:
            if num_delimiters == 0:
                assert isinstance(data, str), \
                    'Data must be an string if no delimiters are provided.'
            else:
                assert not any(obj_or_model_contents_isinstance(item, list) for item in data), \
                    (f'Data is nested higher than permitted by the number of delimiters in '
                     f'Params (={num_delimiters}).')

        return cast(list[NestedStrNoListModelsT], split_data)


class _NestedSplitToItemsModel(Model[list[NestedStrNoListModelsT] | str],
                               Generic[NestedStrNoListModelsT],
                               _NestedItemsParamsMixin):
    @classmethod
    def _parse_data(cls,
                    data: list[NestedStrNoListModelsT] | str) -> list[NestedStrNoListModelsT] | str:
        str_parsed_data = Model[NestedStrWithListModels](data).contents
        return cls._split_data_according_to_delimiters(str_parsed_data)


class NestedSplitToItemsModel(_NestedSplitToItemsModel):
    adjust = bind_adjust_model_func(
        cast(Callable[..., type[_NestedSplitToItemsModel]],
             _NestedSplitToItemsModel.clone_model_cls),
        _NestedSplitToItemsModel.Params,
    )


class _NestedJoinItemsModel(Model[str | list[NestedStrNoListModelsT]],
                            Generic[NestedStrNoListModelsT],
                            _NestedItemsParamsMixin):
    @classmethod
    def _join_data_according_to_delimiters(cls,
                                           data: str | list[NestedStrNoListModelsT],
                                           level: int = 0) -> str:
        if isinstance(data, str):
            return data

        num_delimiters = len(cls.Params.delimiters)
        next_level = level + 1
        raw_data: list[str]
        if num_delimiters > next_level:
            raw_data = [
                cls._join_data_according_to_delimiters(
                    cast(str | list[NestedStrNoListModelsT], item), level=next_level)
                for item in data
            ]
        else:
            raw_data = cast(list[str], data)

        return cls.Params.delimiters[level].join(raw_data) if len(raw_data) > 0 else ''

    @classmethod
    def _parse_data(cls, data: str | list[NestedStrNoListModelsT]) -> str:
        str_parsed_data = Model[NestedStrWithListModels](data).contents
        return cls._join_data_according_to_delimiters(
            cls._split_data_according_to_delimiters(str_parsed_data))


class NestedJoinItemsModel(_NestedJoinItemsModel):
    adjust = bind_adjust_model_func(
        cast(Callable[..., type[_NestedJoinItemsModel]], _NestedJoinItemsModel.clone_model_cls),
        _NestedItemsParamsMixin.Params,
    )


# TODO: Make MatchItemsModel Generic. Generics are currently not supported by Parametrized Models.


class _MatchItemsModel(Model[list[str]]):
    @params_dataclass
    class Params(ParamsBase):
        match_functions: tuple[Callable[[str], bool], ...] = ()
        invert_matches: bool = False
        match_all: bool = True

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
