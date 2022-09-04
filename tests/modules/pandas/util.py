import pandas as pd

from unifair.modules.pandas.models import PandasDataset


def assert_pandas_frame_dtypes(frame: pd.DataFrame, expected_dtypes: tuple) -> None:
    assert tuple(str(_) for _ in frame.dtypes) == expected_dtypes


def assert_pandas_dataset_equals(pandas_dataset_1: PandasDataset,
                                 pandas_dataset_2: PandasDataset) -> None:
    assert pandas_dataset_1.keys() == pandas_dataset_2.keys()
    for key in pandas_dataset_1.keys():
        pd.testing.assert_frame_equal(pandas_dataset_1[key], pandas_dataset_2[key])
