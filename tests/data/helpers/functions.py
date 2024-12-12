from io import BytesIO
import tarfile
from typing import Any, Callable


def assert_tar_file_contents(tarfile_bytes: bytes,
                             data_file_name: str,
                             file_suffix: str,
                             decode_func: Callable,
                             exp_contents: Any):
    with tarfile.open(fileobj=BytesIO(tarfile_bytes), mode='r:gz') as tarfile_stream:
        file_contents = tarfile_stream.extractfile(f'{data_file_name}.{file_suffix}')
        assert file_contents is not None
        assert decode_func(file_contents.read()) == exp_contents


def assert_directory_in_tar_file(tarfile_bytes: bytes, dir_file_name: str):
    with tarfile.open(fileobj=BytesIO(tarfile_bytes), mode='r:gz') as tarfile_stream:
        tar_info = tarfile_stream.getmember(dir_file_name)
        assert tar_info.isdir()
