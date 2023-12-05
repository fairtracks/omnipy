# from omnipy.modules.json.datasets import JsonDictDataset
# from omnipy.modules.json.tasks import transpose_dataset_of_dicts_to_lists
#
#
# def test_transpose_dataset_of_dicts_to_lists_1():
#     transpose = transpose_dataset_of_dicts_to_lists
#     assert (transpose.run(JsonDictDataset(dict(abc={'a': 123}, bcd={'a': 456}))).to_data() \
#             == {'a': [123, 234]})
#
#
#
#
# def test_transpose_dataset_of_dicts_to_lists_2():
#     dataset = JsonDictDataset()
#     # dataset.from_json({'input': '{"a": {"b": [1, 2, 3], "c": "abc"} }'})
#     dataset['input'] = {'a': {'b': [1, 2, 3], 'c': 'abc'}}
#
#     output = transpose_dataset_of_dicts_to_lists.apply()(dataset)
#     print(output.to_data())
#
#     # assert output['a'] == [{'_omnipy_id': 'input_0', 'b': [1, 2, 3], 'c': 'abc'}]
