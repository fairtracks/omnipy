import subprocess
import sys


def test_pandas_import_is_deferred_until_pandas_export_access() -> None:
    code = """
import sys
from typing import ForwardRef
import omnipy as om

assert 'pandas' not in sys.modules
assert 'numpy' not in sys.modules
assert 'PandasModel' in dir(om)
assert not isinstance(om.PandasModel.outer_type(), ForwardRef)
from omnipy.components.pandas.models import PandasModel
assert om.PandasModel is PandasModel
from omnipy.components.pandas import datasets, models, tasks
for module, names in (
    (datasets, ('PandasDataset',)),
    (models, ('PandasModel',)),
    (tasks, ('cartesian_product', 'concat_dataframes_across_datasets',
             'convert_dataset_csv_to_pandas', 'convert_dataset_list_of_dicts_to_pandas',
             'convert_dataset_pandas_to_csv', 'extract_columns_as_files', 'join_tables')),
):
    for name in names:
        assert getattr(om, name) is getattr(module, name)
dataset = om.PandasDataset({'table': [{'value': 1}]})
assert dataset['table'].to_data() == {'value': [1]}
assert 'pandas' in sys.modules
"""
    subprocess.run([sys.executable, '-c', code], check=True)
