from omnipy.modules.json.datasets import JsonDictOfAnyDataset
from omnipy.modules.json.tasks import transpose_dataset_of_dicts_to_lists


def test_transpose_dataset_of_dicts_to_lists():
    transpose = transpose_dataset_of_dicts_to_lists
    assert transpose.run(JsonDictOfAnyDataset(dict(abc={'a': 123}, bcd={'a': 456}))).to_data() == {
        'a': [123, 234]
    }
