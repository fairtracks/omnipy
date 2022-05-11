import tarfile
from io import BytesIO
from typing import Any


def _assert_tar_file_contents(
    tarfile_bytes: bytes, obj_type_name: str, file_suffix: str, exp_contents: Any
):
    with tarfile.open(fileobj=BytesIO(tarfile_bytes), mode="r:gz") as tarfile_stream:
        file_contents = tarfile_stream.extractfile(f"{obj_type_name}.{file_suffix}")
        assert file_contents is not None
        assert file_contents.read().decode("utf8") == exp_contents
