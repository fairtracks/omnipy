from io import BytesIO
import tarfile
from typing import Any

import pandas as pd

from unifair.dataset.pandas import PandasDataset


def _assert_tar_file_contents(tarfile_bytes: bytes,
                              obj_type_name: str,
                              file_suffix: str,
                              exp_contents: Any):
    with tarfile.open(fileobj=BytesIO(tarfile_bytes), mode='r:gz') as tarfile_stream:
        file_contents = tarfile_stream.extractfile(f'{obj_type_name}.{file_suffix}')
        assert file_contents is not None
        assert file_contents.read().decode('utf8') == exp_contents


def _assert_pandas_dataset_equals(pandas_dataset_1: PandasDataset, pandas_dataset_2: PandasDataset):
    assert pandas_dataset_1.keys() == pandas_dataset_2.keys()
    for key in pandas_dataset_1:
        pd.testing.assert_frame_equal(pandas_dataset_1[key], pandas_dataset_2[key])
