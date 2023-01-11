from omnipy.data.dataset import Dataset
from omnipy.data.model import Model


def json_func() -> Dataset[Model[str]]:
    dataset = Dataset[Model[str]]()
    dataset['a'] = '{"one": ["contents", 1, true], "two": none}'
    dataset['b'] = '[1, 4, 9, {"options": {"verbose": false} }]'
    return dataset
