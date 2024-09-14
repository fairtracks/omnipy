from dataclasses import dataclass
from math import floor
from typing import Generic, Literal, Optional, TypeAlias

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel
from typing_extensions import TypeVar

from omnipy.data.model import Model
from omnipy.data.param import bind_adjust_model_func, ParamsBase

from .classes import MyFloatObject

ChildT = TypeVar('ChildT', bound=object)
ChildrenT = TypeVar("ChildrenT", bound=list)


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


class _DefaultStrModel(Model[None | str]):
    @dataclass(kw_only=True)
    class Params(ParamsBase):
        default: str = 'default'

    @classmethod
    def _parse_data(cls, data: None) -> str:
        return cls.Params.default if data is None else data


class DefaultStrModel(_DefaultStrModel):
    adjust = bind_adjust_model_func(
        _DefaultStrModel.clone_model_cls,
        _DefaultStrModel.Params,
    )


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
