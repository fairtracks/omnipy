"""General tasks for splitting, importing, and converting datasets."""

from io import IOBase
import os
from pathlib import Path
from typing import Callable

from typing_extensions import TypeVar

from omnipy.compute.task import TaskTemplate
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.shared.protocols.data import IsDataset

_DatasetT = TypeVar('_DatasetT', bound=IsDataset)
# @TaskTemplate()
# def cast_dataset(dataset: Dataset, cast_model: Callable[[], _ModelT]) -> _ModelT:
#     out_dataset: Dataset[_ModelT] = Dataset[cast_model]()
#     for name, item in dataset.items():
#         out_dataset[name] = cast(cast_model, item.to_data())
#     return out_dataset


@TaskTemplate()
def split_dataset(
        dataset: Dataset[Model[object]],
        datafile_names_for_b: list[str]) -> tuple[Dataset[Model[object]], Dataset[Model[object]]]:
    """Split a dataset into two datasets based on selected data-file names.

    Args:
        dataset: Dataset to split.
        datafile_names_for_b: Names that should be placed in the second output dataset.

    Returns:
        A tuple containing the remaining items first and the selected items second.
    """
    _type = dataset.get_type()
    datafile_names_for_a = set(dataset.keys()) - set(datafile_names_for_b)
    dataset_a = Dataset[_type](  # type: ignore[valid-type]
        {
            name: dataset[name] for name in dataset.keys() if name in datafile_names_for_a
        })
    dataset_b = Dataset[_type](  # type: ignore[valid-type]
        {
            name: dataset[name] for name in dataset.keys() if name in datafile_names_for_b
        })
    return dataset_a, dataset_b


@TaskTemplate()
def import_directory(
        directory: str | Path,
        exclude_prefixes: tuple[str, ...] = ('.', '_'),
        include_suffixes: tuple[str, ...] = (),
        dataset_cls: type[_DatasetT] = Dataset[Model[str]],  # type: ignore
        open_func: Callable[[str], IOBase] = open) -> _DatasetT:
    """Import files from a directory into a dataset keyed by filename stem.

    Args:
        directory: Directory to scan for files.
        exclude_prefixes: Filename prefixes to skip.
        include_suffixes: Optional filename suffixes to include.
        dataset_cls: Dataset type to instantiate for the imported content.
        open_func: Callable used to open each matching file.

    Returns:
        A dataset containing one item per imported file.
    """
    dataset = dataset_cls()
    for import_filename in os.listdir(directory):
        if not exclude_prefixes or \
                not any(import_filename.startswith(prefix) for prefix in exclude_prefixes):
            if not include_suffixes or \
                    any(import_filename.endswith(suffix) for suffix in include_suffixes):
                with open_func(os.path.join(directory, import_filename)) as open_file:
                    dataset_name = '_'.join(import_filename.split('.')[:-1])
                    print(f"{import_filename} -> Dataset['{dataset_name}']")
                    dataset[dataset_name] = open_file.read()
    return dataset


@TaskTemplate()
def convert_dataset(dataset: Dataset, dataset_cls: type[_DatasetT], **kwargs: object) -> _DatasetT:
    """Convert a dataset into another dataset class.

    Args:
        dataset: Source dataset to convert.
        dataset_cls: Target dataset class.
        **kwargs: Extra keyword arguments forwarded to ``dataset_cls``.

    Returns:
        A dataset instance of type ``dataset_cls``.
    """
    return dataset_cls(dataset, **kwargs)  # type: ignore[arg-type]
