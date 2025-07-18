from io import BytesIO
import tarfile
from typing import Any, Callable


def assert_tar_file_content(tarfile_bytes: bytes,
                            data_file_name: str,
                            file_suffix: str,
                            decode_func: Callable,
                            exp_content: Any):
    with tarfile.open(fileobj=BytesIO(tarfile_bytes), mode='r:gz') as tarfile_stream:
        file_content = tarfile_stream.extractfile(f'{data_file_name}.{file_suffix}')
        assert file_content is not None
        assert decode_func(file_content.read()) == exp_content
