from dataclasses import dataclass
from math import floor
from types import NoneType
from typing import Literal

from pydantic import BaseModel, Field

from omnipy.data.model import ListOfParamModel, Model, ParamModel


@dataclass
class MyFloatObject:
    int_part: int = 0
    float_part: float = 0.0
    precision: int = 4


class MyFloatObjModel(Model[MyFloatObject]):
    def to_data(self) -> float:
        return self.contents.int_part + self.contents.float_part

    def from_data(self, value: float):
        self._validate_and_set_contents(MyFloatObject(int_part=floor(value), float_part=value % 1))


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


class PydanticChildModel(BaseModel):
    id: int = Field(0, alias='@id')
    value: float = 0


class PydanticParentModel(BaseModel):
    id: int = Field(0, alias='@id')
    children: list[PydanticChildModel] = []
    children_omnipy: list[Model[PydanticChildModel]] = []


class MyPydanticModel(Model[PydanticParentModel]):
    ...


class LiteralFiveModel(Model[Literal[5]]):
    ...


class LiteralTextModel(Model[Literal['text']]):
    ...


class LiteralFiveOrTextModel(Model[Literal[5, 'text']]):
    ...
