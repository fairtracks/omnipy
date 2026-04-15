from types import MappingProxyType, NoneType

from typing_extensions import reveal_type

from omnipy import (Dataset,
                    JsonDictDataset,
                    JsonDictModel,
                    JsonDictOfDictsOfScalarsModel,
                    JsonNestedListsDataset,
                    Model)
from omnipy.components.json.datasets import JsonListOfListsDataset
from omnipy.components.json.models import (AnyJsonModel,
                                           AnyJsonOnlyDictsModel,
                                           AnyJsonOnlyListsModel,
                                           AnyJsonScalarModel,
                                           JsonCustomDictModel,
                                           JsonCustomListModel,
                                           JsonDictOfDictsModel,
                                           JsonDictOfListsModel,
                                           JsonDictOfListsOfDictsModel,
                                           JsonDictOfNestedListsModel,
                                           JsonListModel,
                                           JsonListOfDictsOfScalarsModel,
                                           JsonListOfListsOfScalarsModel,
                                           JsonListOfNestedDictsModel,
                                           JsonListOfScalarsModel,
                                           JsonModel,
                                           JsonNestedListsModel,
                                           JsonOnlyDictsModel,
                                           JsonOnlyListsModel,
                                           JsonScalarModel)
from omnipy.shared.protocols.builtins import IsInt
from omnipy.shared.protocols.data import IsModel

# TODO: Turn type_hints_of_models into tests with typing.assert_type (or similar)
model = Model[str]('hello')
model_int_as_str = Model[str](123)
reveal_type(Model[str])
reveal_type(model)
reveal_type(model.__add__)
model + model_int_as_str
model + ' world'
model.replace('e', 'a')
model.asd()  # pyright: ignore[reportAttributeAccessIssue]
model.append('!')  # pyright: ignore[reportAttributeAccessIssue]

model2: Model[tuple[int, ...]] = Model[tuple[int, ...]]([1, 2, 3])
reveal_type(Model[tuple[int, ...]])
reveal_type(model2)
model2 + model2
model2 + (4, 5)
model2 + [4, 5]
model2 + range(3)
model2 + (_ for _ in range(3))
model2 + (_ for _ in 'abc')  # pyright: ignore[reportOperatorIssue]
Model[tuple[str, ...]]('a') + 'bc'  # pyright: ignore[reportOperatorIssue]
model2 + ['3', 5]  # pyright: ignore[reportOperatorIssue]
model2 + Model[list[int]]([4, 5])
reveal_type(Model[list[str]]([4, 5]))
reveal_type(model2.__add__)
model2 + Model[list[str]]([4, 5])  # pyright: ignore[reportOperatorIssue]
model2 + ('asd', 5)  # pyright: ignore[reportOperatorIssue]
model2.count(2)
model2.append(2)  # pyright: ignore[reportAttributeAccessIssue]
model2[0]
model2[1] = 5  # pyright: ignore[reportIndexIssue]

# Known issue: Model[list] is not typed as Model_list.
#
# model3 = Model[list]([1, 2, 3])
# reveal_type(Model[list])
# reveal_type(model3)
# reveal_type(model3.content)
# model3.append(2)
# model3.asdf()
# asd = model3[0]
# reveal_type(asd)

model4: Model[list[int]] = Model[list[int]]([1, 2, 3])
reveal_type(Model[list[int]])
reveal_type(model4)
reveal_type(model4.content)
model4.append(2)
model4 + model4
model4 + [4, 5]
Model[list[str]](['a', 'b']) + 'cd'  # pyright: ignore[reportOperatorIssue]
model4 + range(3)
model4 + (_ for _ in range(3))
model4 + (_ for _ in 'abc')  # pyright: ignore[reportOperatorIssue]
model4 * 2
model4.asdf()  # pyright: ignore[reportAttributeAccessIssue]
reveal_type(model4[0])
model4[1] = 5
reveal_type(model4[:2])
model4[:2] = [5, 4]
model4[:2] = ('5',)  # pyright: ignore[reportCallIssue, reportArgumentType]

# Known issue: Model[dict is not typed as Model_dict.
#
# model5 = Model[dict]({'a': 1, 'b': 2})
# reveal_type(Model[dict])
# reveal_type(model5)
# model5 | model5
# model5 | {'c': 3}
# model5.pop('a')
# model5.asdf()
# sdf = model5['a']
# model5['b'] = 'c'
# reveal_type(sdf)

model6 = Model[dict[int, str]]({1: 'a', 2: 'b'})
reveal_type(Model[dict[int, str]])
reveal_type(model6)
model6 | model6
model6 | {3: 'c'}
model6 |= {3: 'c'}
model6 | {'c': 3}  # pyright: ignore[reportOperatorIssue]
model6.__or__
model6.pop(2)
model6.asdf()  # pyright: ignore[reportAttributeAccessIssue]
reveal_type(model6[1])
model6['a'] = 'c'  # pyright: ignore[reportArgumentType]
model6[3] = 'c'

model7 = Model[bytes](b'hello')
reveal_type(Model[bytes])
reveal_type(model7)
model7.replace(b'e', b'a')
model7.asd()  # pyright: ignore[reportAttributeAccessIssue]

model8: Model[tuple[int, str]] = Model[tuple[int, str]]([1, 2])
reveal_type(Model[tuple[int, str]])
reveal_type(model8)
model8 + (3, 4)  # pyright: ignore[reportOperatorIssue]
model8 * 2  # pyright: ignore[reportOperatorIssue]
model8 + ()
model8 * 1
model8.count(2)
model8.append(2)  # pyright: ignore[reportAttributeAccessIssue]
model8[0]
model8[1] = 5  # pyright: ignore[reportIndexIssue]

model9: Model[bool] = Model[bool](True)
reveal_type(Model[bool])
reveal_type(model9)
model9.asdf()  # pyright: ignore[reportAttributeAccessIssue]
and_result_model_bool: Model[bool] = model9 & Model[int](1)
and_result_model_int: IsInt = model9 & 1
or_result_int: IsInt = model9 | 1
model9 ^ '1'
model9 ^ [123]  # pyright: ignore[reportOperatorIssue]
model9.bit_length

model10: Model[float] = Model[float](-3.14)
reveal_type(Model[float])
reveal_type(model10)
model10.safd()  # pyright: ignore[reportAttributeAccessIssue]
plus_result_model_float: Model[float] = model10 + Model[float](3)
plus_result_model_float2: Model[float] = model10 + 10
pow_result_complex: complex = model10**2.3
sub_result_model_float: Model[float] = model10 - '123'
model10 - [123]  # pyright: ignore[reportOperatorIssue]
model10.real

model11: Model[int] = Model[int](-3)
reveal_type(Model[int])
reveal_type(model11)
model11.safd()  # pyright: ignore[reportAttributeAccessIssue]
plus_result_model_int: Model[int] = model11 + Model[int](3)
plus_result_model_int2: Model[int] = model11 + 10
plus_result_float: float = model11 / Model[int](2)
model11 + [123]  # pyright: ignore[reportOperatorIssue]
model11.bit_length()

model12: Model[set[int]] = Model[set[int]]({1, 2, 3})
reveal_type(Model[set[int]])
reveal_type(model12)
model12.safd()  # pyright: ignore[reportAttributeAccessIssue]
model12 & {4, 5}
and_result_Model_set_int: Model[set[int]] = model12 & Model[set[str]]({3, '4'})
and_result_Model_set_int2: Model[set[int]] = model12 & {3, '4'}
and_result_Model_set_int3: Model[set[int]] = model12 & range(3)
or_result_Model_set_int: Model[set[int]] = model12 | Model[set[int]]({3, '4'})
or_result_set_of_int_or_str: set[int | str] = \
    Model[set[str]]({'a', 'b'}) | 'cd'  # pyright: ignore[reportOperatorIssue]
union_result_Model_set_int: Model[set[str]] = Model[set[str]]({'a', 'b'}).union('cd')

# Known issue: Model[AnyClass] does not mimic AnyClass behavior.
#
# class A:
#     def adf(self):
#         pass
#
#
# model_a: IsModel[A] = Model[A]()
# reveal_type(model_a)
# reveal_type(model_a.content)
# model_a.adf()

model_model_list: IsModel[list[int]] = Model[Model[list[int]]]([23])
reveal_type(model_model_list)
model_model_list.append(23)
reveal_type(model_model_list[2])

dataset_model_list_int = Dataset[Model[list[int]]](a=[1, 2, 3])
reveal_type(Dataset[Model[list[int]]])
reveal_type(dataset_model_list_int)
reveal_type(dataset_model_list_int['a'])
dataset_model_list_int['a'].append(2)
dataset_model_list_int['a'].asdf()  # pyright: ignore[reportAttributeAccessIssue]
reveal_type(dataset_model_list_int['a'][0])
dataset_model_list_int['a'][1] = 5

dataset_model_set_int = Dataset[Model[set[int]]](a={1, 2, 3})
reveal_type(Dataset[Model[set[int]]])
reveal_type(dataset_model_set_int)
reveal_type(dataset_model_set_int['a'])
dataset_model_set_int['a'].add(4)
dataset_model_set_int['a'].asdf()  # pyright: ignore[reportAttributeAccessIssue]

dataset_json_list_model: Dataset[JsonListModel] = Dataset[JsonListModel](a=[1, 2, 3])
reveal_type(Dataset[JsonListModel])
reveal_type(dataset_json_list_model)
reveal_type(dataset_json_list_model['a'])
dataset_json_list_model_a: JsonListModel = dataset_json_list_model['a']
dataset_json_list_model_a.append(2)
dataset_json_list_model_a.asdf()  # pyright: ignore[reportAttributeAccessIssue]
reveal_type(dataset_json_list_model_a[0])
dataset_json_list_model_a[1] = 5

nested_dataset = Dataset[Dataset[Model[list[int]]]](outer={'a': [1, 2, 3]})
reveal_type(Dataset[Dataset[Model[list[int]]]])
reveal_type(nested_dataset)
reveal_type(nested_dataset['outer'])
nested_dataset['inner'] = nested_dataset['outer']
nested_dataset_outer_a = nested_dataset['outer']['a']
reveal_type(nested_dataset_outer_a)
nested_dataset_outer_a.append(2)
nested_dataset_outer_a.asdf()  # pyright: ignore[reportAttributeAccessIssue]
nested_dataset_outer_a[1] = 5

nested_or_dataset = Dataset[Dataset[Model[list[int]]] | Model[str]](outer={'a': [1, 2, 3]})
reveal_type(Dataset[Dataset[Model[list[int]]] | Model[str]])
reveal_type(nested_or_dataset)
reveal_type(nested_or_dataset['outer'])
nested_or_dataset['inner'] = nested_or_dataset['outer']
nested_or_dataset_outer_a = nested_or_dataset['outer']['a']
reveal_type(nested_or_dataset_outer_a)
nested_or_dataset_outer_a.append(2)
nested_or_dataset_outer_a.asdf()  # pyright: ignore[reportAttributeAccessIssue]
nested_or_dataset_outer_a[1] = 5

# Known issue: Model[Dataset[Model[list[int]]]] elements are not typed as Model_list.
#
# model_of_dataset_model_list_int = Model[Dataset[Model[list[int]]]](outer=[1, 2, 3])
# reveal_type(Model[Dataset[Model[list[int]]]])
# reveal_type(model_of_dataset_model_list_int)
# reveal_type(model_of_dataset_model_list_int['outer'])
# model_of_dataset_model_list_int['inner'] = nested_dataset['outer']
# model_of_dataset_model_list_int_outer = model_of_dataset_model_list_int['outer']
# reveal_type(model_of_dataset_model_list_int_outer)
# model_of_dataset_model_list_int_outer + [3]
# model_of_dataset_model_list_int_outer.append(4)

model_of_nested_dataset = Model[Dataset[Dataset[Model[list[int]]] | Model[str]]](
    outer={
        'a': [1, 2, 3]
    })
reveal_type(Model[Dataset[Dataset[Model[list[int]]] | Model[str]]])
reveal_type(model_of_nested_dataset)
reveal_type(model_of_nested_dataset['outer'])
model_of_nested_dataset['inner'] = model_of_nested_dataset['outer']
model_of_nested_dataset_outer_0 = model_of_nested_dataset['outer'][0]
reveal_type(model_of_nested_dataset_outer_0)
model_of_nested_dataset_outer_0 + [3]
model_of_nested_dataset_outer_0.asdf()  # pyright: ignore[reportAttributeAccessIssue]
reveal_type(model_of_nested_dataset_outer_0[0] + 2)

dataset_of_model_of_dataset = Dataset[Model[Dataset[Model[list[int]]]]](outer={'a': [1, 2, 3]})
reveal_type(Dataset[Model[Dataset[Model[list[int]]]]]())
reveal_type(dataset_of_model_of_dataset)
reveal_type(dataset_of_model_of_dataset['outer'])
dataset_of_model_of_dataset['inner'] = dataset_of_model_of_dataset['outer']
dataset_of_model_of_dataset_outer_a = dataset_of_model_of_dataset['outer']['a']
reveal_type(dataset_of_model_of_dataset_outer_a)

# Known issue: Dataset[Model[Model[list[int]]]] elements are not typed as
#              Model_list.
#
# dataset_model_model_list_int = Dataset[Model[Model[list[int]]]](a=[23])
# reveal_type(dataset_model_model_list_int)
# dataset_model_model_list_int_a = dataset_model_model_list_int['a']
# reveal_type(dataset_model_model_list_int_a)
# dataset_model_model_list_int_a.append(45)

json_model: AnyJsonModel = JsonModel({'sd': [123, 3]})
reveal_type(json_model)
json_model['sd']

json_model_list: AnyJsonModel = JsonModel([123, 3])
reveal_type(json_model_list)
json_model_list[3]

json_model_scalar: AnyJsonModel = JsonModel(123.3)
reveal_type(json_model_scalar)
json_model_scalar + 423

json_model_obj: AnyJsonModel = JsonModel(object())
reveal_type(json_model_obj)

json_scalar_model: AnyJsonScalarModel = JsonScalarModel(123.0)
reveal_type(json_scalar_model)
json_scalar_model.real

reveal_type(JsonModel(123.0))
json_scalar_model2: AnyJsonScalarModel = JsonScalarModel(JsonModel(123.0))
reveal_type(json_scalar_model2)
json_scalar_model2.real

json_list_model: JsonListModel = JsonListModel([1, 2, 3])
reveal_type(json_list_model)
reveal_type(json_list_model[0])
json_list_model.append(4)
json_list_model.append({'a': 5})
json_list_model + [6, 7]
json_list_model + (6, 7)
json_list_model + 13  # pyright: ignore[reportOperatorIssue]
json_list_model.aljsh()  # pyright: ignore[reportAttributeAccessIssue]
json_list_model[2]
reveal_type(json_list_model[2:3])

json_dict_model: JsonDictModel = JsonDictModel({'asd': [1, 2, 3]})
reveal_type(json_dict_model)
json_dict_model['aaa'] = 4
json_dict_model['adaa'] = {'a': 5}
json_dict_model['sd'] = {'a': 5}
json_dict_model | {'asd': [4, 5]}
json_dict_model | {'asd': (4, 5)}
json_dict_model | {'asd': 3}
json_dict_model.aljsh()  # pyright: ignore[reportAttributeAccessIssue]
reveal_type(json_dict_model['asd'])

json_dict_dataset: JsonDictDataset = JsonDictDataset(a={'asd': [1, 2, 3]})
reveal_type(json_dict_dataset)
reveal_type(json_dict_dataset['a'])
json_dict_dataset['b'] = {'x': 4}
json_dict_dataset_a: JsonDictModel = json_dict_dataset['a']
reveal_type(json_dict_dataset_a)
json_dict_dataset_a['fds'] = {'y': 5}

json_list_of_scalars_model: JsonListOfScalarsModel = JsonListOfScalarsModel([1, 'a', 3.0])
reveal_type(json_list_of_scalars_model)
json_list_of_scalars_model.append(3)
json_list_of_scalars_model.append(['3'])  # pyright: ignore[reportArgumentType]
json_list_of_scalars_model + (3, 4)
json_list_of_scalars_model.asdf()  # pyright: ignore[reportAttributeAccessIssue]
reveal_type(json_list_of_scalars_model[2])

json_list_of_lists_of_scalars_model: JsonListOfListsOfScalarsModel = \
    JsonListOfListsOfScalarsModel([[1, 2], ['a', 'b']])
json_list_of_lists_of_scalars_model2: JsonListOfListsOfScalarsModel = \
    JsonListOfListsOfScalarsModel([[1, 2], ['a', 'b']])
reveal_type(json_list_of_lists_of_scalars_model)
json_list_of_lists_of_scalars_model.append(3)  # pyright: ignore[reportArgumentType]
json_list_of_lists_of_scalars_model.append([3, 4])
json_list_of_lists_of_scalars_model.append([3, ['a']])  # pyright: ignore[reportArgumentType]
json_list_of_lists_of_scalars_model.append(range(3))
json_list_of_lists_of_scalars_model.append(_ for _ in range(3))
json_list_of_lists_of_scalars_model.append(
    _ for _ in [[1], [2]])  # pyright: ignore[reportArgumentType]
json_list_of_lists_of_scalars_model.append(json_list_of_lists_of_scalars_model2[0])
json_list_of_lists_of_scalars_model + json_list_of_lists_of_scalars_model2
reveal_type(json_list_of_lists_of_scalars_model.__add__)
json_list_of_lists_of_scalars_model + ((3, 4),)
json_list_of_lists_of_scalars_model + [(3, 4)]
json_list_of_lists_of_scalars_model + [[3, 4]]
json_list_of_lists_of_scalars_model + [3, 4]  # pyright: ignore[reportOperatorIssue]
json_list_of_lists_of_scalars_model + ((3, [4]),)  # pyright: ignore[reportOperatorIssue]
json_list_of_lists_of_scalars_model + [{3: 4}]  # pyright: ignore[reportOperatorIssue]
json_list_of_lists_of_scalars_model.asdf()  # pyright: ignore[reportAttributeAccessIssue]
json_list_of_lists_of_scalars_model_0 = json_list_of_lists_of_scalars_model[1]
reveal_type(json_list_of_lists_of_scalars_model_0)
json_list_of_lists_of_scalars_model_0 + (3, 4)
json_list_of_lists_of_scalars_model_0 + [3, ['a']]  # pyright: ignore[reportOperatorIssue]
json_list_of_lists_of_scalars_model_0.append(5)
json_list_of_lists_of_scalars_model_0.append([5, 6])  # pyright: ignore[reportArgumentType]
reveal_type(json_list_of_lists_of_scalars_model_0[0])

json_list_of_lists_dataset = JsonListOfListsDataset(d=[[1, 2], ['a', 'b']])
reveal_type(json_list_of_lists_dataset)
reveal_type(json_list_of_lists_dataset['d'])
reveal_type(json_list_of_lists_dataset['d'][0])
json_list_of_lists_dataset['e'] = [3, 4]  # wrong type, not yet checked in Dataset.__setitem__
json_list_of_lists_dataset['d'].append([True, False])
json_list_of_lists_dataset['d'].append({'c': 5})  # pyright: ignore[reportArgumentType]
json_list_of_lists_dataset['d'][0].append(3)

json_list_of_dicts_of_scalars_model: JsonListOfDictsOfScalarsModel = \
    JsonListOfDictsOfScalarsModel([{'a': 1}, {'b': [2, 3]}])
reveal_type(json_list_of_dicts_of_scalars_model)
json_list_of_dicts_of_scalars_model.append({'c': 3})
json_list_of_dicts_of_scalars_model.append({'c': [3, 4]})  # pyright: ignore[reportArgumentType]
json_list_of_dicts_of_scalars_model.append([3, 4])  # pyright: ignore[reportArgumentType]
json_list_of_dicts_of_scalars_model + [{'c': 3}]
json_list_of_dicts_of_scalars_model + [[('c', 3)]]
json_list_of_dicts_of_scalars_model + [{'d': [3, 4]}]  # pyright: ignore[reportOperatorIssue]
json_list_of_dicts_of_scalars_model_0 = json_list_of_dicts_of_scalars_model[0]
reveal_type(json_list_of_dicts_of_scalars_model_0)
json_list_of_dicts_of_scalars_model_0 | {'x': 4}
json_list_of_dicts_of_scalars_model_0 | [('x', 4)]
json_list_of_dicts_of_scalars_model_0 | {'x': [3, 4]}  # pyright: ignore[reportOperatorIssue]
json_list_of_dicts_of_scalars_model_0.update({'y': '5'})
json_list_of_dicts_of_scalars_model_0.update(
    {'y': [5, 6]})  # pyright: ignore[reportCallIssue, reportArgumentType]

json_dict_of_lists_model: JsonDictOfListsModel = \
    JsonDictOfListsModel({'a': [1, 2], 'b': ['x', 'y']})
reveal_type(json_dict_of_lists_model)
json_dict_of_lists_model['c'] = {'a': 5}  # pyright: ignore[reportArgumentType]
json_dict_of_lists_model['c'] = [3, 4]
json_dict_of_lists_model['c'] = json_dict_of_lists_model['b']
json_dict_of_lists_model.asdf()  # pyright: ignore[reportAttributeAccessIssue]
json_dict_of_lists_model | json_dict_of_lists_model
or_result_json_dict_of_lists_model: JsonDictOfListsModel = json_dict_of_lists_model | {'d': [5, 6]}
or_result_json_dict_of_lists_model2: JsonDictOfListsModel = json_dict_of_lists_model | {
    'd': range(3)
}
or_result_json_dict_of_lists_model3: JsonDictOfListsModel = \
    json_dict_of_lists_model | {'d': (_ for _ in range(3))}
or_result_json_dict_of_lists_model4: JsonDictOfListsModel = \
    json_dict_of_lists_model | {'d': 'abc'}  # pyright: ignore[reportOperatorIssue]
json_dict_of_lists_model | {'d': 4}  # pyright: ignore[reportOperatorIssue]
json_dict_of_lists_model_a = json_dict_of_lists_model['a']
reveal_type(json_dict_of_lists_model_a)
reveal_type(json_dict_of_lists_model_a[0])
json_dict_of_lists_model_a_0 = json_dict_of_lists_model_a[0]
assert not isinstance(json_dict_of_lists_model_a_0, (NoneType, str, float, int, bool, dict))
reveal_type(json_dict_of_lists_model_a_0)
reveal_type(json_dict_of_lists_model_a_0[0])  # pyright: ignore[reportArgumentType]

json_dict_of_dicts_model: JsonDictOfDictsModel = \
    JsonDictOfDictsModel({'a': {'x': 1}, 'b': {'y': 2}})
reveal_type(json_dict_of_dicts_model)
json_dict_of_dicts_model['c'] = [3, 4]  # pyright: ignore[reportArgumentType]
json_dict_of_dicts_model['c'] = {'z': 3}
json_dict_of_dicts_model['c'] = json_dict_of_dicts_model['a']
json_dict_of_dicts_model.asdf()  # pyright: ignore[reportAttributeAccessIssue]
json_dict_of_dicts_model | json_dict_of_dicts_model
json_dict_of_dicts_model | {'d': MappingProxyType({'w': 4})}
json_dict_of_dicts_model | {'d': 4}  # pyright: ignore[reportOperatorIssue]
json_dict_of_dicts_model_a = json_dict_of_dicts_model['a']
reveal_type(json_dict_of_dicts_model_a)
json_dict_of_dicts_model_a | {'z': 3}
reveal_type(json_dict_of_dicts_model_a['x'])

json_dict_of_dicts_of_scalars_model: JsonDictOfDictsOfScalarsModel = \
    JsonDictOfDictsOfScalarsModel({'a': {'x': 1}, 'b': {'y': '2'}})
reveal_type(json_dict_of_dicts_of_scalars_model)
json_dict_of_dicts_of_scalars_model['c'] = [4, 5]  # pyright: ignore[reportArgumentType]
json_dict_of_dicts_of_scalars_model['c'] = {'z': 3}
json_dict_of_dicts_of_scalars_model['c'] = json_dict_of_dicts_of_scalars_model['a']
json_dict_of_dicts_of_scalars_model.asdf()  # pyright: ignore[reportAttributeAccessIssue]
json_dict_of_dicts_of_scalars_model | json_dict_of_dicts_of_scalars_model
json_dict_of_dicts_of_scalars_model | {'d': MappingProxyType({'w': 4})}
json_dict_of_dicts_of_scalars_model | {'e': [('z', 3)]}
json_dict_of_dicts_of_scalars_model | {'d': {'w': [4]}}  # pyright: ignore[reportOperatorIssue]
json_dict_of_dicts_of_scalars_model_a = json_dict_of_dicts_of_scalars_model['a']
reveal_type(json_dict_of_dicts_of_scalars_model_a)
json_dict_of_dicts_of_scalars_model_a | {'z': 3}
json_dict_of_dicts_of_scalars_model_a | {'z': {'d': 3}}  # pyright: ignore[reportOperatorIssue]
reveal_type(json_dict_of_dicts_of_scalars_model_a['x'])

json_only_lists_model_int: AnyJsonOnlyListsModel = JsonOnlyListsModel(2)
reveal_type(json_only_lists_model_int)
json_only_lists_model_list = JsonOnlyListsModel(Model[list[object]]([1, 2, [3, 'a', 4.0]]))
reveal_type(json_only_lists_model_list)
json_only_lists_model_list.append(5)
json_only_lists_model_list.append([6, 7])
json_only_lists_model_list + [8, 9]
json_only_lists_model_list + [8, {'x': 9}]  # pyright: ignore[reportOperatorIssue]
json_only_lists_model_list.asdf()  # pyright: ignore[reportAttributeAccessIssue]
reveal_type(json_only_lists_model_list[0])
json_only_lists_model_obj = JsonOnlyListsModel(object())
reveal_type(json_only_lists_model_obj)

json_nested_list: JsonNestedListsModel = JsonNestedListsModel([1, [2, [3, [4]]]])
reveal_type(json_nested_list)
json_nested_list.append(5)
json_nested_list.append([6, [7]])
json_nested_list.append([6, {'a': 7}])  # pyright: ignore[reportArgumentType]
json_nested_list + [8, [9]]
json_nested_list + [8, {'a': 9}]  # pyright: ignore[reportOperatorIssue]
reveal_type(json_nested_list[0])

json_nested_dataset = JsonNestedListsDataset(a=[1, [2, [3]]], b={'x': [4, [5]]})
reveal_type(json_nested_dataset)
reveal_type(json_nested_dataset['a'])
json_nested_dataset['c'] = [6, [7]]

json_only_dicts_model: AnyJsonOnlyDictsModel = \
    JsonOnlyDictsModel(Model[dict[str, int]]({'a': 1, 'b': {'c': 2, 'd': {'e': 3}}}))
reveal_type(json_only_dicts_model)
json_only_dicts_model['f'] = 4
json_only_dicts_model['f'] = {'h': 5}
json_only_dicts_model['f'] = [3, 4]  # pyright: ignore[reportArgumentType]
json_only_dicts_model.update({'g': {'h': 5}})
json_only_dicts_model.update({'g': [3, 4]})  # pyright: ignore[reportCallIssue, reportArgumentType]
reveal_type(json_only_dicts_model['c'])
json_only_dicts_model_obj = JsonOnlyDictsModel(object())
reveal_type(json_only_dicts_model_obj)

json_list_of_nested_dicts_model: JsonListOfNestedDictsModel = \
    JsonListOfNestedDictsModel([{'a': 1}, {'b': {'c': 2}}])
reveal_type(json_list_of_nested_dicts_model)
json_list_of_nested_dicts_model.append(3)  # pyright: ignore[reportArgumentType]
json_list_of_nested_dicts_model.append({'d': {'e': 4}})
json_list_of_nested_dicts_model.append({'d': {'e': [4, 5]}})  # pyright: ignore[reportArgumentType]
json_list_of_nested_dicts_model.append(json_list_of_nested_dicts_model[0])
json_list_of_nested_dicts_model + json_list_of_nested_dicts_model
json_list_of_nested_dicts_model + [3]  # pyright: ignore[reportOperatorIssue]
json_list_of_nested_dicts_model + [{'d': 'a'}]
json_list_of_nested_dicts_model + [{'d': {'e': [4, 5]}}]  # pyright: ignore[reportOperatorIssue]
json_list_of_nested_dicts_model_0 = json_list_of_nested_dicts_model[0]
reveal_type(json_list_of_nested_dicts_model_0)
json_list_of_nested_dicts_model_0 | {'x': 4}
json_list_of_nested_dicts_model_0 | {'x': {'y': 5}}
json_list_of_nested_dicts_model_0 | {'x': {'y': [3, 4]}}  # pyright: ignore[reportOperatorIssue]
reveal_type(json_list_of_nested_dicts_model[0]['a'])

json_dict_of_nested_lists_model: JsonDictOfNestedListsModel = \
    JsonDictOfNestedListsModel({'a': [1, [2, 3]], 'b': {'c': [4, 5]}})
reveal_type(json_dict_of_nested_lists_model)
json_dict_of_nested_lists_model['d'] = [6, [7, 8]]
json_dict_of_nested_lists_model['d'] = {'e': [9, 10]}  # pyright: ignore[reportArgumentType]
json_dict_of_nested_lists_model['d'] = json_dict_of_nested_lists_model['a']
json_dict_of_nested_lists_model | json_dict_of_nested_lists_model
json_dict_of_nested_lists_model | {'f': [11, [12, 13]]}
json_dict_of_nested_lists_model | {'f': {'g': [13, 14]}}  # pyright: ignore[reportOperatorIssue]
json_dict_of_nested_lists_model_a = json_dict_of_nested_lists_model['a']
reveal_type(json_dict_of_nested_lists_model_a)
json_dict_of_nested_lists_model_a.append(4)
json_dict_of_nested_lists_model_a.append({'g': 5})  # pyright: ignore[reportArgumentType]
json_dict_of_nested_lists_model_a + [5, 6]
json_dict_of_nested_lists_model_a + [5, {'g': 6}]  # pyright: ignore[reportOperatorIssue]
reveal_type(json_dict_of_nested_lists_model_a[0])

json_custom_dict_model: JsonCustomDictModel[int] = JsonCustomDictModel[int]({'a': 3})
reveal_type(json_custom_dict_model)
json_custom_dict_model['b'] = 3
json_custom_dict_model['b'] = '5'  # pyright: ignore[reportArgumentType]
json_custom_dict_model | {'c': 4}
json_custom_dict_model | {'c': '4'}  # pyright: ignore[reportOperatorIssue]
reveal_type(json_custom_dict_model['a'])

json_custom_list_model: JsonCustomListModel[list[int]] = \
    JsonCustomListModel[list[int]]([[3, 4], [5, 6]])
reveal_type(json_custom_list_model)
json_custom_list_model[1] = '5'  # pyright: ignore[reportArgumentType, reportCallIssue]
json_custom_list_model[1] = [5]
json_custom_list_model.append([6, 7])
json_custom_list_model.append(8)  # pyright: ignore[reportArgumentType]
reveal_type(json_custom_list_model[0])

json_dict_of_lists_of_dicts_model: JsonDictOfListsOfDictsModel = \
    JsonDictOfListsOfDictsModel({'a': [{'x': 1}, {'y': 2}]})
reveal_type(json_dict_of_lists_of_dicts_model)
json_dict_of_lists_of_dicts_model['b'] = [{'z': 3}]
json_dict_of_lists_of_dicts_model['b'] = {'z': 3}  # pyright: ignore[reportArgumentType]
json_dict_of_lists_of_dicts_model.update({'b': [{'z': 3}]})
json_dict_of_lists_of_dicts_model.update({  # pyright: ignore[reportCallIssue]
    'b': {  # pyright: ignore[reportArgumentType]
        'z': 3
    }
})
json_dict_of_lists_of_dicts_model | {'b': [{'z': 3}]}
json_dict_of_lists_of_dicts_model | {'b': {'z': 3}}  # pyright: ignore[reportOperatorIssue]
json_dict_of_lists_of_dicts_model_a = json_dict_of_lists_of_dicts_model['a']
reveal_type(json_dict_of_lists_of_dicts_model_a)
json_dict_of_lists_of_dicts_model_a.append({'w': 4})
json_dict_of_lists_of_dicts_model_a.append([{'w': 4}])  # pyright: ignore[reportArgumentType]
json_dict_of_lists_of_dicts_model_a_0 = json_dict_of_lists_of_dicts_model_a[0]
reveal_type(json_dict_of_lists_of_dicts_model_a_0)
json_dict_of_lists_of_dicts_model_a_0 | {'v': 5}
reveal_type(json_dict_of_lists_of_dicts_model_a_0['x'])
