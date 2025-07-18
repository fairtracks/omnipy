from typing import TYPE_CHECKING

from omnipy.components.pandas.datasets import PandasDataset

if TYPE_CHECKING:
    from omnipy.components.pandas.lazy_import import pd


def assert_pandas_frame_dtypes(frame: 'pd.DataFrame', expected_dtypes: tuple) -> None:
    real_dtypes = tuple(str(_) for _ in frame.dtypes)
    assert real_dtypes == expected_dtypes, f'{real_dtypes} != {expected_dtypes}'


def assert_pandas_dataset_equals(pandas_dataset_1: PandasDataset,
                                 pandas_dataset_2: PandasDataset) -> None:
    from omnipy.components.pandas.lazy_import import pd

    assert pandas_dataset_1.keys() == pandas_dataset_2.keys()
    for key in pandas_dataset_1.keys():
        pd.testing.assert_frame_equal(pandas_dataset_1[key].content, pandas_dataset_2[key].content)
