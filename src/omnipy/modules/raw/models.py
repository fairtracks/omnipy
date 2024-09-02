from dataclasses import dataclass
import os
from typing import cast

from omnipy.data.model import ListOfParamModel, Model, ParamModel
from omnipy.data.param import bind_adjust_model_func, ParamsBase


class _EncodingParamsMixin:
    @dataclass(kw_only=True)
    class Params(ParamsBase):
        encoding: str = 'utf-8'


class _BytesModel(Model[str | bytes], _EncodingParamsMixin):
    @classmethod
    def _parse_data(cls, data: str | bytes) -> bytes:
        if isinstance(data, bytes):
            return data

        return data.encode(cls.Params.encoding)


class BytesModel(_BytesModel):
    adjust = bind_adjust_model_func(
        _BytesModel.clone_model_cls,
        _EncodingParamsMixin.Params,
    )


class _StrModel(Model[bytes | str], _EncodingParamsMixin):
    Params = _EncodingParamsMixin.Params

    @classmethod
    def _parse_data(cls, data: bytes | str) -> str:
        if isinstance(data, str):
            return data

        return data.decode(cls.Params.encoding)

    ...


class StrModel(_StrModel):
    adjust = bind_adjust_model_func(
        _StrModel.clone_model_cls,
        _EncodingParamsMixin.Params,
    )


class SplitToLinesModel(ParamModel[str | list[str], bool]):
    @classmethod
    def _parse_data(cls, data: str | list[str], strip: bool = True) -> list[str]:
        if isinstance(data, list):
            return data

        if strip:
            data = data.strip()
        lines = data.split(os.linesep)
        return [line.strip() for line in lines] if strip else lines


class JoinLinesModel(Model[list[str] | str]):
    @classmethod
    def _parse_data(cls, data: list[str] | str) -> str:
        if isinstance(data, str):
            return data
        return os.linesep.join(data)


class SplitToItemsMixin:
    @dataclass(kw_only=True)
    class Params(ParamsBase):
        strip: bool = True
        strip_chars: str | None = None
        delimiter: str = '\t'

    @classmethod
    def _split_line(cls, data: str) -> list[str]:
        if cls.Params.strip:
            data = data.strip(cls.Params.strip_chars)

        items = data.split(cls.Params.delimiter)
        return [item.strip(cls.Params.strip_chars) for item in items] if cls.Params.strip else items


class _SplitToItemsModelNew(
        Model[list[str] | str],
        SplitToItemsMixin,
):
    @classmethod
    def _parse_data(cls, data: list[str] | str) -> list[str]:
        if isinstance(data, list):
            return data

        return cls._split_line(data)


class SplitToItemsModelNew(_SplitToItemsModelNew):
    adjust = bind_adjust_model_func(
        _SplitToItemsModelNew.clone_model_cls,
        _SplitToItemsModelNew.Params,
    )


class SplitToItemsModel(ParamModel[str | list[str], bool | str]):
    @classmethod
    def _parse_data(cls,
                    data: str | list[str],
                    strip: bool = True,
                    delimiter: str = '\t') -> list[str]:
        if isinstance(data, list):
            return data

        items = data.split(delimiter)
        return [item.strip() for item in items] if strip else items


class JoinItemsModel(ParamModel[list[str] | str, str]):
    @classmethod
    def _parse_data(cls, data: list[str] | str, delimiter: str = '\t') -> str:
        if isinstance(data, str):
            return data

        return delimiter.join(data)


class _SplitLinesToColumnsModelNew(
        Model[list[list[str]] | list[str] | list[StrModel]],
        SplitToItemsMixin,
):
    @classmethod
    def _parse_data(cls, data: list[list[str]] | list[str] | list[StrModel]) -> list[list[str]]:
        if isinstance(data, list) and (len(data) == 0 or isinstance(data[0], list)):
            return cast(list[list[str]], data)

        return [cls._split_line(cast(str, line)) for line in data]


class SplitLinesToColumnsModelNew(_SplitLinesToColumnsModelNew):
    adjust = bind_adjust_model_func(
        _SplitLinesToColumnsModelNew.clone_model_cls,
        _SplitLinesToColumnsModelNew.Params,
    )


class SplitLinesToColumnsModel(ListOfParamModel[SplitToItemsModel, bool | str]):
    ...


class JoinColumnsToLinesModel(ListOfParamModel[JoinItemsModel, str]):
    ...
