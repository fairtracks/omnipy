import os
from typing import cast

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


class _SplitToLinesModel(Model[list[str] | str]):
    @params_dataclass
    class Params(ParamsBase):
        strip: bool = True

    @classmethod
    def _parse_data(cls, data: list[str] | str) -> list[str]:
        if isinstance(data, list):
            return data

        if cls.Params.strip:
            data = data.strip()
        lines = data.split(os.linesep)
        return [line.strip() for line in lines] if cls.Params.strip else lines


class SplitToLinesModel(_SplitToLinesModel):
    adjust = bind_adjust_model_func(
        _SplitToLinesModel.clone_model_cls,
        _SplitToLinesModel.Params,
    )


class JoinLinesModel(Model[str | list[str]]):
    @classmethod
    def _parse_data(cls, data: str | list[str]) -> str:
        if isinstance(data, str):
            return data
        return os.linesep.join(data)


class _SplitToItemsMixin:
    @params_dataclass
    class Params(ParamsBase):
        strip: bool = True
        strip_chars: str | None = None
        delimiter: str = '\t'

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


class _SplitLinesToColumnsModel(
        Model[list[list[str]] | list[str] | list[StrModel]],
        _SplitToItemsMixin,
):
    @classmethod
    def _parse_data(cls, data: list[list[str]] | list[str] | list[StrModel]) -> list[list[str]]:
        if isinstance(data, list) and (len(data) == 0 or isinstance(data[0], list)):
            return cast(list[list[str]], data)

        return [cls._split_line(cast(str, line)) for line in data]


class SplitLinesToColumnsModel(_SplitLinesToColumnsModel):
    adjust = bind_adjust_model_func(
        _SplitLinesToColumnsModel.clone_model_cls,
        _SplitLinesToColumnsModel.Params,
    )


class _JoinItemsMixin:
    @params_dataclass
    class Params(ParamsBase):
        delimiter: str = '\t'

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


class _JoinColumnsToLinesModel(
        Model[list[str] | list[list[str]]],
        _JoinItemsMixin,
):
    @classmethod
    def _parse_data(cls, data: list[str] | list[list[str]]) -> list[str]:
        if isinstance(data, list) and (len(data) == 0 or not isinstance(data[0], list)):
            return cast(list[str], data)

        return [cls._join_items(cast(list[str], cols)) for cols in data]


class JoinColumnsToLinesModel(_JoinColumnsToLinesModel):
    adjust = bind_adjust_model_func(
        _JoinColumnsToLinesModel.clone_model_cls,
        _JoinColumnsToLinesModel.Params,
    )
