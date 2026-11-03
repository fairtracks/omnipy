"""Saving entry point for Datasets."""

import os
import tarfile
from typing import cast


class SaveMixin:
    """Save contents as a gzipped tar archive, using the registered serializers."""

    def save(self, path: str | os.PathLike[str]) -> None:
        """Save a ``.tar.gz`` archive and extract a directory copy beside it.

        Args:
            path: Destination path with or without the ``.tar.gz`` suffix.
        """
        from omnipy.data.dataset import Dataset

        dataset = cast(Dataset, self)
        serializer_registry = dataset._get_serializer_registry()
        parsed_dataset, serializer = serializer_registry.auto_detect_tar_file_serializer(dataset)

        if serializer is None:
            print(
                f'Unable to find a serializer for dataset with data type "{type(self)}". '
                f'Will abort saving...'
            )
        else:
            path = os.fspath(path)
            out_tar_gz_path = path if path.endswith('.tar.gz') else f'{path}.tar.gz'

            print(f'Writing dataset as a gzipped tarpack to "{os.path.abspath(out_tar_gz_path)}"')
            with open(out_tar_gz_path, 'wb') as out_tar_gz_file:
                out_tar_gz_file.write(serializer.serialize(parsed_dataset))

            directory = os.path.abspath(out_tar_gz_path[:-7])
            os.makedirs(directory, exist_ok=True)
            print(f'Extracting content to directory "{directory}"')
            with tarfile.open(out_tar_gz_path) as tar:
                tar.extractall(path=directory)
