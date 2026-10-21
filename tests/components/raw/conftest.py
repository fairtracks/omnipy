import os
from typing import Annotated

import pytest
import pytest_cases as pc

from omnipy.components.raw.enums import NewLine
from omnipy.data.model import Model

from ...helpers.protocols import AssertModelOrValFunc
from .helpers.protocols import AssertLineOfOsLinesepSplitCrlfTextFunc


@pytest.fixture(scope='function')
def hamlet_lines() -> list[str]:
    return [
        '        ',
        '        Alas, poor Yorick! I knew him, Horatio: a fellow',
        '        of infinite jest, of most excellent fancy: he hath',
        '        borne me on his back a thousand times; and now, how',
        '        abhorred in my imagination it is! my gorge rises at',
        '        it. Here hung those lips that I have kissed I know',
        '        not how oft. Where be your gibes now? your',
        '        gambols? your songs? your flashes of merriment,',
        '        that were wont to set the table on a roar? Not one',
        '        now, to mock your own grinning? quite chap-fallen.',
        '        ',
    ]


@pytest.fixture(scope='function')
def hamlet_lines_stripped(hamlet_lines: Annotated[list[str], pytest.fixture]) -> list[str]:
    return [line.strip() for line in hamlet_lines[1:-1]]


@pytest.fixture(scope='function')
def last_hamlet_lines_stripped(
    hamlet_lines_stripped: Annotated[list[str], pytest.fixture],
) -> list[str]:
    return hamlet_lines_stripped[3:]


@pytest.fixture(scope='function')
def hamlet_text_lf(hamlet_lines: Annotated[list[str], pytest.fixture]) -> str:
    return '\n'.join(hamlet_lines)


@pytest.fixture(scope='function')
def hamlet_text_crlf(hamlet_lines: Annotated[list[str], pytest.fixture]) -> str:
    return '\r\n'.join(hamlet_lines)


@pc.fixture(scope='function')
@pc.parametrize('use_str_model', [True, False], ids=['use_str_model=True', 'use_str_model=False'])
def hamlet_text_lf_as_model_or_plain(
    hamlet_text_lf: Annotated[str, pytest.fixture],
    use_str_model: bool,
) -> Model[str] | str:
    return Model[str](hamlet_text_lf) if use_str_model else hamlet_text_lf


@pc.fixture(scope='function')
@pc.parametrize('use_str_model', [True, False], ids=['use_str_model=True', 'use_str_model=False'])
def hamlet_text_crlf_as_model_or_plain(
    hamlet_text_crlf: Annotated[str, pytest.fixture],
    use_str_model: bool,
) -> Model[str] | str:
    return Model[str](hamlet_text_crlf) if use_str_model else hamlet_text_crlf


@pc.fixture(scope='function')
@pc.parametrize('use_str_model', [True, False], ids=['use_str_model=True', 'use_str_model=False'])
def text_with_mixed_newlines_as_model_or_plain(
    use_str_model: bool,
) -> Model[str] | str:
    raw_data = 'first \n second  \r\nthird\rfourth\n'
    return Model[str](raw_data) if use_str_model else raw_data


@pc.fixture(scope='function')
@pc.parametrize('use_str_model', [True, False], ids=['use_str_model=True', 'use_str_model=False'])
def first_text_with_comma_as_model_or_plain(use_str_model: bool) -> Model[str] | str:
    raw_data = 'abc, def ,ghi,jkl'
    return Model[str](raw_data) if use_str_model else raw_data


@pc.fixture(scope='function')
@pc.parametrize('use_str_model', [True, False], ids=['use_str_model=True', 'use_str_model=False'])
def second_text_with_comma_as_model_or_plain(use_str_model: bool) -> Model[str] | str:
    raw_data = 'mno, pqr ,stu,vwx,yz '
    return Model[str](raw_data) if use_str_model else raw_data


@pc.fixture(scope='function')
def first_text_with_tabs_as_model_or_plain(
    first_text_with_comma_as_model_or_plain: Annotated[Model[str] | str, pytest.fixture],
) -> Model[str] | str:
    return first_text_with_comma_as_model_or_plain.replace(',', '\t')  # type: ignore[union-attr]


@pc.fixture(scope='function')
def second_text_with_tabs_as_model_or_plain(
    second_text_with_comma_as_model_or_plain: Annotated[Model[str] | str, pytest.fixture],
) -> Model[str] | str:
    return second_text_with_comma_as_model_or_plain.replace(',', '\t')  # type: ignore[union-attr]


@pc.fixture(scope='function')
def dict_of_text_with_comma_as_model_or_plain(
    first_text_with_comma_as_model_or_plain: Annotated[Model[str] | str, pytest.fixture],
    second_text_with_comma_as_model_or_plain: Annotated[Model[str] | str, pytest.fixture],
) -> dict[str, Model[str] | str]:
    return {
        'start': first_text_with_comma_as_model_or_plain,
        'end': second_text_with_comma_as_model_or_plain,
    }


@pc.fixture(scope='function')
def dict_of_text_with_tabs_as_model_or_plain(
    first_text_with_tabs_as_model_or_plain: Annotated[Model[str] | str, pytest.fixture],
    second_text_with_tabs_as_model_or_plain: Annotated[Model[str] | str, pytest.fixture],
) -> dict[str, Model[str] | str]:
    return {
        'start': first_text_with_tabs_as_model_or_plain,
        'end': second_text_with_tabs_as_model_or_plain,
    }


@pc.fixture(scope='function')
def first_item_list() -> list[str]:
    return ['abc', 'def', 'ghi', 'jkl']


@pc.fixture(scope='function')
def second_item_list() -> list[str]:
    return ['mno', 'pqr', 'stu', 'vwx', 'yz']


@pc.fixture(scope='function')
def dict_of_item_lists(
    first_item_list: Annotated[list[str], pytest.fixture],
    second_item_list: Annotated[list[str], pytest.fixture],
) -> dict[str, list[str]]:
    return {
        'start': first_item_list,
        'end': second_item_list,
    }


@pc.fixture(scope='function')
@pc.parametrize('use_str_model', [True, False], ids=['use_str_model=True', 'use_str_model=False'])
def forward_list_of_texts_with_tabs(use_str_model: bool) -> list[Model[str]] | list[str]:
    raw_data_tab = ['abc\t def \tghi\t jkl', 'mno\t pqr\tstu\t vwx', 'yz']
    return [Model[str](line) for line in raw_data_tab] if use_str_model else raw_data_tab


@pc.fixture(scope='function')
@pc.parametrize('use_str_model', [True, False], ids=['use_str_model=True', 'use_str_model=False'])
def reverse_list_of_texts_with_tabs(use_str_model: bool) -> list[Model[str]] | list[str]:
    raw_data_tab = ['zyx\twvu\t tsr \t pqo', ' nml\t kji\thgf\t edc', 'ab ']
    return [Model[str](line) for line in raw_data_tab] if use_str_model else raw_data_tab


@pc.fixture(scope='function')
def forward_list_of_texts_with_comma(
    forward_list_of_texts_with_tabs: Annotated[
        list[Model[str]] | list[str],
        pytest.fixture,
    ],
) -> list[Model[str]] | list[str]:
    return [
        text.replace('\t', ',')  # type: ignore[union-attr]
        for text in forward_list_of_texts_with_tabs
    ]


@pc.fixture(scope='function')
def reverse_list_of_texts_with_comma(
    reverse_list_of_texts_with_tabs: Annotated[
        list[Model[str]] | list[str],
        pytest.fixture,
    ],
) -> list[Model[str]] | list[str]:
    return [
        text.replace('\t', ',')  # type: ignore[union-attr]
        for text in reverse_list_of_texts_with_tabs
    ]


@pc.fixture(scope='function')
def dict_of_lists_of_texts_with_tabs_as_model_or_plain(
    forward_list_of_texts_with_tabs: Annotated[list[Model[str]] | list[str], pytest.fixture],
    reverse_list_of_texts_with_tabs: Annotated[list[Model[str]] | list[str], pytest.fixture],
) -> dict[str, list[Model[str]] | list[str]]:
    return {
        'forward': forward_list_of_texts_with_tabs,
        'reverse': reverse_list_of_texts_with_tabs,
    }


@pc.fixture(scope='function')
def dict_of_lists_of_texts_with_comma_as_model_or_plain(
    forward_list_of_texts_with_comma: Annotated[list[Model[str]] | list[str], pytest.fixture],
    reverse_list_of_texts_with_comma: Annotated[list[Model[str]] | list[str], pytest.fixture],
) -> dict[str, list[Model[str]] | list[str]]:
    return {
        'forward': forward_list_of_texts_with_comma,
        'reverse': reverse_list_of_texts_with_comma,
    }


@pc.fixture(scope='function')
def forward_list_of_lists_of_items() -> list[list[str]]:
    return [['mno', 'pqr', 'stu', 'vwx'], ['yz']]


@pc.fixture(scope='function')
def reverse_list_of_lists_of_items() -> list[list[str]]:
    return [['nml', 'kji', 'hgf', 'edc'], ['ab']]


@pc.fixture(scope='function')
def dict_of_list_of_lists_of_items(
    forward_list_of_lists_of_items: Annotated[list[list[str]], pytest.fixture],
    reverse_list_of_lists_of_items: Annotated[list[list[str]], pytest.fixture],
) -> dict[str, list[list[str]]]:
    return {
        'forward': forward_list_of_lists_of_items,
        'reverse': reverse_list_of_lists_of_items,
    }


@pytest.fixture(scope='function')
def assert_line_of_os_linesep_split_crlf_text(
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> AssertLineOfOsLinesepSplitCrlfTextFunc:
    """Return an assertion helper for model or plain-value access."""

    def _assert_line_of_os_linesep_split_crlf_text(
        data: str,
        expected: str,
        with_newline: bool,
    ):
        match os.linesep:
            case NewLine.LF:
                expected = expected + NewLine.CR
            case NewLine.CR:
                expected = NewLine.LF + expected
            case _:
                ...

        if with_newline:
            expected = expected + os.linesep

        assert_model_if_dyn_conv_else_val(data, str, expected)

    return _assert_line_of_os_linesep_split_crlf_text
