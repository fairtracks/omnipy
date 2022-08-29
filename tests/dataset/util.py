from io import BytesIO
import tarfile
from typing import Any, Callable

import pandas as pd

from unifair.dataset.pandas import PandasDataset


def _assert_tar_file_contents(tarfile_bytes: bytes,
                              obj_type_name: str,
                              file_suffix: str,
                              decode_func: Callable,
                              exp_contents: Any):
    with tarfile.open(fileobj=BytesIO(tarfile_bytes), mode='r:gz') as tarfile_stream:
        file_contents = tarfile_stream.extractfile(f'{obj_type_name}.{file_suffix}')
        assert file_contents is not None
        assert decode_func(file_contents.read()) == exp_contents


def _assert_pandas_frame_dtypes(frame: pd.DataFrame, expected_dtypes: tuple) -> None:
    assert tuple(str(_) for _ in frame.dtypes) == expected_dtypes


def _assert_pandas_dataset_equals(pandas_dataset_1: PandasDataset,
                                  pandas_dataset_2: PandasDataset) -> None:
    assert pandas_dataset_1.keys() == pandas_dataset_2.keys()
    for key in pandas_dataset_1.keys():
        pd.testing.assert_frame_equal(pandas_dataset_1[key], pandas_dataset_2[key])