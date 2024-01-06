import os

from omnipy.data.model import ListOfParamModel, Model, ParamModel


class BytesModel(ParamModel[str | bytes, str]):
    @classmethod
    def _parse_data(cls, data: str | bytes, encoding: str = 'utf-8') -> bytes:
        if isinstance(data, bytes):
            return data

        return data.encode(encoding)

    ...


class StrModel(ParamModel[bytes | str, str]):
    @classmethod
    def _parse_data(cls, data: bytes | str, encoding: str = 'utf-8') -> str:
        if isinstance(data, str):
            return data

        return data.decode(encoding)

    ...


class SplitToLinesModel(ParamModel[str | list[str], bool]):
    @classmethod
    def _parse_data(cls, data: str | list[str], strip: bool = True) -> list[str]:
        if isinstance(data, list):
            return data

        lines = data.split(os.linesep)
        return [line.strip() for line in lines] if strip else lines


class JoinLinesModel(Model[list[str] | str]):
    @classmethod
    def _parse_data(cls, data: list[str] | str) -> str:
        if isinstance(data, str):
            return data
        return os.linesep.join(data)


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


class SplitLinesToColumnsModel(ListOfParamModel[SplitToItemsModel, bool | str]):
    ...


class JoinColumnsToLinesModel(ListOfParamModel[JoinItemsModel, str]):
    ...
