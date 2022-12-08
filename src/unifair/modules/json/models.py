# from __future__ import annotations
from typing import Dict, ForwardRef, Generic, List, TypeVar, Union

from unifair.data.dataset import Dataset
from unifair.data.model import Model

JsonType = ForwardRef('JsonType')

JsonListValT = TypeVar('JsonListValT')
JsonDictValT = TypeVar('JsonDictValT')

# class JsonList(GenericModel, Generic[JsonListValT]):
#     __root__: List[JsonListValT] = []
#
#     @property
#     def contents(self):
#         return self.__root__
#
#     def to_data(self) -> Any:
#         return self.dict()[ROOT_KEY]
#
#
# class JsonDict(GenericModel, Generic[JsonDictValT]):
#     __root__: Dict[str, JsonDictValT] = {}
#
#     @property
#     def contents(self):
#         return self.__root__
#
#     def to_data(self) -> Any:
#         return self.dict()[ROOT_KEY]


class JsonList(Model[List[Union[None, JsonListValT]]], Generic[JsonListValT]):
    ...


class JsonDict(Model[Dict[str, Union[None, JsonDictValT]]], Generic[JsonDictValT]):
    ...


class JsonScalarType(Model[Union[None, int, float, str, bool]]):
    ...


JsonType = Union[None, JsonScalarType, JsonList['JsonType'], JsonDict['JsonType']]

JsonList['JsonType'].update_forward_refs(JsonType=JsonType)
JsonDict['JsonType'].update_forward_refs(JsonType=JsonType)


class JsonModel(Model[JsonType]):
    ...


class JsonDictOfAnyModel(Model[JsonDict[JsonType]]):
    ...


class JsonDictOfDictOfAnyModel(Model[JsonDict[JsonDict[JsonType]]]):
    ...


class JsonListOfAnyModel(Model[Union[JsonList[JsonType]]]):
    ...


class JsonListOfDictOfAnyModel(Model[JsonList[JsonDict[JsonType]]]):
    ...


class JsonDictOfListOfDictOfAnyModel(Model[JsonDict[JsonListOfDictOfAnyModel]]):
    ...


# @classmethod
# def _parse_data(cls, data: Union[JsonList, JsonDict]) -> Union[JsonList, JsonDict]:
#     # data = cls._data_not_empty_object(data)
#     return data

# @classmethod
# def _data_not_empty_object(cls, data: List):
#     for obj in data:
#         assert len(obj) > 0
#     return data


class JsonDataset(Dataset[JsonModel]):
    ...


JsonNoListType = Union[JsonScalarType, JsonDict['JsonType']]

JsonList['JsonNoListType'].update_forward_refs(JsonNoListType=JsonNoListType)
JsonDict['JsonNoListType'].update_forward_refs(JsonNoListType=JsonNoListType)


class JsonListOfDictsModel(Model[JsonList[JsonDict[JsonScalarType]]]):
    ...


class JsonNestedDictsModel(Model[JsonDict[JsonNoListType]]):
    ...


class JsonListOfNestedDictsModel(Model[JsonList[JsonNestedDictsModel]]):
    ...
