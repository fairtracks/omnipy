"""Saving entry point shared by Models and Datasets."""

import os
import tarfile
from typing import cast


class SaveMixin:
    """Save contents as a gzipped tar archive, using the registered serializers."""

    def save(self, path: str | os.PathLike[str]) -> None:
        """Save a ``.tar.gz`` archive and extract a directory copy beside it.

        Datasets save each entry as a separate file. Models wrapping a Dataset (e.g.
        ``Model[JsonDataset]``) save the wrapped Dataset in the same way. Other Models save their
        complete contents as a single file, named after the Model class (e.g.
        ``__model_list_int__.json`` for ``Model[list[int]]``), which ``load()`` reads back as a
        single value. The serializer supplies the file suffix.

        Args:
            path: Destination path with or without the ``.tar.gz`` suffix.
        """
        from omnipy.data.dataset import Dataset, is_dataset_instance
        from omnipy.data.helpers import get_single_value_key, get_wrapped_dataset
        from omnipy.data.model import Model

        if is_dataset_instance(self):
            dataset = self
        else:
            model = cast(Model, self)
            wrapped_dataset = get_wrapped_dataset(model)
            if wrapped_dataset is not None:
                dataset = wrapped_dataset
            else:
                model_cls = type(model)
                dataset = Dataset[model_cls]({get_single_value_key(model_cls): model})  # type: ignore[valid-type]

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
