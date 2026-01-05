from types import NoneType
from typing import Iterable

from typing_extensions import reveal_type

from omnipy import Dataset, JsonDictDataset, JsonDictModel, JsonNestedListsDataset, Model
from omnipy.components.json.datasets import JsonListOfListsDataset
from omnipy.components.json.models import (JsonCustomDictModel,
                                           JsonDictOfListsModel,
                                           JsonListModel,
                                           JsonListOfListsOfScalarsModel,
                                           JsonListOfNestedDictsModel,
                                           JsonListOfScalarsModel,
                                           JsonModel,
                                           JsonNestedListsModel,
                                           JsonOnlyDictsModel,
                                           JsonOnlyListsModel,
                                           JsonScalarModel)
from omnipy.shared.protocols.data import IsDataset, IsModel

d = JsonDictModel({'a': 1, 'b': 2})
d['a'] = 4

none_model = Model[None](None)
reveal_type(Model[None])
reveal_type(none_model)
reveal_type(none_model.content)

model = Model[str]('hello')
model = Model[str](123)
reveal_type(Model[str])
reveal_type(model)

model.replace('e', 'a')
model.asd()
model.append('!')

model2 = Model[tuple[int, ...]]([1, 2, 3])
reveal_type(Model[tuple[int, ...]])
reveal_type(model2)
model2.count(2)
# model2.append(2)
model2[0]
model2[1] = 5

model3 = Model[list]([1, 2, 3])
reveal_type(Model[list])
reveal_type(model3)
reveal_type(model3.content)
model3.append(2)
model3.asdf()
asd = model3[0]
reveal_type(asd)

model4 = Model[list[int]]([1, 2, 3])
reveal_type(Model[list[int]])
reveal_type(model4)
reveal_type(model4.content)
model4.append(2)
model4.asdf()
das = model4[0]
model4[1] = 5
reveal_type(das)

model5 = Model[dict]({'a': 1, 'b': 2})
reveal_type(Model[dict])
reveal_type(model5)
model5.pop('a')
model5.asdf()
sdf = model5['a']
model5['b'] = 'c'
reveal_type(sdf)

model6 = Model[dict[int, str]]({1: 'a', 2: 'b'})
reveal_type(Model[dict[int, str]])
reveal_type(model6)
model6.pop(2)
model6.asdf()
czx = model6[1]
model6['a'] = 'c'
model6[3] = 'c'
reveal_type(czx)

(1, 2, 3).count(1)


class A:
    def adf(self):
        pass


ass: IsModel = A

model_a = Model[A]()
reveal_type(model_a)
reveal_type(model_a.content)
model_a.adf()

model_model_list = Model[Model[list[int]]]([23])
reveal_type(model_model_list)
model_model_list.append(23)
mm = model_model_list[2]
reveal_type(mm)

dataset = Dataset[Model[list[int]]](a=[1, 2, 3])
reveal_type(Dataset[Model[list[int]]])
reveal_type(dataset)
reveal_type(dataset['a'])
dataset['a'].append(2)
dataset['a'].asdf()
wex = dataset['a'][0]
dataset['a'][1] = 5
reveal_type(wex)

dataset_2 = Dataset[JsonListModel](a=[1, 2, 3])
reveal_type(Dataset[JsonListModel])
reveal_type(dataset_2)
reveal_type(dataset_2['a'])
dataset_2['a'].append(2)
dataset_2['a'].asdf()
xad = dataset_2['a'][0]
dataset_2['a'][1] = 5
reveal_type(xad)

ffgh: IsDataset[Dataset[Model[list[int]]]] = Dataset[Dataset[Model[list[int]]]]()
nested_dataset = Dataset[Dataset[Model[list[int]]]](outer={'a': [1, 2, 3]})
reveal_type(Dataset[Dataset[Model[list[int]]]])
reveal_type(nested_dataset)
reveal_type(nested_dataset['outer'])
nested_dataset['inner'] = nested_dataset['outer']
reveal_type(nested_dataset['outer']['a'])
nested_dataset['outer']['a'].append(2)
nested_dataset['outer']['a'].asdf()
dqx = nested_dataset['outer']['a'][0]
nested_dataset['outer']['a'][1] = 5
reveal_type(dqx)

nested_or_dataset = Dataset[Dataset[Model[list[int]]] | Model[str]](outer={'a': [1, 2, 3]})
reveal_type(Dataset[Dataset[Model[list[int]]] | Model[str]])
reveal_type(nested_or_dataset)
reveal_type(nested_or_dataset['outer'])
nested_or_dataset['inner'] = nested_dataset['outer']
reveal_type(nested_or_dataset['outer']['a'])
nested_or_dataset['outer']['a'].append(2)
nested_or_dataset['outer']['a'].asdf()
ffs = nested_or_dataset['outer']['a'][0]
nested_or_dataset['outer']['a'][1] = 5
reveal_type(ffs)

dataset_model_model_list = Dataset[Model[Model[list[int]]]](a=[23])
reveal_type(dataset_model_model_list)
reveal_type(dataset_model_model_list['a'])
dd = dataset_model_model_list['a']
reveal_type(dd)
dd.append(45)

dds: Iterable[int] = 'asd'

json_model = JsonModel({'sd': [123, 3]})
reveal_type(json_model)
json_model['sd']

json_scalar_model = JsonScalarModel(123)
reveal_type(json_scalar_model)
json_scalar_model.real

json_list_model = JsonListModel([1, 2, 3])
reveal_type(json_list_model)
json_list_model.append(4)
json_list_model.append({'a': 5})
json_list_model.aljsh()
json_list_model[2]

json_dict_model = JsonDictModel({'asd': [1, 2, 3]})
reveal_type(json_dict_model)
json_dict_model['aaa'] = 4
json_dict_model['adaa'] = {'a': 5}
json_dict_model['sd'] = {'a': 5}
json_dict_model.aljsh()
sub = json_dict_model['asd']
reveal_type(sub)

json_dict_dataset = JsonDictDataset(a={'asd': [1, 2, 3]})
reveal_type(json_dict_dataset)
reveal_type(json_dict_dataset['a'])
json_dict_dataset['b'] = {'x': 4}
subd = json_dict_dataset['a']
reveal_type(subd)
subd['fds'] = {'y': 5}

json_list_of_scalars_model = JsonListOfScalarsModel([1, 'a', 3.0])
reveal_type(json_list_of_scalars_model)
json_list_of_scalars_model.append(3)
json_list_of_scalars_model.append(['3'])
json_list_of_scalars_model.asdf()
dsa = json_list_of_scalars_model[2]
reveal_type(dsa)

json_list_of_lists_model = JsonListOfListsOfScalarsModel([[1, 2], ['a', 'b']])
json_list_of_lists_model2 = JsonListOfListsOfScalarsModel([[1, 2], ['a', 'b']])
reveal_type(json_list_of_lists_model)
json_list_of_lists_model.append(3)
json_list_of_lists_model.append([3, 4])
json_list_of_lists_model.append([3, ['a']])
json_list_of_lists_model.append(json_list_of_lists_model2[0])
json_list_of_lists_model.asdf()
wed = json_list_of_lists_model[1]
reveal_type(wed)
reveal_type(wed[0])

json_list_of_lists_dataset = JsonListOfListsDataset(d=[[1, 2], ['a', 'b']])
reveal_type(json_list_of_lists_dataset)
reveal_type(json_list_of_lists_dataset['d'])
json_list_of_lists_dataset['e'] = [3, 4]
json_list_of_lists_dataset['d'][0].append(3)

json_dict_of_lists_model = JsonDictOfListsModel({'a': [1, 2], 'b': ['x', 'y']})
reveal_type(json_dict_of_lists_model)
json_dict_of_lists_model['c'] = [3, 4]
json_dict_of_lists_model['c'] = json_dict_of_lists_model['b']
json_dict_of_lists_model.asdf()
json_dict_of_lists_model | json_dict_of_lists_model
assd = json_dict_of_lists_model['a']
reveal_type(assd)
reveal_type(assd[0])
df = assd[0]
assert not isinstance(df, (NoneType, str, float, int, bool, dict))
reveal_type(df)
reveal_type(df[0])

json_only_lists_model_int = JsonOnlyListsModel(2)
reveal_type(json_only_lists_model_int)
json_only_lists_model_list = JsonOnlyListsModel([1, 2, [3, 'a', 4.0]])
reveal_type(json_only_lists_model_list)
json_only_lists_model_list.append(5)
json_only_lists_model_list.append([6, 7])
json_only_lists_model_list.asdf()
asd = json_only_lists_model_list[0]

json_nested_list = JsonNestedListsModel([1, [2, [3, [4]]]])
reveal_type(json_nested_list)
json_nested_list.append(5)
json_nested_list.append([6, [7]])

json_nested_dataset = JsonNestedListsDataset(a=[1, [2, [3]]], b={'x': [4, [5]]})
reveal_type(json_nested_dataset)
reveal_type(json_nested_dataset['a'])
json_nested_dataset['c'] = [6, [7]]

json_only_dicts_model = JsonOnlyDictsModel({'a': 1, 'b': {'c': 2, 'd': {'e': 3}}})
reveal_type(json_only_dicts_model)
json_only_dicts_model['f'] = 4

json_list_of_nested_dicts_model = JsonListOfNestedDictsModel([{'a': 1}, {'b': {'c': 2}}])
reveal_type(json_list_of_nested_dicts_model)
json_list_of_nested_dicts_model.append({'d': 3})
json_list_of_nested_dicts_model.append(json_list_of_nested_dicts_model[0])

json_custom_dict_model = JsonCustomDictModel[int]({'a': 3})
reveal_type(json_custom_dict_model)
json_custom_dict_model['b'] = 3
json_custom_dict_model['b'] = '5'
