# from typing import Dict, Optional, Union
#
# from omnipy.data.dataset import Dataset
# from omnipy.data.model import Model
# from omnipy.modules.json.datasets import JsonDataset, JsonDictOfAnyDataset
# from omnipy.modules.json.models import (JsonDictModel,
#                                         JsonDictOfAnyModel,
#                                         JsonListModel,
#                                         JsonModel,
#                                         JsonSubModel)
# from omnipy.modules.json.typedefs import JsonScalar
#
#
# def test_json_dataset():
#     test_data = {'a': {'123': 2312}, 'b': {'sd': 'df'}}
#     assert JsonDataset(test_data)['a'] == JsonDictModel['JsonSubModel']({'123': 2312})
#     assert Dataset[Model[JsonSubModel]](test_data)['a'] == JsonDictModel['JsonSubModel']({
#         '123': 2312
#     })
#     assert JsonDictOfAnyDataset(test_data)['a'] == 1
#     assert JsonDictOfAnyDataset(test_data)['a'] == JsonSubModel({'123': 2312})
#     assert Dataset[Model[JsonDictModel['JsonSubModel']]](
#         test_data)['a'] == JsonDictModel['JsonSubModel']({
#             '123': 2312
#         })
#     # assert Dataset[Model[Dict[str, str]]](test_data)['a'] == JsonDictModel['JsonSubModel']({
#     #     '123': 2312
#     # })
#     assert Dataset[JsonDictModel['JsonSubModel']](test_data)['a'] == JsonDictModel['JsonSubModel']({
#         '123': 2312
#     })
#     assert JsonDictOfAnyDataset(test_data)['a'] == JsonDictModel['JsonSubModel']({'123': 2312})
#     assert Dataset[Model[Dict[str, int]]](test_data)['a'] == JsonDictModel['JsonSubModel']({
#         '123': 2312
#     })
#
#
# def test_json_dataset_consistency():
#     test_data = {'a': {'123': 2312}, 'b': {'sd': 'df'}}
#     assert JsonDataset(test_data)['a'] == _JsonDictM({'123': 2312})
#     assert JsonDictDataset(test_data)['a'] == _JsonDictM({'123': 2312})
