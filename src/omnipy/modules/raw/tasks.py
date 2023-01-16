from io import StringIO
import os

from omnipy.compute.task import TaskTemplate
from omnipy.modules.raw.protocols import (IsModifyAllLinesCallable,
                                          IsModifyContentsCallable,
                                          IsModifyEachLineCallable)


@TaskTemplate(iterate_over_data_files=True)
def modify_datafile_contents(
    data_file: str,
    modify_contents_func: IsModifyContentsCallable,
    **kwargs: object,
) -> str:
    return modify_contents_func(data_file, **kwargs)


@TaskTemplate(iterate_over_data_files=True)
def modify_each_line(
    data_file: str,
    modify_line_func: IsModifyEachLineCallable,
    **kwargs: object,
) -> str:
    output_data = StringIO()
    for i, line in enumerate(StringIO(data_file)):
        modified_line = modify_line_func(i, line, **kwargs)
        if modified_line is not None:
            output_data.write(modified_line)
    return output_data.getvalue()


@TaskTemplate(iterate_over_data_files=True)
def modify_all_lines(
    data_file: str,
    modify_all_lines_func: IsModifyAllLinesCallable,
    **kwargs: object,
) -> str:
    all_lines = [line.strip() for line in StringIO(data_file)]
    modified_lines = modify_all_lines_func(all_lines, **kwargs)
    return os.linesep.join(modified_lines)
