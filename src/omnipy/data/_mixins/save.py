"""Share archive saving between Models and Datasets."""

import os
import tarfile
from typing import cast


class SaveMixin:
    """Reuse Dataset serializers for a collection or one complete Model value."""

    def save(self, path: str | os.PathLike[str]) -> None:
        """Save a ``.tar.gz`` archive and extract a directory copy beside it.

        Dataset entries become separate files. A Model's complete contents are
        saved as one entry named ``data``, including when its contents are a
        mapping or Dataset. The serializer supplies the member's file suffix.

        Args:
            path: Destination path with or without the ``.tar.gz`` suffix.
        """
        from omnipy.data.dataset import Dataset, is_dataset_instance
        from omnipy.data.model import Model

        if is_dataset_instance(self):
            dataset = self
        else:
            model = cast(Model, self)
            model_cls = type(model)
            dataset = Dataset[model_cls]({'data': model})  # type: ignore[valid-type]

        serializer_registry = dataset._get_serializer_registry()
        parsed_dataset, serializer = serializer_registry.auto_detect_tar_file_serializer(dataset)

        if serializer is None:
            print(
                f'Unable to find a serializer for data with type "{type(self)}". '
                f'Will abort saving...'
            )
        else:
            path = os.fspath(path)
            out_tar_gz_path = path if path.endswith('.tar.gz') else f'{path}.tar.gz'

            print(f'Writing data as a gzipped tarpack to "{os.path.abspath(out_tar_gz_path)}"')
            with open(out_tar_gz_path, 'wb') as out_tar_gz_file:
                out_tar_gz_file.write(serializer.serialize(parsed_dataset))

            directory = os.path.abspath(out_tar_gz_path[:-7])
            os.makedirs(directory, exist_ok=True)
            print(f'Extracting content to directory "{directory}"')
            with tarfile.open(out_tar_gz_path) as tar:
                tar.extractall(path=directory)
