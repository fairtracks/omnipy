from io import StringIO
import os
from types import NoneType
from typing import Callable, List, Union

from unifair.compute.task import TaskTemplate
from unifair.data.dataset import Dataset
from unifair.data.model import Model


@TaskTemplate
def modify_datafile_contents(
    dataset: Dataset[Model[str]],
    modify_contents_func: Callable[[str], str],
    **kwargs: object,
) -> Dataset[Model[str]]:
    out_dataset = Dataset[Model[str]]()
    for name, datafile in dataset.items():
        out_dataset[name] = modify_contents_func(datafile, **kwargs)
    return out_dataset


@TaskTemplate
def modify_each_line(
    dataset: Dataset[Model[str]],
    modify_line_func: Callable[[int, str], Union[NoneType, str]],
    **kwargs: object,
) -> Dataset[Model[str]]:
    out_dataset = Dataset[Model[str]]()
    for name, datafile in dataset.items():
        output_data = StringIO()
        for i, line in enumerate(StringIO(datafile)):
            modified_line = modify_line_func(i, line, **kwargs)
            if modified_line is not None:
                output_data.write(modified_line)
        out_dataset[name] = output_data.getvalue()
    return out_dataset


@TaskTemplate
def modify_all_lines(
    dataset: Dataset[Model[str]],
    modify_all_lines_func: Callable[[int, List[str]], List[str]],
    **kwargs: object,
) -> Dataset[Model[str]]:
    out_dataset = Dataset[Model[str]]()
    for name, datafile in dataset.items():
        all_lines = [line.strip() for line in StringIO(datafile)]
        modified_lines = modify_all_lines_func(all_lines, **kwargs)
        out_dataset[name] = os.linesep.join(modified_lines)
    return out_dataset
