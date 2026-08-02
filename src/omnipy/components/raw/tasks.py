"""Tasks for decoding, editing, concatenating, and unioning raw datasets."""

from io import StringIO
import os
from textwrap import dedent

from chardet import UniversalDetector

from omnipy.compute.task import TaskTemplate
from omnipy.data.model import Model

from ...util.helpers import is_package_editable
from .datasets import StrDataset
from .protocols import IsModifyAllLinesCallable, IsModifyContentCallable, IsModifyEachLineCallable

if is_package_editable('omnipy'):
    os.environ['OMNIPY_MACRO_CONCAT_DESCRIPTION'] = dedent("""\
        Concatenation is based on a deep copy of the first value, with
        consecutive concatenations through the `+=` operator.""")
    UNION_DESC_COMMON = dedent("""\
        Union is based on a deep copy of the first {obj}, with consecutive
        unions through the `|=` operator.""")
    os.environ['OMNIPY_MACRO_UNION_DESCRIPTION_VALUE'] = UNION_DESC_COMMON.format(obj='value')
    os.environ['OMNIPY_MACRO_UNION_DESCRIPTION_DATASET'] = UNION_DESC_COMMON.format(obj='dataset')


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
