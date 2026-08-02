"""Tasks for decoding, editing, concatenating, and unioning raw datasets."""

from collections.abc import Callable
from copy import deepcopy
from functools import reduce
from io import StringIO
from itertools import chain
from operator import iadd, ior
import os
from textwrap import dedent
from typing import Any, cast, Iterable, Iterator

from chardet import UniversalDetector
from typing_extensions import TypeVar

from omnipy.compute.task import TaskTemplate
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model

from ...util.helpers import is_package_editable
from .datasets import StrDataset
from .protocols import (IsModifyAllLinesCallable,
                        IsModifyContentCallable,
                        IsModifyEachLineCallable,
                        SupportsIAdd,
                        SupportsIOr)

if is_package_editable('omnipy'):
    os.environ['OMNIPY_MACRO_CONCAT_DESCRIPTION'] = dedent("""\
        Concatenation is based on a deep copy of the first value, with
        consecutive concatenations through the `+=` operator.""")
    UNION_DESC_COMMON = dedent("""\
        Union is based on a deep copy of the first {obj}, with consecutive
        unions through the `|=` operator.""")
    os.environ['OMNIPY_MACRO_UNION_DESCRIPTION_VALUE'] = UNION_DESC_COMMON.format(obj='value')
    os.environ['OMNIPY_MACRO_UNION_DESCRIPTION_DATASET'] = UNION_DESC_COMMON.format(obj='dataset')

_T = TypeVar('_T')
_DatasetT = TypeVar('_DatasetT', bound=Dataset)
_ModelT = TypeVar('_ModelT', bound=Model)
_SupportsIAddT = TypeVar('_SupportsIAddT', bound=SupportsIAdd)
_SupportsIOrT = TypeVar('_SupportsIOrT', bound=SupportsIOr)


@TaskTemplate(iterate_over_data_files=True, output_dataset_cls=StrDataset)
def decode_bytes(data: Model[bytes], encoding: str | None = None) -> str:
    """Decode each binary data file to text, auto-detecting encoding when none is supplied."""

    if encoding is None:
        detector = UniversalDetector()
        for line in data.splitlines():  # type: ignore[attr-defined]
            detector.feed(line)
            if detector.done:
                break
        detector.close()
        result = detector.result

        encoding = result['encoding']
        confidence = result['confidence']
        language = result['language']

        # TODO: Implement simple solution to log from a task/flow.
        # TODO: Implement solution to add information to the dataset metadata and apply this to
        #       decode_bytes() for storing detected encoding etc.
        print(f'Automatically detected text encoding to be "{encoding}" with confidence '
              f'"{confidence}". The language is predicted to be "{language}". '
              f'(All predictions have been made by the "chardet" library.)')

        if encoding is None:
            encoding = 'ascii'

    return data.decode(encoding)  # type: ignore[attr-defined]


@TaskTemplate(iterate_over_data_files=True)
def modify_datafile_content(
    data_file: Model[str],
    modify_content_func: IsModifyContentCallable,
    **kwargs: object,
) -> str:
    """Apply a callable to each full text data file."""

    return modify_content_func(str(data_file), **kwargs)


@TaskTemplate(iterate_over_data_files=True)
def modify_each_line(
    data_file: Model[str],
    modify_line_func: IsModifyEachLineCallable,
    **kwargs: object,
) -> str:
    """Apply a callable to each line and rebuild the text from returned lines."""

    output_data = StringIO()
    for i, line in enumerate(StringIO(str(data_file))):
        modified_line = modify_line_func(i, line, **kwargs)
        if modified_line is not None:
            output_data.write(modified_line)
    return output_data.getvalue()


@TaskTemplate(iterate_over_data_files=True)
def modify_all_lines(
    data_file: Model[str],
    modify_all_lines_func: IsModifyAllLinesCallable,
    **kwargs: object,
) -> str:
    """Apply a callable to stripped lines and join the result with OS-specific newlines."""

    all_lines = [line.strip() for line in StringIO(str(data_file))]
    modified_lines = modify_all_lines_func(all_lines, **kwargs)
    return os.linesep.join(modified_lines)


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
    *other_datasets: Dataset[Model[Any]],
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
