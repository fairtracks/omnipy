import pandas

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.modules.json.datasets import JsonDataset
from omnipy.modules.json.models import JsonModel
from omnipy.modules.pandas.models import PandasDataset

pandas_dataset = PandasDataset()
pandas_dataset.from_data({
    'pandas_person':
        pandas.DataFrame((('John', 'Doe', 46), ('Jane', 'Doe', 42), ('Mr', 'Miyagi', 82)),
                         columns=('firstname', 'lastname', 'age')),
    'pandas_fruits':
        pandas.DataFrame((('apple', 'sweet'), ('orange', 'sweet and sour'), ('lemon', 'sour')),
                         columns=('fruit', 'taste'))
})

json_table_dataset = Dataset[JsonModel]()
json_table_dataset['json_table_a'] = [
    dict(firstname='John', lastname='Doe', age=46),
    dict(firstname='Jane', lastname='Doe', age=42),
    dict(firstname='Mr.', lastname='Miyagi', age=82)
]
json_table_dataset['json_table_b'] = [
    dict(fruit='apple', taste='sweet'),
    dict(fruit='orange', taste='sweet and sour'),
    dict(fruit='lemon', taste='sour')
]

json_nested_table_dataset = JsonDataset()
json_nested_table_dataset['json_nested_table_a'] = [
    dict(name=dict(firstname='John', lastname='Doe'), age=46),
    dict(name=dict(firstname='Jane', lastname='Doe'), age=42),
    dict(name=dict(firstname='Mr.', lastname='Miyagi'), age=82)
]
json_nested_table_dataset['json_nested_table_b'] = [
    dict(name=dict(fruit='apple'), taste='sweet'),
    dict(name=dict(fruit='orange'), taste='sweet and sour'),
    dict(name=dict(fruit='lemon'), taste='sour')
]

json_table_as_str_dataset = Dataset[Model[str]]()
json_table_as_str_dataset['json_table_a'] = """
[
    {"firstname": "John", "lastname": "Doe", "age": 46},
    {"firstname": "Jane", "lastname": "Doe", "age": 42},
    {"firstname": "Mr.", "lastname": "Miyagi", "age": 82}
]"""[1:]
json_table_as_str_dataset['json_table_b'] = """
[
    {"fruit": "apple", "taste": "sweet"},
    {"fruit": "orange", "taste": "sweet and sour"},
    {"fruit": "lemon", "taste": "sour"}
]"""[1:]

json_dataset = Dataset[JsonModel]()
json_dataset['json_python_a'] = {'one': ['contents', 1, True], 'two': None}
json_dataset['json_python_b'] = [1, 4, 9, {'options': {'verbose': False}}]

json_str_dataset = Dataset[Model[str]]()
json_str_dataset['json_str_a'] = '{"one": ["contents", 1, true], "two": null}'
json_str_dataset['json_str_b'] = '[1, 4, 9, {"options": {"verbose": false}}]'

csv_dataset = Dataset[Model[str]]()
csv_dataset['csv_person'] = 'firstname,lastname,age\nJohn,Doe,46\nJane,Doe,42\nMr,Miyagi,82\n'
csv_dataset['csv_fruits'] = 'fruit,taste\napple,sweet\norange,sweet and sour\nlemon,sour\n'

str_dataset = Dataset[Model[str]]()
str_dataset['str_a'] = '1, 2, 4, 6 -> aa\n6, 3, 4, 2 -> ab\n'
str_dataset['str_b'] = '3, 5, 6, 3 -> ba\n2, 5, 6, 3 -> bb\n'

python_dataset = Dataset[Model[object]]()
python_dataset['python_a'] = [{'a': 1, 'b': [2, 3, 4], 'c': {'yes': True, 'no': False}}]
python_dataset['python_b'] = lambda x: x + 1
