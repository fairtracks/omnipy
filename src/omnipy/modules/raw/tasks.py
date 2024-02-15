from copy import deepcopy
from functools import reduce
from io import StringIO
from itertools import chain
from operator import add, ior
import os
from typing import TypeVar

from chardet import UniversalDetector

from omnipy.compute.task import TaskTemplate
from omnipy.compute.typing import mypy_fix_task_template
from omnipy.data.dataset import Dataset, Model

from .datasets import StrDataset
from .protocols import IsModifyAllLinesCallable, IsModifyContentsCallable, IsModifyEachLineCallable


@mypy_fix_task_template
@TaskTemplate(iterate_over_data_files=True, return_dataset_cls=StrDataset)
def decode_bytes(data: Model[bytes], encoding: str | None = None) -> str:
    if encoding is None:
        detector = UniversalDetector()
        for line in data.splitlines():
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

    return data.decode(encoding)


@mypy_fix_task_template
@TaskTemplate(iterate_over_data_files=True)
def modify_datafile_contents(
    data_file: Model[str],
    modify_contents_func: IsModifyContentsCallable,
    **kwargs: object,
) -> str:
    return modify_contents_func(str(data_file), **kwargs)


@mypy_fix_task_template
@TaskTemplate(iterate_over_data_files=True)
def modify_each_line(
    data_file: Model[str],
    modify_line_func: IsModifyEachLineCallable,
    **kwargs: object,
) -> str:
    output_data = StringIO()
    for i, line in enumerate(StringIO(str(data_file))):
        modified_line = modify_line_func(i, line, **kwargs)
        if modified_line is not None:
            output_data.write(modified_line)
    return output_data.getvalue()


@mypy_fix_task_template
@TaskTemplate(iterate_over_data_files=True)
def modify_all_lines(
    data_file: Model[str],
    modify_all_lines_func: IsModifyAllLinesCallable,
    **kwargs: object,
) -> str:
    all_lines = [line.strip() for line in StringIO(str(data_file))]
    modified_lines = modify_all_lines_func(all_lines, **kwargs)
    return os.linesep.join(modified_lines)


_ModelT = TypeVar('_ModelT', bound=Model)


@mypy_fix_task_template
@TaskTemplate()
def concat_all(dataset: Dataset[_ModelT]) -> _ModelT:
    return reduce(add, (val for val in dataset.values()))


@mypy_fix_task_template
@TaskTemplate()
def union_all(dataset: Dataset[_ModelT]) -> _ModelT:
    all_vals = tuple(val for val in dataset.values())
    assert len(all_vals) > 0
    first_val = deepcopy(all_vals[0])

    return reduce(ior, chain((first_val,), all_vals[1:]))
