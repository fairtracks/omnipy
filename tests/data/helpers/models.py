from dataclasses import dataclass
from math import floor
from types import NoneType
from typing import Generic, Literal, Optional, TypeAlias

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel
from typing_extensions import TypeVar

from omnipy.data.model import ListOfParamModel, Model, ParamModel
from omnipy.data.param import bind_adjust_model_func, ParamsBase

ChildT = TypeVar('ChildT', bound=object)
ChildrenT = TypeVar("ChildrenT", bound=list)


@dataclass
class MyFloatObject:
    int_part: int = 0
    float_part: float = 0.0
    precision: int = 4


class MyFloatObjModel(Model[MyFloatObject]):
    def to_data(self) -> float:
        return self.contents.int_part + self.contents.float_part

    def from_data(self, value: float):
        self._validate_and_set_value(MyFloatObject(int_part=floor(value), float_part=value % 1))


class StringToLength(Model[str]):
    @classmethod
    def _parse_data(cls, data: str) -> int:
        return len(data)


class UppercaseModel(Model[str]):
    @classmethod
    def _parse_data(cls, data: str) -> str:
        return data.upper()


class WordSplitterModel(Model[list[str] | str]):
    @classmethod
    def _parse_data(cls, data: list[str] | str) -> list[str]:
        if isinstance(data, str):
            return data.split()
        return data


class CBA:
    class MyGenericModel(Model[Optional[ChildT]], Generic[ChildT]):
        ...


MyFwdRefModel: TypeAlias = CBA.MyGenericModel['NumberModel']
MyNestedFwdRefModel: TypeAlias = CBA.MyGenericModel['str | NumberModel']


class NumberModel(Model[int]):
    ...


MyFwdRefModel.update_forward_refs(NumberModel=NumberModel)
MyNestedFwdRefModel.update_forward_refs(NumberModel=NumberModel)


class _ParamUpperStrModel(Model[str]):
    @dataclass(kw_only=True)
    class Params(ParamsBase):
        upper: bool = False

    @classmethod
    def _parse_data(cls, data: str) -> str:
        return data.upper() if cls.Params.upper else data


class ParamUpperStrModel(_ParamUpperStrModel):
    adjust = bind_adjust_model_func(
        _ParamUpperStrModel.clone_model_cls,
        _ParamUpperStrModel.Params,
    )


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


class PydanticParentModel(GenericModel, Generic[ChildrenT]):
    id: int = Field(0, alias='@id')
    children: ChildrenT = []


class MyPydanticModel(Model[PydanticParentModel[ChildrenT]], Generic[ChildrenT]):
    ...


class LiteralFiveModel(Model[Literal[5]]):
    ...


class LiteralTextModel(Model[Literal['text']]):
    ...


class LiteralFiveOrTextModel(Model[Literal[5, 'text']]):
    ...


class MyNumberBase:
    def __init__(self, val: int = 1):
        self.val = val

    def __eq__(self, other: 'MyNumberBase') -> bool:  # type: ignore[override]
        return self.val == other.val
