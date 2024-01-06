from types import NoneType

from omnipy.data.model import ListOfParamModel, Model, ParamModel


class StringToLength(Model[str]):
    @classmethod
    def _parse_data(cls, data: str) -> int:
        return len(data)


class UpperStrModel(ParamModel[str, bool]):
    @classmethod
    def _parse_data(cls, data: str, upper: bool = False) -> str:
        return data.upper() if upper else data


class ListOfUpperStrModel(ListOfParamModel[UpperStrModel, bool]):
    ...


class DefaultStrModel(ParamModel[NoneType | str, str]):
    @classmethod
    def _parse_data(cls, data: NoneType, default: str = 'default') -> str:
        return default if data is None else data
