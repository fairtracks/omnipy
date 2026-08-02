"""General tasks for splitting, importing, and creating datasets and models."""
from _operator import iadd, ior
from collections.abc import Callable, Iterable, Iterator
from copy import deepcopy
from functools import reduce
from io import IOBase
from itertools import chain
import os
from pathlib import Path
from typing import Any, cast

from typing_extensions import TypeVar

from omnipy.compute.task import TaskTemplate
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.shared.protocols.data import IsDataset

from .protocols import SupportsIAdd, SupportsIOr

_T = TypeVar('_T')
_DatasetT = TypeVar('_DatasetT', bound=IsDataset)
_ModelT = TypeVar('_ModelT', bound=Model)
_SupportsIAddT = TypeVar('_SupportsIAddT', bound=SupportsIAdd)
_SupportsIOrT = TypeVar('_SupportsIOrT', bound=SupportsIOr)

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
def create_dataset_from_args(*args: object,
                             dataset_cls: type[_DatasetT],
                             key: str | None = None,
                             keys: tuple[str, ...] | None = None) -> _DatasetT:
    """Create a dataset from one or more positional payload objects.

    With no positional inputs, an empty dataset is created. A single
    positional input is forwarded as a single argument. Multiple
    positional inputs are packed into the tuple normally represented by
    ``*args`` before Dataset construction, allowing for key-value pairs to
    be passed as positional arguments. Alternatively, the ``key`` or
    ``keys`` keyword parameters can be used to specify the keys for the
    datasets.

    Args:
        *args: Positional payload passed to the dataset constructor.
        dataset_cls: Dataset class to instantiate.
        key: Optional single key (as string) for a single dataset entry.
        keys: Optional keys (as tuple of strings) to use for the dataset
            entries. Must be of the same length as ``args``. Only one of
            ``key`` or ``keys`` can be provided at a time.

    Returns:
        A dataset instance of type ``dataset_cls``.
    """
    assert (key is None or keys is None), \
        'Only one of `key` or `keys` can be provided at a time.'
    if key is not None:
        keys = (key,)

    if len(args) == 0:
        assert keys is None, ('No positional arguments were provided, but '
                              f'keys were provided: {keys}')
        return dataset_cls()

    if keys is not None:
        assert len(keys) == len(args), ('Number of keys must match number '
                                        'of positional arguments: '
                                        f'{len(keys)} != {len(args)}')
        return dataset_cls(dict(zip(keys, args)))
    else:
        if len(args) == 1:
            return dataset_cls(args[0])  # type: ignore[arg-type]
        return dataset_cls(args)  # type: ignore[arg-type]


@TaskTemplate()
def create_dataset_from_kwargs(*, dataset_cls: type[_DatasetT], **data: object) -> _DatasetT:
    """Create a dataset from named model or sub-dataset inputs.

    Args:
        dataset_cls: Dataset class to instantiate.
        **data: Named dataset entries forwarded as keyword arguments to ``dataset_cls``.

    Returns:
        A dataset instance of type ``dataset_cls``.
    """
    return dataset_cls(**data)  # type: ignore[arg-type]


@TaskTemplate()
def create_model_from_args(*args: object, model_cls: type[_ModelT]) -> _ModelT:
    """Create a model from positional inputs.

    A single positional input is forwarded unchanged. Multiple positional inputs are packed into the
    tuple normally represented by ``*args`` before model construction.

    Args:
        *args: Positional payload values to turn into the model root value.
        model_cls: Model class to instantiate.

    Returns:
        A model instance of type ``model_cls``.
    """
    if len(args) == 0:
        return model_cls()  # type: ignore[call-arg]
    if len(args) == 1:
        return model_cls(args[0])  # type: ignore[arg-type]
    return model_cls(args)  # type: ignore[arg-type]


@TaskTemplate()
def create_model_from_kwargs(*, model_cls: type[_ModelT], **data: object) -> _ModelT:
    """Create a model from named keyword inputs.

    Args:
        model_cls: Model class to instantiate.
        **data: Named values forwarded as keyword arguments to ``model_cls``.

    Returns:
        A model instance of type ``model_cls``.
    """
    return model_cls(**data)  # type: ignore[arg-type]


def _extract_first_and_other_datasets(
        datasets: dict[str, _DatasetT]) -> tuple[_DatasetT, tuple[_DatasetT, ...]]:
    first_dataset, *other_datasets = datasets.values()
    return first_dataset, tuple(other_datasets)


def _iter_dataset_values(datasets: Iterable[Dataset[_ModelT]]) -> Iterator[_ModelT]:
    for dataset in datasets:
        yield from dataset.values()


def _common_reduce(
    operator: Callable,
    first_vals: tuple[_T, ...],
    other_vals: Iterable[object],
) -> _T:
    assert len(first_vals) > 0
    first_val = deepcopy(first_vals[0])
    return cast(_T, reduce(operator, chain((first_val,), first_vals[1:], other_vals)))


def _concat_dataset_values(
    first_dataset: Dataset[Model[_SupportsIAddT]],
    *other_datasets: Dataset[Model[Any]],
) -> Model[_SupportsIAddT]:
    return _common_reduce(
        iadd,
        tuple(_iter_dataset_values((first_dataset,))),
        _iter_dataset_values(other_datasets),
    )


def _union_dataset_values(
    first_dataset: Dataset[Model[_SupportsIOrT]],
    *other_datasets: Dataset[Model[Any]],
) -> Model[_SupportsIOrT]:
    return _common_reduce(
        ior,
        tuple(_iter_dataset_values((first_dataset,))),
        _iter_dataset_values(other_datasets),
    )


def _union_datasets(
    first_dataset: _DatasetT,
    *other_datasets: _DatasetT | Dataset[Model[Any]],
) -> _DatasetT:
    return _common_reduce(ior, (first_dataset,), other_datasets)


@TaskTemplate()
def concat_all_vals_in_datasets_as_args(
    first_dataset: Dataset[Model[_SupportsIAddT]],
    *other_datasets: Dataset[Model[Any]],
) -> Model[_SupportsIAddT]:
    # %% Original docstring (managed by expand_docstr_macros.py) %%
    # Concatenate all value from positional datasets.
    #
    # {{CONCAT_DESCRIPTION}}
    #
    """Concatenate all value from positional datasets.

    Concatenation is based on a deep copy of the first value, with
    consecutive concatenations through the `+=` operator.
    """

    return _concat_dataset_values(first_dataset, *other_datasets)


@TaskTemplate()
def concat_all_vals_in_datasets_as_kwargs(**datasets: Dataset[Model[_SupportsIAddT]],
                                          ) -> Model[_SupportsIAddT]:
    # %% Original docstring (managed by expand_docstr_macros.py) %%
    # Concatenate all values from keyword datasets.
    #
    # {{CONCAT_DESCRIPTION}}
    #
    """Concatenate all values from keyword datasets.

    Concatenation is based on a deep copy of the first value, with
    consecutive concatenations through the `+=` operator.
    """

    first_dataset, other_datasets = _extract_first_and_other_datasets(datasets)
    return _concat_dataset_values(first_dataset, *other_datasets)


@TaskTemplate()
def union_all_vals_in_datasets_as_args(
    first_dataset: Dataset[Model[_SupportsIOrT]],
    *other_datasets: Dataset[Model[Any]],
) -> Model[_SupportsIOrT]:
    # %% Original docstring (managed by expand_docstr_macros.py) %%
    # Union all dataset values from positional datasets.
    #
    # {{UNION_DESCRIPTION_VALUE}}
    #
    """Union all dataset values from positional datasets.

    Union is based on a deep copy of the first value, with consecutive
    unions through the `|=` operator.
    """

    return _union_dataset_values(first_dataset, *other_datasets)


@TaskTemplate()
def union_all_vals_in_datasets_as_kwargs(**datasets: Dataset[Model[_SupportsIOrT]],
                                         ) -> Model[_SupportsIOrT]:
    # %% Original docstring (managed by expand_docstr_macros.py) %%
    # Union all dataset values from keyword datasets.
    #
    # {{UNION_DESCRIPTION_VALUE}}
    #
    """Union all dataset values from keyword datasets.

    Union is based on a deep copy of the first value, with consecutive
    unions through the `|=` operator.
    """

    first_dataset, other_datasets = _extract_first_and_other_datasets(datasets)
    return _union_dataset_values(first_dataset, *other_datasets)


@TaskTemplate()
def union_all_datasets_as_args(
    first_dataset: _DatasetT,
    *other_datasets: Dataset[Model[Any]],
) -> _DatasetT:
    # %% Original docstring (managed by expand_docstr_macros.py) %%
    # Union all positional datasets.
    #
    # {{UNION_DESCRIPTION_DATASET}}
    #
    """Union all positional datasets.

    Union is based on a deep copy of the first dataset, with consecutive
    unions through the `|=` operator.
    """

    return _union_datasets(first_dataset, *other_datasets)


@TaskTemplate()
def union_all_datasets_as_kwargs(**datasets: _DatasetT) -> _DatasetT:
    # %% Original docstring (managed by expand_docstr_macros.py) %%
    # Union all keyword datasets.
    #
    # {{UNION_DESCRIPTION_DATASET}}
    """Union all keyword datasets.

    Union is based on a deep copy of the first dataset, with consecutive
    unions through the `|=` operator."""

    first_dataset, other_datasets = _extract_first_and_other_datasets(datasets)
    return _union_datasets(first_dataset, *other_datasets)
