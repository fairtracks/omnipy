import pandas as pd

from unifair.modules.json.models import JsonDataset
from unifair.modules.pandas.models import PandasDataset


def convert_json_to_pandas(json_data: JsonDataset) -> PandasDataset:
    pandas_data = PandasDataset()
    for obj_key in json_data.keys():
        pandas_data[obj_key] = pd.json_normalize(json_data[obj_key])
    return pandas_data
